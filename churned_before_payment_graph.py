import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os


def generate_churned_before_payment_graph(start_year, end_year):

    query_churned_before_payment = f'''

    SELECT "Fiscal Year", 
    "Total Pledges Starting", 
    "Pledges Churned Without Payment", 
    "Average Days Before Churn With No Payment", 
    "Pct Churned Without Payment"
    FROM public.oftw_churns_before_payments

    where "Fiscal Year" >= {start_year} and "Fiscal Year" <= {end_year}

    order by "Fiscal Year" asc

    '''

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Polars Dataframe From 
    polars_churn_before_payment = pl.read_database_uri(uri=postgres_uri, query=query_churned_before_payment, engine='adbc')

    max_pledges_polar = (polars_churn_before_payment.select(pl.col("Total Pledges Starting").max()).item()) * 1.2


    ## Sorting for Fiscal Year Discrete Category ##
    category_orders_fys = polars_churn_before_payment.select(pl.col("Fiscal Year")).rows(named=True)

    category_orders_fys = sorted([int(i['Fiscal Year']) for i in category_orders_fys])

    figure_churn_before_payment = px.bar(data_frame=polars_churn_before_payment, x="Fiscal Year", y=["Total Pledges Starting", "Pledges Churned Without Payment"],
                                        barmode='group', custom_data=["Pct Churned Without Payment", "Average Days Before Churn With No Payment"],
                                        color_discrete_map={"Total Pledges Starting": "rgb(11, 40, 56)", "Pledges Churned Without Payment": "rgb(98, 179, 224)"},
                                        text="value", )
    
    figure_churn_before_payment.update_yaxes(showgrid=True, zeroline=False, showline=False, showticklabels=True, tickwidth=2, gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    figure_churn_before_payment.update_layout(legend={
            'orientation':'h',
            'yanchor':"bottom",
            'y':1.02,
            'xanchor': 'center',
            'x': 0.5}, 
            legend_title_text = None,
            xaxis_title='Pledge Started Fiscal Year',
            yaxis_title="Number of Pledges",
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='closest',
            yaxis_range=[0, max_pledges_polar])
    
    figure_churn_before_payment.update_traces(textfont_size=10, marker={"cornerradius":5}, 
                                                        hovertemplate="""<b>FY%{x:.0d}</b><br><br>Number of Pledges: %{y:,.0d}<br>Pct Churned Without Payment: %{customdata[0]:.2%}<br>Average Days Before Churn With No Payment: %{customdata[1]:d} Days""",
                                                        textposition='outside',
                                                        texttemplate='''%{y:,.0d}''')
    

    figure_churn_before_payment.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')

    return figure_churn_before_payment

