import polars as pl
from dash import html, dcc, Input, Output, State, get_asset_url

import dash_mantine_components as dmc

import os

from pledges_by_type_graph import pledges_by_type_graph
from dash_iconify import DashIconify


def generateNewSignupsPledgesGoals(goal_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')



    ## Pull Initial Data from Polars ##
    ## Queries ##
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

        from public.oftw_pledges_raw opr 
        where pledge_status not in ('ERROR', 'Payment failure')
        and date_part('year', cast(pledge_starts_at as date)) >= 2015

        )

        select cast(COUNT(distinct donor_id) as real) as "Number of Donors"
        from a
        where (pledge_status in ('Active donor', 'One-Time'))
    
    '''

    query_active_pledges_total = '''

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

        from public.oftw_pledges_raw opr 
        where pledge_status not in ('ERROR', 'Payment failure')
        and date_part('year', cast(pledge_starts_at as date)) >= 2015

        )

        select cast(COUNT(distinct pledge_id) as real) as "Number of Pledges"
        from a
        where (pledge_status in ('Active donor'))
    
    '''


    query_pledge_attrition_rate = f'''

        select *,
        (("Active Pledges" + "Pre Churned Pledges") - ("Active Pledges" + "Pre Churned Pledges" - ("Churned Pledges" - "Added Pledges"))) / ("Active Pledges" + "Pre Churned Pledges") as "Churn Rate"
        from 
        public.oftw_churn_rate_fy
        where "Fiscal Year" = {goal_year}
   
    '''

    query_pledge_frequency_share = f'''

            select
        case 
        	when date_part('month', cast(pledge_created_at as date)) >= 7 then date_part('year', cast(pledge_created_at as date)) + 1
        	else date_part('year', cast(pledge_created_at as date)) 
        end as "Fiscal Year",

        case when pledge_status = 'One-Time' then 'One-Time' else 'Subscription' end as "Pledge Type",

        count(distinct pledge_id) "Created Pledges"
        from public.oftw_pledges_raw
        where case 
        	when date_part('month', cast(pledge_created_at as date)) >= 7 then date_part('year', cast(pledge_created_at as date)) + 1
        	else date_part('year', cast(pledge_created_at as date)) 
        end = {goal_year}
        group by 1, 2

    '''

    ## Total Active Donors Polars ##
    polars_total_active_donors = pl.read_database_uri(query=query_new_sign_ups_total, uri=postgres_uri, engine='adbc')

    ## Total Active Pledges Polars ##
    polars_total_active_pledges = pl.read_database_uri(query=query_active_pledges_total, uri=postgres_uri, engine='adbc')

    ## Churn Rate Polars ##
    polars_goal_churn_rate = pl.read_database_uri(query=query_pledge_attrition_rate, uri=postgres_uri, engine='adbc')

    ## Pledge Share Polars ##
    polars_pledge_frequency_share = pl.read_database_uri(query=query_pledge_frequency_share, uri=postgres_uri, engine='adbc')


    ## GV1 Section ##
    gv1 = polars_total_active_donors.select(pl.col('Number of Donors')).item()
    gv1_goal = 1200

    gv1_progress = []

    if round((gv1 / gv1_goal), 2) > 1.00:

        gv1_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv1) * gv1_goal), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'Active Donors Goal Progress: 100%'

            ),

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv1_goal * 1.00)) * (gv1 - gv1_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv1) * gv1_goal), 0)), color='green'),
                boxWrapperProps={"display": "contents"},
                label=f'Active Donors Goal Exceeded: {round(((100.00 / (gv1_goal * 1.00)) * (gv1 - gv1_goal)), 0):.0f}%'

            )
            

        ]

    else:

        gv1_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv1_goal*1.00)) * gv1), 0):.0f}%'), value=round(((100.00 / (gv1_goal * 1.00)) * gv1), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'Active Donors Goal Progress: {round(((100.00 / (gv1_goal*1.00)) * gv1), 0):.0f}%'

            )

        ]

    ## gv2 section ##
    gv2 = polars_total_active_pledges.select(pl.col('Number of Pledges')).item()
    gv2_goal = 850

    gv2_progress = []

    if round((gv2 / gv2_goal), 2) > 1.00:

        gv2_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv2) * gv2_goal), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'Active Pledges Goal Progress: 100%'

            ),

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv2_goal * 1.00)) * (gv2 - gv2_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv2) * gv2_goal), 0)), color='green'),
                boxWrapperProps={"display": "contents"},
                label=f'Active Pledges Goal Exceeded: {round(((100.00 / (gv2_goal * 1.00)) * (gv2 - gv2_goal)), 0):.0f}%'

            )         

        ]

    else:

        gv2_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv2_goal*1.00)) * gv2), 0):.0f}%'), value=round(((100.00 / (gv2_goal * 1.00)) * gv2), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'Active Pledges Goal Progress: {round(((100.00 / (gv2_goal*1.00)) * gv2), 0):.0f}%'

            )

        ]

    ## gv3 section ##
    
    gv3 = polars_goal_churn_rate.select(pl.col("Churn Rate")).item()
    ## gv3 = 0.19
    gv3_goal = 0.18

    gv3_progress = []

    ## Color Coding of Progress bars based on Pct Values ##
    ## If Within 5% then Orange, If Over then Red, else Green ##
    print(round(gv3, 2))
    if (round(gv3, 2) < (gv3_goal - 0.05)):

        gv3_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'Exceed Expectations'), value=100, color='green'),
                boxWrapperProps={"display": "contents"},
                label=f'Pledge Attrition Rate Progress: Exceed Expectations'

            )

        ]
        
    elif (round(gv3, 2) >= (gv3_goal - 0.05)) and (round(gv3, 2) < (gv3_goal)):

        gv3_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'Within Threshold (5%)'), value=100, color='orange'),
                boxWrapperProps={"display": "contents"},
                label=f'Pledge Attrition Rate Progress: Within 5% Threshold'

            )

        ]

    elif (round(gv3, 2) >= (gv3_goal)):

        gv3_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'Above Target'), value=100, color='red'),
                boxWrapperProps={"display": "contents"},
                label=f'Pledge Attrition Rate Progress: Failing, Currently Above Target'

            )

        ]

    ## gv4 section ##
    gv4_one_time = polars_pledge_frequency_share.filter(pl.col('Pledge Type') == 'One-Time').select(pl.col('Created Pledges')).item()

    gv4_subscription = polars_pledge_frequency_share.filter(pl.col('Pledge Type') == 'Subscription').select(pl.col('Created Pledges')).item()
    
    gv4_total = gv4_one_time + gv4_subscription

    gv4_progress = [

        dmc.FloatingTooltip(

            dmc.ProgressSection(dmc.ProgressLabel(f'Subscription'), value=round((gv4_subscription / gv4_total) * 100, 0), color='#1971c2'),
            boxWrapperProps={"display": "contents"},
            label=f'Percent Share Subscription Pledges: {((gv4_subscription / gv4_total) * 100):,.1f}%'

        ),

        dmc.FloatingTooltip(

            dmc.ProgressSection(dmc.ProgressLabel(f'One Time'), value=round((gv4_one_time / gv4_total) * 100, 0), color='#845ef7'),
            boxWrapperProps={"display": "contents"},
            label=f'Percent Share One-Time Pledges: {((gv4_one_time / gv4_total) * 100.00):,.1f}%'

        )

    ]

    return_array = [
        dmc.Group([

            html.Span([
                
                html.H2('Key Objectives & Goals', style={'marginBottom': '0', 'fontSize': 'xx-large', 'marginTop': '0.6rem'}),
                html.H4('Pledges & Donors', style={'color': 'grey', 'margin': '0'})
                
            ])

        ], style={'marginBottom': '0.5em'}, id='keys-objs-head-title'),
        
        dmc.Grid([
            
            ## Card for Total Active Donors ##
            dmc.GridCol([

                dmc.Paper([
                
                html.H5('Total Active Donors', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                html.Small('Active & One Time Donors', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                html.Small(f'Goal: {gv1_goal:.0f}', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                html.Span([
                    html.H2(f'{gv1:,.0f}', style={'marginTop': '0', 'marginBottom': '0'}), 
                    dmc.ProgressRoot(
                        gv1_progress,size='xl', mb='xs'
                    )
                ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-end', 'height': '100%'})

                ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')

            ],span={'base': 12, 'xs':6, 'md': 3}),

            dmc.GridCol([

                ## Card for Total Active Pledges ##
                ## Distinct Count of Active Donor Pledges ##
                dmc.Paper([

                    html.H5('Total Active Pledges', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                    html.Small('Active Pledges Only', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                    html.Small(f'Goal: {gv2_goal:.0f}', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                    html.Span([

                        html.H2(f'{gv2:,.0f}', style={'marginTop': '0', 'marginBottom': '0'}),
                        dmc.ProgressRoot(

                            gv2_progress,
                            size='xl', mb='xs'

                        )

                    ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-end', 'height': '100%'})

                ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')

            ],span={'base': 12, 'xs':6, 'md': 3}),

            
            dmc.GridCol([

                ## Card for Pledge Attrition Rate ##
                ## Using Distinct Count of Pledge IDs ##
                ## (Churned in Fiscal Year - Added in Fiscal Year) / Active Pledges at beginning of Fiscal Year ##
                ## Goal is 18 Percent ##
                dmc.Paper([

                    html.H5('Pledge Attrition Rate', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                    html.Small('Subscription Pledges Only', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                    html.Small(f'Goal: {gv3_goal:.0%}', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                    html.Span([

                        html.H2(f'{gv3:.2%}', style={'marginTop': '0', 'marginBottom': '0'}),
                        dmc.ProgressRoot(

                            gv3_progress,
                            size='xl', mb='xs'

                        )

                    ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-end', 'height': '100%'})

                ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')

            ],span={'base': 12, 'xs':6, 'md': 3}),


            dmc.GridCol([

                ## Card to show share of new sign ups that are subscriptions vs one time ##
                ## Using distinct count of Pledge IDs ##
                ## Using Pledge Created At Date (Not Pledge Starts Date) - Focused on sign ups ##
                ## No Goal currently ##
                dmc.Paper([

                    html.H5('Subscription Signup Ratio', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                    html.Small('Subscription vs One Time', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                    html.Small(f'Goal: N/A', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                    html.Span([

                        html.H2(f'{(gv4_subscription / gv4_total):.1%}', style={'marginTop': '0', 'marginBottom': '0'}), 

                        dmc.ProgressRoot(

                            gv4_progress,
                            size='xl', mb='xs'

                        )

                    ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-end', 'height': '100%'})

                ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')

            ], span={'base': 12, 'xs':6, 'md': 3})
                            
        ], style={'justifyContent':'space-around'}, gutter='xl', grow=True, id='display-cards-group-main'),

        dmc.Container([

            dmc.Paper([

                dmc.Group([

                    html.Span([
                        html.H2('Created Pledges By Pledge Type', style={'marginBottom': '0.05em'}, id='pledges-donor-graph-title'),
                        html.P('Subscription & One-Time', className='text-muted', id='pledges-donor-graph-subtitle')
                    ]),

                    ## Chart Selection Now Handled By Left Navigation ##
                    ## Instead used for Chart Options ##
                    html.Span([
                        dmc.Button(
                            children=[

                                html.Div([
                                    html.P('Chart Options', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                                    dmc.Badge('0 Options', variant='light', color='gray', style={'marginBottom': '0.5rem'})
                                ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                            ],
                            leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                            color='#6495ed',
                            radius='md',
                            size='md',
                            variant='filled',
                            disabled=True,
                            style={'height': '100%'},
                            id='chart-settings-button-click'

                        ),

                        dmc.Modal(id='chart-settings-modal')
                       
                    ], style={'alignSelf': 'flex-end'}, id='chart-settings-span')

                ], style={'marginBottom': '0'}, justify='space-between'),
                
                
                html.Hr(style={'margin': '0.5rem 0'}),
                html.P('''Displays the number of Pledge sign ups based on OFTW's financial calendar (FY starts in July) on a quarterly basis.
                       Pledges are split into One-Time and Subscription (Ongoing, Annual, Monthly, etc.)
                       Focuses on when pledge was signed up, regardless if pledge is currently cancelled / churned.''',
                       className='text-muted', id='pledges-donor-graph-description'),
                
                html.Span([
                    dcc.Graph(style={'height': '38.5vh', 'margin-bottom': '0.6rem'}, figure=pledges_by_type_graph(), id='pledges-donor-graph-figure')
                ], id='pledges-donor-graph-figure-span')

            
            ], shadow='lg', withBorder=True, radius='lg', px='xl', className='keys-objs-graph-card')

        ], style={'height': '56vh'}, className='keys-obj-graph-container')
    ]

    return return_array