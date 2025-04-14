import polars as pl
from dash import html, dcc, Input, Output, State, get_asset_url

import dash_mantine_components as dmc

import os

from dash_iconify import DashIconify


def generate_cards_goals_pledges_churn(goal_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Pull Initial Data from Polars ##
    ## Queries ##
    query_new_sign_ups_total = '''

    SELECT "Number of Donors"
    FROM public.oftw_active_donor_card
    
    '''

    query_active_pledges_total = '''

    SELECT "Number of Pledges"
    FROM public.oftw_active_pledges_card
    
    '''


    query_pledge_attrition_rate = f'''

        select *,
        (("Active Pledges" + "Pre Churned Pledges") - ("Active Pledges" + "Pre Churned Pledges" - ("Churned Pledges" - "Added Pledges"))) / ("Active Pledges" + "Pre Churned Pledges") as "Churn Rate"
        from 
        public.oftw_churn_rate_fy
        where "Fiscal Year" = {goal_year}
   
    '''

    query_pledge_frequency_share = f'''

        SELECT "Fiscal Year", "Pledge Type", "Created Pledges"
        FROM public.oftw_pledge_frequency_share_card
        where "Fiscal Year" = {goal_year}

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
            label=f'Percent Share Subscription Pledges: {round((gv4_subscription / gv4_total) * 100, 0)}%'

        ),

        dmc.FloatingTooltip(

            dmc.ProgressSection(dmc.ProgressLabel(f'One Time'), value=round((gv4_one_time / gv4_total) * 100, 0), color='#845ef7'),
            boxWrapperProps={"display": "contents"},
            label=f'Percent Share One-Time Pledges: {round((gv4_one_time / gv4_total) * 100, 0)}%'

        )

    ]



    header_return_array = [

        html.Span([
                
            html.H2('Key Objectives & Goals', style={'marginBottom': '0', 'fontSize': 'xx-large', 'marginTop': '0.6rem'}),
            html.H4('Pledges & Donors', style={'color': 'grey', 'margin': '0'})
                
        ])

    ]

    cards_return_array = [

        dmc.GridCol([

            ## Card for Total Active Donors ##
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

        ], span={'base': 12, 'xs':6, 'md': 3}),

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

        ], span={'base': 12, 'xs':6, 'md': 3}),

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

        ], span={'base': 12, 'xs':6, 'md': 3}),

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

        ], span={'base': 12, 'xs':6, 'md': 3}),

    ]

    return header_return_array, cards_return_array


def generate_cards_goals_money_metrics(goal_year):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')

    ## Query Total Money Moved ##
    query_money_moved_total = f'''

    SELECT "Fiscal Year", "Payment Amount", "Number of Payments"
    FROM public.oftw_money_moved_total_card
    where "Fiscal Year" = {goal_year}
    
    '''

    query_counter_money_moved_total = f'''

    SELECT "Fiscal Year", "Counterfactuality Payment Amount", "Number of Payments"
    FROM public.oftw_cf_money_moved_card
    where "Fiscal Year" = {goal_year}

    '''

    ## Only looks at ARR at the current time
    ## Uses the latest currency date for each currency to best match latest date pulled ##
    query_current_arr_calculation = f'''

    SELECT "Number of Pledges", "Total Pledge Amount"
    FROM public.oftw_current_aprr_card
    

    '''


    query_arpp_payments = f'''

    SELECT "Fiscal Year", "Total Payment Amount", "Number of Paying Pledges"
    FROM public.oftw_aprr_1yr_comparison
    where "Fiscal Year" in ({goal_year}, {goal_year - 1})
    
    '''


    ## Polars Total Money Moved ##
    polars_money_moved_total = pl.read_database_uri(uri=postgres_uri, query=query_money_moved_total, engine='adbc')

    ## Polars Counterfactuality Money Moved ##
    polars_counter_money_moved = pl.read_database_uri(uri=postgres_uri, query=query_counter_money_moved_total, engine='adbc')

    ## Polars current ARR Calculation
    ## Only based on if the pledge is listed as 'Active Donor' ##
    polars_current_arr_calculation = pl.read_database_uri(uri=postgres_uri, query=query_current_arr_calculation, engine='adbc')

    ## Polars Average Revenue Per Pledge ##
    ## Per Pledge used instead of Per Donor Because of Many missing IDs ##
    polars_arpp_payments = pl.read_database_uri(uri=postgres_uri, query=query_arpp_payments, engine='adbc')
    polars_arpp_payments = polars_arpp_payments.with_columns((pl.col('Total Payment Amount') / pl.col('Number of Paying Pledges')).alias('Average Revenue Per Pledge'))

    ## gv1 section ##
    ## GV1 Section ##
    gv1 = polars_money_moved_total.select(pl.col('Payment Amount')).item()
    gv1_goal = 1800000

    gv1_progress = []

    if round((gv1 / gv1_goal), 2) > 1.00:

        gv1_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv1) * gv1_goal), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'Money Moved Goal Progress: 100%'

            ),

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv1_goal * 1.00)) * (gv1 - gv1_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv1) * gv1_goal), 0)), color='green'),
                boxWrapperProps={"display": "contents"},
                label=f'Money Moved Goal Exceeded: {round(((100.00 / (gv1_goal * 1.00)) * (gv1 - gv1_goal)), 0):.0f}%'

            )

        ]

    else:

        gv1_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv1_goal*1.00)) * gv1), 0):.0f}%'), value=round(((100.00 / (gv1_goal * 1.00)) * gv1), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'Money Moved Goal Progress: {round(((100.00 / (gv1_goal*1.00)) * gv1), 0):.0f}%'

            )

        ]

    ## gv2_section ##
    gv2 = polars_counter_money_moved.select(pl.col("Counterfactuality Payment Amount")).item()
    gv2_goal = 1260000

    gv2_progress = []

    if round((gv2 / gv2_goal), 2) > 1.00:

        gv2_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv2) * gv2_goal), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'CounterFactual Money Moved Goal Progress: 100%'

            ),

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv2_goal * 1.00)) * (gv2 - gv2_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv2) * gv2_goal), 0)), color='green'),
                boxWrapperProps={"display": "contents"},
                label=f'CounterFactual Money Moved Goal Exceeded: {round(((100.00 / (gv2_goal * 1.00)) * (gv2 - gv2_goal)), 0):.0f}%'

            )

        ]

    else:

        gv2_progress = [

            dmc.FloatingTooltip(
                
                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv2_goal*1.00)) * gv2), 0):.0f}%'), value=round(((100.00 / (gv2_goal * 1.00)) * gv2), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'CounterFactual Money Moved Goal Progress: {round(((100.00 / (gv2_goal*1.00)) * gv2), 0):.0f}%'
            
            )

        ]

    
    ## gv3 Section ##
    ## gv3_Section ##
    gv3 = polars_current_arr_calculation.select(pl.col('Total Pledge Amount')).item()
    gv3_goal = 1200000

    gv3_progress = []

    if round((gv3 / gv3_goal), 2) > 1.00:

        gv3_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv3) * gv3_goal), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'Current ARR Goal Progress: 100%'

            ),

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv3_goal * 1.00)) * (gv3 - gv3_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv3) * gv3_goal), 0)), color='green'),
                boxWrapperProps={"display": "contents"},
                label=f'Current ARR Goal Exceeded: {round(((100.00 / (gv3_goal * 1.00)) * (gv3 - gv3_goal)), 0):.0f}%'

            )            

        ]

    else:

        gv3_progress = [

            dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv3_goal*1.00)) * gv3), 0):.0f}%'), value=round(((100.00 / (gv3_goal * 1.00)) * gv3), 0), color='cyan'),
                boxWrapperProps={"display": "contents"},
                label=f'Current ARR Goal Progress: {round(((100.00 / (gv3_goal*1.00)) * gv3), 0):.0f}%'

            )      

        ]


    ## gv4 section ##
    ## gv4_section ##
    gv4_current_year = polars_arpp_payments.filter(pl.col('Fiscal Year') == goal_year).select(pl.col('Average Revenue Per Pledge')).item()
    gv4_previous_year = polars_arpp_payments.filter(pl.col('Fiscal Year') == (goal_year - 1)).select(pl.col('Average Revenue Per Pledge')).item()

    gv4_total = gv4_previous_year + gv4_current_year

    gv4_progress = [

        dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'FY{goal_year - 1}'), value=round((gv4_previous_year / gv4_total) * 100, 0), color='#1971c2'),
                boxWrapperProps={"display": "contents"},
                label=f'FY{goal_year - 1} Average Revenue Per Pledge (APRR): ${gv4_previous_year:,.0f}'

        ),

        dmc.FloatingTooltip(

                dmc.ProgressSection(dmc.ProgressLabel(f'FY{goal_year}'), value=round((gv4_current_year / gv4_total) * 100, 0), color='#845ef7'),
                boxWrapperProps={"display": "contents"},
                label=f'FY{goal_year} Average Revenue Per Pledge (APRR): ${gv4_current_year:,.0f}'

        )                

    ]


    ## Returning Header for Money Moved Section
    header_return_array = [

        html.Span([
                
            html.H2('Key Objectives & Goals', style={'marginBottom': '0', 'fontSize': 'xx-large', 'marginTop': '0.6rem'}),
            html.H4('Money Related Objectives', style={'color': 'grey', 'margin': '0'})
                
        ])

    ]

    cards_return_array = [

        dmc.GridCol([

            ## Card for Total Money Moved within Fiscal Year ##
            dmc.Paper([

                html.H5('Total Money Moved', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                html.Small('Active & One Time Pledges', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                html.Small(f'Goal: ${gv1_goal:,.0f}', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                html.Span([

                    html.H2(f'${gv1:,.0f}', style={'marginTop': '0', 'marginBottom': '0'}), 

                    dmc.ProgressRoot(

                        gv1_progress,size='xl', mb='xs'

                    )

                ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-end', 'height': '100%'})

            ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')

        ],span={'base': 12, 'xs':6, 'md': 3}, style={'display': 'flex', 'flex-direction': 'column'}),

        dmc.GridCol([

            ## Card for Total Counterfactuality Money Moved ##
            dmc.Paper([

                html.H5('Counterfactual Money Moved', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                html.Small('Active & One Time Pledges', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                html.Small(f'Goal: ${gv2_goal:,.0f}', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                html.Span([

                    html.H2(f'${gv2:,.0f}', style={'marginTop': '0', 'marginBottom': '0'}), 

                    dmc.ProgressRoot(

                        gv2_progress,
                        size='xl', mb='xs'

                    )

                ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-end', 'height': '100%'})

            ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')

        ],span={'base': 12, 'xs':6, 'md': 3}),

        dmc.GridCol([

            ## Card for Current Annualized Run Rate ##
            ## Using Pledged Amounts from Pledges Data Set, Active Donor Pledges Only ##
            ## (Churned in Fiscal Year - Added in Fiscal Year) / Active Pledges at beginning of Fiscal Year ##
            ## Goal is $1.2 Million ##
            dmc.Paper([

                html.H5('Current ARR', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                html.Small('Active Donor Pledges', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                html.Small(f'Goal: ${gv3_goal:,}', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                html.Span([

                    html.H2(f'${gv3:,.0f}', style={'marginTop': '0', 'marginBottom': '0'}), 

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

                html.H5('1Yr APRR Change', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                html.Small('Current vs Previous Fiscal Year', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                html.Small(f'All Payments, Goal: N/A', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                html.Span([

                    html.H2(f'{((gv4_current_year - gv4_previous_year) / gv4_previous_year):.1%}', style={'marginTop': '0', 'marginBottom': '0'}), 

                    dmc.ProgressRoot(

                        gv4_progress,
                        size='xl', mb='xs'

                    )

                ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-end', 'height': '100%'})

            ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')

        ],span={'base': 12, 'xs':6, 'md': 3})

    ]

    return header_return_array, cards_return_array