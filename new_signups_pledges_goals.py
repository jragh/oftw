import polars as pl
from dash import html, dcc, Input, Output, State, get_asset_url

import dash_mantine_components as dmc

import os

def generateNewSignupsPledgesGoals(goal_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    print(postgres_uri)



    ## Pull Initial Data from Polars ##
    query_new_sign_ups_total = '''

    with a as (

        select case 
        	when date_part('month', cast(pledge_starts_at as date)) >= 7 then date_part('year', cast(pledge_starts_at as date)) + 1
        	else date_part('year', cast(pledge_starts_at as date))
        end as "Fiscal Year",

        case
        	when date_part('month', cast(pledge_starts_at as date)) >= 7 then date_part('month', cast(pledge_starts_at as date)) - 6
        	else date_part('month', cast(pledge_starts_at as date)) + 6 
        end as "Fiscal Month",

        cast(pledge_starts_at as date),
        pledge_status, 
        case when pledge_status = 'One-Time' then 'One-Time' else 'Subscription' end as "Pledge Type",
        pledge_id,
        donor_id

        from oftw.public.oftw_pledges_raw opr 
        where pledge_status not in ('ERROR', 'Payment failure')
        and date_part('year', cast(pledge_starts_at as date)) >= 2015

        )

        select "Fiscal Year",
        cast(COUNT(distinct pledge_id) as real) as "Number of Pledges"
        from a
        where pledge_status in ('Active donor', 'One-Time')
        group by "Fiscal Year"
        order by cast("Fiscal Year" as int) asc 
    
    '''

    polars_new_sign_ups_total = pl.read_database_uri(query=query_new_sign_ups_total, uri=postgres_uri, engine='adbc')

    gv1 = polars_new_sign_ups_total.filter(pl.col('Fiscal Year') == goal_year).select(pl.col('Number of Pledges')).item()

    return_array = [
        html.H2('New Sign Ups & Pledges', style={'marginBottom': '0'}),
        html.H4('Key Objectives & Goals', style={'color': 'grey', 'marginTop': '0'}),
        dmc.Group([
            
            ## Card for new sign ups ##
            dmc.Paper([
                
                html.H5('New Sign Ups', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                html.Small('Active & One Time', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),

                html.H2(f'{gv1:,.0f}', style={'marginTop': '0.5em', 'marginBottom': '0'}), 

                dmc.ProgressRoot(

                    dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / 1200.00) * gv1), 0):.0f}%'), value=round(((100.00 / 1200.00) * gv1), 0), color='cyan'),
                    size='xl', mb='xs'

                )

            ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')
                            
        ])
    ]

    return return_array