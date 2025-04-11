import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os

def generate_money_moved_annual_graph(start_year, end_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Query to grab annual money moved data split by Frequency Type ##
    query_money_moved_annual = f'''

    with curr as (
    select *,
    case
    	when "CURRENCY SHORT" in ('GBP', 'AUD', 'EUR') then "CURRENCY RATE"
    	when "CURRENCY SHORT" in ('CAD', 'SGD', 'CHF') then (1.00 / "CURRENCY RATE")
    end as "CURRENCY RATE FINAL"
    from public.oftw_currency_conversion
    ),

    pledge_freq as (
    select distinct pledge_id, frequency from public.oftw_pledges_raw

    ),

    annual_info as (

    select 
    case
    	when DATE_PART('month', cast(opr."date" as date)) >= 7 then DATE_PART('year', cast(opr."date" as date)) + 1
    	else DATE_PART('year', cast(opr."date" as date))
    end as "Fiscal Year",

    case 
    	when pledge.frequency = 'One-Time' then 'One-Time'
    	else 'Subscription'
    end as "Payment Frequency",

    SUM(case
    	when opr.currency = 'USD' then opr.amount
    	else opr."amount" * curr."CURRENCY RATE FINAL"
    end) as "Payment Amount",

    count(*) "Number of Payments"

    from public.oftw_payments_raw opr 
    left join curr
    on cast(opr."date" as DATE) = cast(curr."DATE" as DATE) and opr.currency = curr."CURRENCY SHORT"

    left join pledge_freq pledge
    on opr.pledge_id = pledge.pledge_id 

    group by 1, 2)

    select "Fiscal Year",
    CONCAT('FY', cast("Fiscal Year" as varchar)) as "Fiscal Year Named",
    row_number() over (order by "Fiscal Year", "Payment Frequency") as "Fiscal Year Sorted",
    "Payment Frequency",
    "Payment Amount",
    "Number of Payments"
    from annual_info
    where "Fiscal Year" >= {start_year} and "Fiscal Year" <= {end_year}
    order by "Fiscal Year", "Payment Frequency"

    '''


    ## Polars Extraction of Query Above ##
    polars_money_moved_annual = pl.read_database_uri(uri=postgres_uri, engine='adbc', query=query_money_moved_annual)

    max_payment_polar = (polars_money_moved_annual.select(pl.col("Payment Amount").max()).item()) * 1.2

    cols_sorting = polars_money_moved_annual.group_by('Fiscal Year Named').agg(pl.col('Fiscal Year Sorted')).sum()

    cols_sorting = cols_sorting.select(pl.col('Fiscal Year Named').sort_by(pl.col('Fiscal Year Sorted'))).to_series(0).to_list()

    graph_money_moved_annual = px.bar(data_frame=polars_money_moved_annual, x="Fiscal Year Named", y="Payment Amount", color="Payment Frequency", barmode='stack',
                                      category_orders={'Fiscal Year Named': cols_sorting},
                                      color_discrete_map={'One-Time': '#71bdff', 'Subscription': '#0e4984'},
                                      text='Payment Amount', custom_data=["Number of Payments"])
    
    graph_money_moved_annual.update_yaxes(showgrid=True, zeroline=False, showline=False, showticklabels=True, tickwidth=2, gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    graph_money_moved_annual.update_layout(legend={
            'orientation':'h',
            'yanchor':"bottom",
            'y':1.02,
            'xanchor': 'center',
            'x': 0.5}, 
            legend_title_text = 'Payment Frequency',
            xaxis_title='Fiscal Year',
            yaxis_title="Total Amount Paid ($USD)",
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='closest')
    

    graph_money_moved_annual.update_traces(textfont_size=10, marker={"cornerradius":5}, 
                                                        hovertemplate="""Hello World""",
                                                        textposition='outside',
                                                        texttemplate='''%{y:,.0d}''')
    

    graph_money_moved_annual.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')

    return graph_money_moved_annual
    
