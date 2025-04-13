import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os

def pledges_by_type_graph():

    posgtres_uri = os.getenv('POSTGRES_URI_LOCATION')

    query_pledges_by_type_distinct = f'''
    
    SELECT "Fiscal Year", "Pledge Status Grouped", "Number of Pledge Sign Ups"
    FROM public.oftw_pledges_by_type_overall

    
    '''

    pledges_by_type_distinct_polars = pl.read_database_uri(uri=posgtres_uri, query=query_pledges_by_type_distinct, engine='adbc')

    max_pledges_polar = pledges_by_type_distinct_polars.group_by(pl.col("Fiscal Year")).agg(pl.col("Number of Pledge Sign Ups").sum()).select(pl.col("Number of Pledge Sign Ups").max()).item()

    ## max_pass_util_carrier_polar = (pass_util_carrier_polar.select(pl.col('TOTAL SEATS').max()).item()) * 1.10

    pledges_by_type_distinct_fig = px.bar(data_frame=pledges_by_type_distinct_polars, x="Fiscal Year", y="Number of Pledge Sign Ups", color="Pledge Status Grouped",
                                          barmode='stack', color_discrete_map={'One-Time': '#845ef7', 'Subscription': '#1971c2'},
                                          text_auto="0.,3s",
                                          category_orders={'Pledge Status Grouped': ['Subscription', 'One-Time']},
                                          custom_data=["Pledge Status Grouped"])
    
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
    
    pledges_by_type_distinct_fig.update_traces(textfont_size=10, marker={"cornerradius":5}, hovertemplate="""<b>FY%{x:.0d}: %{customdata[0]}</b><br><br><b>Number of Pledge Sign Ups: </b>%{y:,.0d}""", textposition='inside')

    pledges_by_type_distinct_fig.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')

    return pledges_by_type_distinct_fig


