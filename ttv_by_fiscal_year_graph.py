import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os

def generate_ttv_by_fiscal_year():

    posgtres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Query from postgresql Database ##
    query_ttv_by_fiscal_year = '''

    SELECT CONCAT('FY', cast("Fiscal Year" as varchar)) "Fiscal Year Named", 
    "Fiscal Year",
    "TTV Category", "Number of Pledges", "Total Pledges"
    FROM public.oftw_ttv_by_fiscal_year

    '''

    ## Polars Dataframe Setup ##
    polars_ttv_by_fiscal_year = pl.read_database_uri(posgtres_uri, query=query_ttv_by_fiscal_year, engine='adbc')


    ## Polars Additional Columns ##
    polars_ttv_by_fiscal_year = polars_ttv_by_fiscal_year.with_columns(((pl.col("Number of Pledges") / pl.col("Total Pledges")) * 1000.00).alias("Sign Ups Per 1000 Pledges"))

    max_polars_attr = polars_ttv_by_fiscal_year.select(pl.col("Number of Pledges").max()).item()

    cols_sorting = polars_ttv_by_fiscal_year.group_by('Fiscal Year Named').agg(pl.col('Fiscal Year')).avg()

    cols_sorting = cols_sorting.select(pl.col('Fiscal Year Named').sort_by(pl.col('Fiscal Year'))).to_series(0).to_list()

    ttv_category_sorting = [
        'Within 1 Week'
        ,'Within 1 Month'
        ,'Within 1 Year'
        ,'Over a Year'
    ]



    ## Figure Set Up ##
    ttv_by_fiscal_year_figure = px.bar(data_frame=polars_ttv_by_fiscal_year, x='Fiscal Year Named', y='Number of Pledges', color="TTV Category",
                                       category_orders={'Fiscal Year Named': cols_sorting, 'TTV Category': ttv_category_sorting})
    

    


