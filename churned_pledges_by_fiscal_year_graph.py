import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os



def generate_churned_pledges_by_fiscal_year(minYear, maxYear):

    ## Query to pull churned pledges by fiscal year ##
    query_churned_pledges_by_fiscal_year = f'''
    
    with a as (
    select *,
    (("Active Pledges" + "Pre Churned Pledges") - ("Active Pledges" + "Pre Churned Pledges" - ("Churned Pledges" - "Added Pledges"))) / ("Active Pledges" + "Pre Churned Pledges") as "Calculated Churn Rate",
    ("Active Pledges" + "Pre Churned Pledges" - ("Churned Pledges" - "Added Pledges")) - ("Active Pledges" + "Pre Churned Pledges") as "Calculated Pledge Change",
    ("Active Pledges" + "Pre Churned Pledges") as "Active Pledges Start of Year",
    ("Active Pledges" + "Pre Churned Pledges" - ("Churned Pledges" - "Added Pledges")) as "Active Pledges End of Year"
    from 
    public.oftw_churn_rate_fy
    where "Fiscal Year" >= {str(minYear)} and "Fiscal Year" <= {str(maxYear)})

    select a.*,
    case 
    	when a."Calculated Pledge Change" < 0 then CONCAT('Lost ', cast(a."Calculated Pledge Change" * -1 as varchar), ' Pledges')
    	else CONCAT('Gained ', cast(a."Calculated Pledge Change" as varchar), ' Pledges')
    end as "Calculated Pledge Change Description",
    case
	    when a."Calculated Pledge Change" < 0 then 'Negative'
	    else 'Positive'
    end as "PosNeg"
    from a
    
    '''

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Polars dataframe from query ##
    polars_churned_pledges_by_fiscal_year = pl.read_database_uri(uri=postgres_uri, query=query_churned_pledges_by_fiscal_year, engine='adbc').sort(pl.col("Fiscal Year"), descending=False)

    max_pledges_polar = (polars_churned_pledges_by_fiscal_year.select(pl.col("Calculated Pledge Change").abs().max()).item()) * 1.2
    min_pledges_polar = (polars_churned_pledges_by_fiscal_year.select(pl.col("Calculated Pledge Change").min()).item()) * 1.2

    category_orders_fys = polars_churned_pledges_by_fiscal_year.select(pl.col("Fiscal Year")).rows(named=True)

    category_orders_fys = sorted([int(i['Fiscal Year']) for i in category_orders_fys])

    print(category_orders_fys)

    ## pledges_by_type_distinct_polars.group_by(pl.col("Fiscal Year")).agg(pl.col("Number of Pledge Sign Ups").sum()).select(pl.col("Number of Pledge Sign Ups").max()).item()

    ## No Legend as there will just be 2 colors ##
    figure_churned_pledges_by_fiscal_year = px.bar(data_frame=polars_churned_pledges_by_fiscal_year, 
                                                   x='Fiscal Year', 
                                                   y="Calculated Pledge Change", 
                                                   color="PosNeg",
                                                   color_discrete_map={'Positive':'#1AB2D7',
                                                                       'Negative':'#D54217'},
                                                   custom_data=["Calculated Churn Rate", "Active Pledges Start of Year", "Active Pledges End of Year", "Calculated Pledge Change Description"],
                                                   text="Calculated Pledge Change"
                                                   )
    
    figure_churned_pledges_by_fiscal_year.update_yaxes(showgrid=True, zeroline=True, zerolinewidth=2, zerolinecolor='#CDC6B8', 
                                                       showline=False, linecolor='black', showticklabels=True, tickwidth=2,
                                                       gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    figure_churned_pledges_by_fiscal_year.update_layout(
            xaxis_title="Fiscal Year",
            yaxis_title="Change in Active Pledges",
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='closest',
            yaxis_range=[min_pledges_polar, max_pledges_polar],
            showlegend=False)
    
    figure_churned_pledges_by_fiscal_year.update_traces(textfont_size=10, marker={"cornerradius":5}, 
                                                        hovertemplate="""<b>FY%{x:.d0}: %{customdata[3]} <br><br>Churn Rate: %{customdata[0]:.3%}</b><br>Active Pledges Start of FY: %{customdata[1]:,.0d}<br>Active Pledges End of FY: %{customdata[2]:,.0d}""",
                                                        textposition='outside')

    figure_churned_pledges_by_fiscal_year.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)', type='category')

    return figure_churned_pledges_by_fiscal_year
    


