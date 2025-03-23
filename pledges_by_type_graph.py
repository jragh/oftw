import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os

def pledges_by_type_graph():

    posgtres_uri = os.getenv('POSTGRES_URI_LOCATION')

    query_pledges_by_type_distinct = f'''
    
    with pledge_info as (

        select pledge_id, 
        cast(pledge_created_at as date) "pledge_created_at", 

        case 
        	when date_part('month', cast(pledge_created_at as date)) >= 7 then date_part('year', cast(pledge_created_at as date)) + 1
        	else date_part('year', cast(pledge_created_at as date))
        end "fiscal_year",

        case
        	when date_part('month', cast(pledge_created_at as date)) in (7, 8, 9) then 1
        	when date_part('month', cast(pledge_created_at as date)) in (10, 11, 12) then 2
        	when date_part('month', cast(pledge_created_at as date)) in (1, 2, 3) then 3
        	when date_part('month', cast(pledge_created_at as date)) in (4, 5, 6) then 4
        end "fiscal_month",
        pledge_status,
        case 
        	when pledge_status = 'One-Time' then 'One-Time' else 'Subscription'
        end as "pledge_status_grouped"
        from public.oftw_pledges_raw
        where (pledge_created_at is not null and pledge_created_at != '')


        )

    select fiscal_year "Fiscal Year",
    pledge_status_grouped "Pledge Status Grouped",
    count(distinct pledge_id) "Number of Pledge Sign Ups"
    
    from pledge_info
    
    where fiscal_year >= 2014
    group by fiscal_year, pledge_status_grouped
    order by fiscal_year, pledge_status_grouped
    
    '''

    pledges_by_type_distinct_polars = pl.read_database_uri(uri=posgtres_uri, query=query_pledges_by_type_distinct, engine='adbc')

    max_pledges_polar = pledges_by_type_distinct_polars.group_by(pl.col("Fiscal Year")).agg(pl.col("Number of Pledge Sign Ups").sum()).select(pl.col("Number of Pledge Sign Ups").max()).item()

    ## max_pass_util_carrier_polar = (pass_util_carrier_polar.select(pl.col('TOTAL SEATS').max()).item()) * 1.10

    pledges_by_type_distinct_fig = px.bar(data_frame=pledges_by_type_distinct_polars, x="Fiscal Year", y="Number of Pledge Sign Ups", color="Pledge Status Grouped",
                                          barmode='stack', color_discrete_map={'One-Time': '#845ef7', 'Subscription': '#1971c2'},
                                          text_auto="0.,3s",
                                          category_orders={'Pledge Status Grouped': ['Subscription', 'One-Time']})
    
    pledges_by_type_distinct_fig.update_yaxes(showgrid=True, zeroline=False, showline=False, showticklabels=True, tickwidth=2, gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    pledges_by_type_distinct_fig.update_layout(legend={
            'orientation':'h',
            'yanchor':"bottom",
            'y':1.02,
            'xanchor': 'center',
            'x': 0.5}, 
            legend_title_text = '<b>Pledge Type</b>',
            xaxis_title=None,
            yaxis_title="Pledge Sign Ups",
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='closest',
            yaxis_range=[0, max_pledges_polar])
    
    pledges_by_type_distinct_fig.update_traces(textfont_size=10, marker={"cornerradius":5}, hovertemplate="""Testing Hover Template Currently""", textposition='inside')

    pledges_by_type_distinct_fig.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')

    return pledges_by_type_distinct_fig


