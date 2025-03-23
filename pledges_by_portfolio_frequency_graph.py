import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px

import os

def pledges_by_portfolio_frequency_true(beginning_year, end_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Create the Query with between filter, use the calendar from DMC to provide the filtering changes ##
    query_pledges_by_portfolio_frequency = f'''

    with a as (
        select pledge_id, 
        frequency, 
        cast(pledge_created_at as date) "pledge_created_at",
        case 
        	when date_part('month',cast(pledge_created_at as date)) >= 7 then date_part('year',cast(pledge_created_at as date)) + 1
        	else date_part('year',cast(pledge_created_at as date))
        end as "fiscal_year"

        from public.oftw_pledges_raw),

        b as (

        select distinct pledge_id, portfolio
        from public.oftw_payments_raw opr),

        c as (

        select portfolio, count(distinct pledge_id), 
        row_number() over (order by count(distinct pledge_id) desc) "Ordering"
        from public.oftw_payments_raw
        where portfolio not in ('One for the World Discretionary Fund', 'One for the World Operating Costs')
        group by portfolio 
        order by count(distinct pledge_id) desc

        )

        select b."portfolio", a."frequency", c."Ordering", 
        count(distinct a.pledge_id) "pledge_sign_ups"
        from a 
        inner join b
        on a.pledge_id = b.pledge_id

        left join c
        on b."portfolio" = c."portfolio"

        where a."fiscal_year" >= {str(beginning_year)} and a."fiscal_year" <= {str(end_year)}
        and b.portfolio not in ('One for the World Discretionary Fund', 'One for the World Operating Costs')
        and a."frequency"  != ''

        group by b."portfolio", a."frequency", c."Ordering"
        order by c."Ordering", a."frequency" asc
    
    '''

    polars_pledges_by_portfolio_frequency = pl.read_database_uri(uri=postgres_uri, query=query_pledges_by_portfolio_frequency, engine='adbc')

    ## List for ordering the portfolios
    portfolio_listing = polars_pledges_by_portfolio_frequency.group_by(pl.col('portfolio'), pl.col('Ordering')).agg(pl.col('pledge_sign_ups').sort_by(pl.col('portfolio')).sum())

    portfolio_listing = portfolio_listing.select(pl.col('portfolio').sort_by(pl.col('Ordering'))).get_column('portfolio').to_list()

    ## Filtered pledges by portfolio
    ## Will need to add parameter inside function call for callback ##
    polars_pledges_by_portfolio_frequency = polars_pledges_by_portfolio_frequency.filter(pl.col('portfolio').is_in(portfolio_listing))

    graph_pledges_by_portfolio_frequency = px.bar(data_frame=polars_pledges_by_portfolio_frequency, y='portfolio', x='pledge_sign_ups', color='frequency',
                                                  orientation='h', barmode='stack', text_auto='0.,3s',
                                                  category_orders={'portfolio': portfolio_listing})
    
    graph_pledges_by_portfolio_frequency.update_traces(textfont_size=10, marker={'cornerradius':4}, hovertemplate='Will Update this after ngl', textposition='inside')

    graph_pledges_by_portfolio_frequency.update_layout(yaxis={'tickfont': {'size': 10}, 'categoryorder': 'total ascending'}, 
                                  margin={'l':10, 'r': 10, 't': 10, 'b': 8},
                               plot_bgcolor='#fff', paper_bgcolor="#fff",
                               legend={'font': {'size': 10}, 'orientation':'h'})
    
    graph_pledges_by_portfolio_frequency.update_legends(yanchor="bottom", y=1.02, xanchor= 'right', x= 0.5, title=None)

    graph_pledges_by_portfolio_frequency.update_yaxes(type='category', title='Portfolio', linewidth=2.5, showgrid=False, 
                               linecolor='rgb(180, 180, 180)', ticksuffix="  ")
    
    graph_pledges_by_portfolio_frequency.update_xaxes(title='Total Pledge Sign Ups',
                              showgrid=True, zeroline=False, showline=False, 
                              showticklabels=True, tickwidth=2, gridcolor="rgba(60, 60, 60, 0.15)")
    
    return graph_pledges_by_portfolio_frequency
