import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os

def generate_ttv_by_fiscal_year(start_year, end_year):

    posgtres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Query from postgresql Database ##
    query_ttv_by_fiscal_year = f'''

    SELECT CONCAT('FY', cast("Fiscal Year"::real as varchar)) "Fiscal Year Named", 
    "Fiscal Year"::real,
    "TTV Category", "Number of Pledges"::real, "Total Pledges"::real
    FROM public.oftw_ttv_by_fiscal_year

    where "Fiscal Year" >= {start_year} and "Fiscal Year" <= {end_year}

    '''

    ## Polars Dataframe Setup ##
    polars_ttv_by_fiscal_year = pl.read_database_uri(uri=posgtres_uri, query=query_ttv_by_fiscal_year, engine='adbc')


    ## Polars Additional Columns ##
    polars_ttv_by_fiscal_year = polars_ttv_by_fiscal_year.with_columns(((pl.col("Number of Pledges") / pl.col("Total Pledges")) * 100.00).alias("Sign Ups Per 100 Pledges"))

    max_polars_attr = polars_ttv_by_fiscal_year.select(pl.col("Number of Pledges").max()).item()

    cols_sorting = polars_ttv_by_fiscal_year.group_by('Fiscal Year Named').agg(pl.col('Fiscal Year')).mean()

    cols_sorting = cols_sorting.select(pl.col('Fiscal Year Named').sort_by(pl.col('Fiscal Year'))).to_series(0).to_list()

    ttv_category_sorting = [
        'Within 1 Week'
        ,'Within 1 Month'
        ,'Within 1 Year'
        ,'Over a Year'
    ]



    ## Figure Set Up ##
    ttv_by_fiscal_year_figure = px.bar(data_frame=polars_ttv_by_fiscal_year, x='Fiscal Year Named', y='Number of Pledges', color="TTV Category",
                                       category_orders={'Fiscal Year Named': cols_sorting, 'TTV Category': ttv_category_sorting},
                                       color_discrete_map={'Within 1 Week': '#0e4984', 'Within 1 Month': '#4281c0', 'Within 1 Year': '#71bdff', 'Over a Year': '#EBA747'},
                                       text='Number of Pledges', custom_data=["Sign Ups Per 100 Pledges"],
                                       barmode='stack')
    

    ttv_by_fiscal_year_figure.update_yaxes(showgrid=True, zeroline=False, showline=False, showticklabels=True, tickwidth=2, gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    ttv_by_fiscal_year_figure.update_layout(legend={
            'orientation':'h',
            'yanchor':"bottom",
            'y':1.02,
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 12}}, 
            legend_title = {'text': 'Time to Value (TTV)', 'font': {'weight': 'bold', 'size': 12}},
            xaxis_title={'text':"Fiscal Year", 'font': {'size': 12}},
            yaxis_title={'text':"Total Pledges Created", 'font': {'size': 12}},
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='x unified')
    

    ttv_by_fiscal_year_figure.update_traces(textfont_size=10, marker={"cornerradius":5}, 
                                                        hovertemplate="""<br><b>Pledges Signed Up: </b>%{y:,.0d}<br><b>Sign Ups Per 100 Pledges: </b>%{customdata[0]:,.1f}""",
                                                        textposition='inside',
                                                        texttemplate='''%{y:,.0d}''')
    

    ttv_by_fiscal_year_figure.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')


    return ttv_by_fiscal_year_figure
    

    


