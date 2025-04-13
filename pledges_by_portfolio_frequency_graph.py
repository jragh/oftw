import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os

def pledges_by_portfolio_frequency_true(beginning_year, end_year, selected_portfolios:list):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Create the Query with between filter, use the calendar from DMC to provide the filtering changes ##
    query_pledges_by_portfolio_frequency = f'''

    SELECT portfolio, frequency, "Ordering", SUM(pledge_sign_ups::real) pledge_sign_ups 
    FROM public.oftw_pledges_by_portfolio_frequency
    where fiscal_year >= {str(beginning_year)} and fiscal_year <= {str(end_year)}
    group by portfolio, frequency, "Ordering"
    order by "Ordering", frequency

    
    '''

    polars_pledges_by_portfolio_frequency = pl.read_database_uri(uri=postgres_uri, query=query_pledges_by_portfolio_frequency, engine='adbc')

    ## List for ordering the portfolios
    portfolio_listing = polars_pledges_by_portfolio_frequency.group_by(pl.col('portfolio'), pl.col('Ordering')).agg(pl.col('pledge_sign_ups').sort_by(pl.col('portfolio')).sum())

    portfolio_listing = portfolio_listing.select(pl.col('portfolio').sort_by(pl.col('Ordering'))).get_column('portfolio').to_list()

    ## Filtered pledges by portfolio
    ## Will need to add parameter inside function call for callback ##
    
    if (selected_portfolios is None and selected_portfolios.strip() == '') or (selected_portfolios == []):

        selected_portfolios = ['OFTW Top Picks'
                ,'Entire OFTW Portfolio'
                ,'Custom Portfolio'
                ,'OFTW Top Pick: Against Malaria Foundation'
                ,'GiveWell (Maximum Impact Fund)']
        
        polars_pledges_by_portfolio_frequency = polars_pledges_by_portfolio_frequency.filter(pl.col('portfolio').is_in(portfolio_listing) & pl.col('portfolio').is_in(selected_portfolios))

    else:

        polars_pledges_by_portfolio_frequency = polars_pledges_by_portfolio_frequency.filter(pl.col('portfolio').is_in(portfolio_listing) & pl.col('portfolio').is_in(selected_portfolios))

    graph_pledges_by_portfolio_frequency = px.bar(data_frame=polars_pledges_by_portfolio_frequency, y='portfolio', x='pledge_sign_ups', color='frequency',
                                                  orientation='h', barmode='stack', text_auto='0.,3s',
                                                  category_orders={'portfolio': portfolio_listing,
                                                                   'frequency': ['Annually', 'Quarterly', 'Monthly', 'Semi-Monthly', 'One-Time', 'Unspecified']},
                                                color_discrete_map={'Annually': '#1e466e',
                                                                    'Quarterly': '#376795',
                                                                    'Monthly': '#528FAD',
                                                                    'Semi-Monthly': '#72BCD5',
                                                                    'One-Time': '#FFE6B7',
                                                                    'Unspecified':'#CDC6B8'})
    
    graph_pledges_by_portfolio_frequency.update_traces(textfont_size=10, marker={'cornerradius':4}, hovertemplate='Will Update this after ngl', textposition='inside')

    graph_pledges_by_portfolio_frequency.update_layout(yaxis={'tickfont': {'size': 10}, 'categoryorder': 'total ascending'}, 
                                  margin={'l':10, 'r': 10, 't': 10, 'b': 8},
                               plot_bgcolor='#fff', paper_bgcolor="#fff",
                               legend={'font': {'size': 10}, 'orientation':'h'})
    
    graph_pledges_by_portfolio_frequency.update_legends(yanchor="bottom", y=1.02, xanchor= 'right', x= 0.7, title=None)

    graph_pledges_by_portfolio_frequency.update_yaxes(type='category', title='Portfolio', linewidth=2.5, showgrid=False, 
                               linecolor='rgb(180, 180, 180)', ticksuffix="  ")
    
    graph_pledges_by_portfolio_frequency.update_xaxes(title='Total Pledge Sign Ups',
                              showgrid=True, zeroline=False, showline=False, 
                              showticklabels=True, tickwidth=2, gridcolor="rgba(60, 60, 60, 0.15)")
    
    return graph_pledges_by_portfolio_frequency
