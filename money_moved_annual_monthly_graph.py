import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os

def generate_money_moved_annual_graph(start_year, end_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Query to grab annual money moved data split by Frequency Type ##
    query_money_moved_annual = f'''

    SELECT "Fiscal Year", "Fiscal Year Named", "Fiscal Year Sorted", "Payment Frequency", "Payment Amount", "Number of Payments"
    FROM public.oftw_money_moved_annual
    where "Fiscal Year" >= {start_year} and "Fiscal Year" <= {end_year}
    order by "Fiscal Year", "Payment Frequency" 

    '''


    ## Polars Extraction of Query Above ##
    polars_money_moved_annual = pl.read_database_uri(uri=postgres_uri, engine='adbc', query=query_money_moved_annual)

    max_payment_polar = (polars_money_moved_annual.group_by('Fiscal Year Named').agg(pl.col("Payment Amount").sum()).select(pl.col("Payment Amount").max()).item()) * 1.2

    cols_sorting = polars_money_moved_annual.group_by('Fiscal Year Named').agg(pl.col('Fiscal Year Sorted')).sum()

    cols_sorting = cols_sorting.select(pl.col('Fiscal Year Named').sort_by(pl.col('Fiscal Year Sorted'))).to_series(0).to_list()

    graph_money_moved_annual = px.bar(data_frame=polars_money_moved_annual, x="Fiscal Year Named", y="Payment Amount", color="Payment Frequency", barmode='stack',
                                      category_orders={'Fiscal Year Named': cols_sorting, 'Payment Frequency': ['Subscription', 'One-Time']},
                                      color_discrete_map={'One-Time': '#71bdff', 'Subscription': '#0e4984'},
                                      text='Payment Amount', custom_data=["Number of Payments", "Payment Frequency"]
                                      )
    
    graph_money_moved_annual.update_yaxes(showgrid=True, zeroline=False, showline=False, showticklabels=True, tickwidth=2, gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    graph_money_moved_annual.update_layout(legend={
            'orientation':'h',
            'yanchor':"bottom",
            'y':1.02,
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 12}}, 
            legend_title = {'text': 'Payment Frequency', 'font': {'weight': 'bold', 'size': 12}},
            xaxis_title={'text':"Fiscal Year", 'font': {'size': 12}},
            yaxis_title={'text':"Total Amount Paid ($USD)", 'font': {'size': 12}},
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='closest',
            yaxis_range=[0,max_payment_polar])
    

    graph_money_moved_annual.update_traces(textfont_size=10, marker={"cornerradius":5}, 
                                                        hovertemplate="""<b>%{x}: %{customdata[1]}</b><br><br><b>Total Payment Amount Recieved: </b>$%{y:,.0d}<br><b>Total Payments Recieved: </b>%{customdata[0]:,.0d}""",
                                                        textposition='inside',
                                                        texttemplate='''$%{y:,.0d}''')
    

    graph_money_moved_annual.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')

    return graph_money_moved_annual



def generate_money_moved_monthly_graph(start_year, end_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    query_money_moved_monthly = f'''

    SELECT "Fiscal Year", "Fiscal Month", "Fiscal Year Named", "Fiscal Year Sorted", "Payment Frequency", "Payment Amount", "Number of Payments"
    FROM public.oftw_money_moved_monthly
    where "Fiscal Year" >= {start_year} and "Fiscal Year" <= {end_year}
    order by "Fiscal Year", "Fiscal Month", "Payment Frequency"

    '''

    ## Polars Dataframe Pull for Monthly Money Moved Query ##
    polars_money_moved_monthly = pl.read_database_uri(uri=postgres_uri, query=query_money_moved_monthly, engine='adbc')

    cols_sorting = polars_money_moved_monthly.group_by('Fiscal Year Named').agg(pl.col('Fiscal Year Sorted')).sum()

    cols_sorting = cols_sorting.select(pl.col("Fiscal Year Named").sort_by(pl.col("Fiscal Year Sorted"))).to_series(0).to_list()

    max_payment_polar = (polars_money_moved_monthly.group_by('Fiscal Year Named').agg(pl.col("Payment Amount").sum()).select(pl.col("Payment Amount").max()).item()) * 1.2

    ## Graph / Figure Return ##

    graph_money_moved_monthly = px.area(data_frame=polars_money_moved_monthly, x="Fiscal Year Named", y="Payment Amount", color="Payment Frequency",
                                        category_orders={'Fiscal Year Named': cols_sorting, 'Payment Frequency': ['Subscription', 'One-Time']},
                                        custom_data=["Number of Payments", "Payment Frequency"],
                                        color_discrete_map={'One-Time': '#71bdff', 'Subscription': '#0e4984'},
                                        markers=True
                                        )
    
    graph_money_moved_monthly.update_yaxes(showgrid=True, zeroline=False, showline=False, showticklabels=True, tickwidth=2, gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    graph_money_moved_monthly.update_layout(legend={
            'orientation':'h',
            'yanchor':"bottom",
            'y':1.02,
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 12}}, 
            legend_title = {'text': 'Payment Frequency', 'font': {'weight': 'bold', 'size': 12}},
            xaxis_title={'text':"Fiscal Year", 'font': {'size': 12}},
            yaxis_title={'text':"Total Amount Paid ($USD)", 'font': {'size': 12}},
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='x unified')
    
    graph_money_moved_monthly.update_traces(textfont_size=10,
                                                        hovertemplate="""<b>%{customdata[1]} Payment Amount Recieved: </b>$%{y:,.0d}<br><b>%{customdata[1]} Payments Recieved: </b>%{customdata[0]:,.0d}<extra></extra>""",
                                                        )
    
    graph_money_moved_monthly.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')

    return graph_money_moved_monthly



def generate_arpp_annual_graph(start_year, end_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Query to pull annual ARPP calculation split by payment frequency ##
    query_arpp_annual_graph = f'''

    SELECT "Fiscal Year", "Fiscal Year Named", "Fiscal Year Sorted", "Payment Frequency", "Total Payment Amount", "Number of Paying Pledges"
    FROM public.oftw_aprr_annual

    where "Fiscal Year" >= {start_year} and "Fiscal Year" <= {end_year}

    order by "Fiscal Year", "Payment Frequency"

    '''

    ## Polars Dataframe from the Query ##
    ## Calculate ARPP ##
    ## Find Max Value ARPP ##
    polars_arpp_annual_graph = pl.read_database_uri(query=query_arpp_annual_graph, uri=postgres_uri, engine='adbc')

    polars_arpp_annual_graph = polars_arpp_annual_graph.with_columns((pl.col("Total Payment Amount") / pl.col("Number of Paying Pledges")).alias("Average Revenue Per Pledge"))

    polars_arpp_max = (polars_arpp_annual_graph.select(pl.col("Average Revenue Per Pledge").max()).item()) * 1.2

    cols_sorting = polars_arpp_annual_graph.group_by('Fiscal Year Named').agg(pl.col('Fiscal Year Sorted')).sum()
    
    cols_sorting = cols_sorting.select(pl.col("Fiscal Year Named").sort_by(pl.col("Fiscal Year Sorted"))).to_series(0).to_list()


    ## Graph / Figure Return ##

    graph_arpp_annual = px.bar(data_frame=polars_arpp_annual_graph, x="Fiscal Year Named", y="Average Revenue Per Pledge", color="Payment Frequency", barmode='group',
                               category_orders={'Fiscal Year Named': cols_sorting, 'Payment Frequency': ['Subscription', 'One-Time']},
                               color_discrete_map={'One-Time': '#71bdff', 'Subscription': '#0e4984'},
                               text='Average Revenue Per Pledge', custom_data=["Number of Paying Pledges", "Payment Frequency", "Total Payment Amount"]
                               )
    
    graph_arpp_annual.update_yaxes(showgrid=True, zeroline=False, showline=False, showticklabels=True, tickwidth=2, gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    graph_arpp_annual.update_layout(legend={
            'orientation':'h',
            'yanchor':"bottom",
            'y':1.02,
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 12}}, 
            legend_title = {'text': 'Payment Frequency', 'font': {'weight': 'bold', 'size': 12}},
            xaxis_title={'text':"Fiscal Year", 'font': {'size': 12}},
            yaxis_title={'text':"Average Revenue Per Pledge ($USD)", 'font': {'size': 12}},
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='closest',
            yaxis_range=[0,polars_arpp_max])
    
    graph_arpp_annual.update_traces(textfont_size=10, marker={"cornerradius":5}, 
                                                        hovertemplate="""Hello World""",
                                                        textposition='inside',
                                                        texttemplate='''$%{y:,.2d}''')
    
    graph_arpp_annual.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')

    return graph_arpp_annual



def generate_arpp_monthly_graph(start_year, end_year, payment_platforms):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Query for Monthly APRR Pull ##
    query_arpp_monthly_graph = f'''

    SELECT "Fiscal Year", "Fiscal Month", "Fiscal Year Named", "Fiscal Year Sorted", "Payment Platform", "Total Payment Amount", "Number of Paying Pledges"
    FROM public.oftw_aprr_monthly

    where "Fiscal Year" >= {start_year} and "Fiscal Year" <= {end_year}

    order by "Fiscal Year", "Fiscal Month", "Payment Platform"

    '''


    ## Polars Pull and Transformations ##
    polars_arpp_monthly_graph_raw = pl.read_database_uri(uri=postgres_uri, query=query_arpp_monthly_graph, engine='adbc')

    if (payment_platforms is None and payment_platforms.strip() == '') or (payment_platforms == []):

        payment_platforms = ['Donational'
            ,'Benevity'
            ,'Squarespace'
            ,'NFG'
            ,'Off Platform'
            ,'Gift Aid'
        ]

    ## Overall Listing of Payment Platforms sorted by number of Pledges ##
    payment_platform_listing = polars_arpp_monthly_graph_raw.group_by(pl.col('Payment Platform')).agg(pl.col('Number of Paying Pledges').sort_by(pl.col('Payment Platform')).sum())

    payment_platform_listing = payment_platform_listing.select(pl.col('Payment Platform').sort_by(pl.col('Number of Paying Pledges'), descending=True)).get_column('Payment Platform').to_list()

    ## Filtering Based on Selected Payment Platforms ##
    polars_arpp_monthly_graph_raw = polars_arpp_monthly_graph_raw.filter(pl.col('Payment Platform').is_in(payment_platform_listing) & pl.col('Payment Platform').is_in(payment_platforms))

    ## Gropup by to sum the values before setting up final column ##
    polars_arpp_monthly_grouped = polars_arpp_monthly_graph_raw.group_by([ "Fiscal Year", "Fiscal Month", "Fiscal Year Named"]).agg([pl.col("Fiscal Year Sorted").max(), pl.col('Total Payment Amount').sum(), pl.col('Number of Paying Pledges').sum()])

    polars_arpp_monthly_grouped = polars_arpp_monthly_grouped.with_columns((pl.col("Total Payment Amount") / pl.col("Number of Paying Pledges")).alias("Average Revenue Per Pledge"))

    polars_arpp_max = (polars_arpp_monthly_grouped.select(pl.col("Average Revenue Per Pledge").max()).item()) * 1.2

    print(polars_arpp_monthly_grouped.head(25))

    cols_sorting = polars_arpp_monthly_grouped.group_by('Fiscal Year Named').agg(pl.col('Fiscal Year Sorted').sum())
    
    cols_sorting = cols_sorting.select(pl.col("Fiscal Year Named").sort_by(pl.col("Fiscal Year Sorted"))).to_series(0).to_list()

    print(cols_sorting)


    # Graph / Figure Return #
    graph_arpp_monthly = px.bar(data_frame=polars_arpp_monthly_grouped, x="Fiscal Year Named", y="Average Revenue Per Pledge",
                                category_orders={'Fiscal Year Named': cols_sorting},
                                text='Average Revenue Per Pledge', custom_data=["Number of Paying Pledges", "Total Payment Amount"]
                                )
    
    graph_arpp_monthly.update_yaxes(showgrid=True, zeroline=False, showline=False, showticklabels=True, tickwidth=2, gridcolor="rgba(30, 63, 102, 0.15)", type="-")

    graph_arpp_monthly.update_layout( 
            xaxis_title={'text':"Fiscal Year", 'font': {'size': 11}},
            yaxis_title={'text':"Average Revenue Per Pledge ($USD)", 'font': {'size': 11}},
            yaxis_tickfont={'size': 10},
            xaxis_tickfont={'size': 10},
            margin={'l':10, 'r': 10, 't': 10, 'b': 10},
            plot_bgcolor='#fff', paper_bgcolor="#fff",
            hovermode='closest',
            ## yaxis_range=[0,polars_arpp_max],
            showlegend=False)
    
    graph_arpp_monthly.update_traces(textfont_size=10, marker={"cornerradius":5, 'color':"#1971c2"}, 
                                                        hovertemplate="""Hello World""",
                                                        textposition='inside',
                                                        texttemplate='''$%{y:,.2d}''')
    
    graph_arpp_monthly.update_xaxes(linewidth=2.5, showgrid=False, linecolor='rgb(180, 180, 180)')

    return graph_arpp_monthly
    
