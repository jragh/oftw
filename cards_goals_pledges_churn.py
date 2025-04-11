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

        from oftw.public.oftw_pledges_raw opr 
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

            dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv1) * gv1_goal), 0), color='cyan'),
            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv1_goal * 1.00)) * (gv1 - gv1_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv1) * gv1_goal), 0)), color='green')

        ]

    else:

        gv1_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv1_goal*1.00)) * gv1), 0):.0f}%'), value=round(((100.00 / (gv1_goal * 1.00)) * gv1), 0), color='cyan')

        ]


    ## gv2 section ##
    gv2 = polars_total_active_pledges.select(pl.col('Number of Pledges')).item()
    gv2_goal = 850

    gv2_progress = []

    if round((gv2 / gv2_goal), 2) > 1.00:

        gv2_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv2) * gv2_goal), 0), color='cyan'),
            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv2_goal * 1.00)) * (gv2 - gv2_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv2) * gv2_goal), 0)), color='green')

        ]

    else:

        gv2_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv2_goal*1.00)) * gv2), 0):.0f}%'), value=round(((100.00 / (gv2_goal * 1.00)) * gv2), 0), color='cyan')

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

            dmc.ProgressSection(dmc.ProgressLabel(f'Exceed Expectations'), value=100, color='green')

        ]
        
    elif (round(gv3, 2) >= (gv3_goal - 0.05)) and (round(gv3, 2) < (gv3_goal)):

        gv3_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'Within Threshold (5%)'), value=100, color='orange')

        ]

    elif (round(gv3, 2) >= (gv3_goal)):

        gv3_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'Above Target'), value=100, color='red')

        ]

    ## gv4 section ##
    gv4_one_time = polars_pledge_frequency_share.filter(pl.col('Pledge Type') == 'One-Time').select(pl.col('Created Pledges')).item()

    gv4_subscription = polars_pledge_frequency_share.filter(pl.col('Pledge Type') == 'Subscription').select(pl.col('Created Pledges')).item()
    
    gv4_total = gv4_one_time + gv4_subscription

    gv4_progress = [

        dmc.ProgressSection(dmc.ProgressLabel(f'Subscription'), value=round((gv4_subscription / gv4_total) * 100, 0), color='#1971c2'),
        dmc.ProgressSection(dmc.ProgressLabel(f'One Time'), value=round((gv4_one_time / gv4_total) * 100, 0), color='#845ef7')

    ]



    header_return_array = [

        html.Span([
                
            html.H2('Key Objectives & Goals', style={'marginBottom': '0', 'fontSize': 'xx-large', 'marginTop': '0'}),
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

    with curr as (
    select *,
    case
    	when "CURRENCY SHORT" in ('GBP', 'AUD', 'EUR') then "CURRENCY RATE"
    	when "CURRENCY SHORT" in ('CAD', 'SGD', 'CHF') then (1.00 / "CURRENCY RATE")
    end as "CURRENCY RATE FINAL"
    from public.oftw_currency_conversion
    )
    
    select 
    case
    	when DATE_PART('month', cast(opr."date" as date)) >= 7 then DATE_PART('year', cast(opr."date" as date)) + 1
    	else DATE_PART('year', cast(opr."date" as date))
    end as "Fiscal Year",
    
    
    SUM(case
    	when opr.currency = 'USD' then opr.amount
    	else opr."amount" * curr."CURRENCY RATE FINAL"
    end) as "Payment Amount",
    
    count(*) "Number of Payments"
    
    from public.oftw_payments_raw opr 
    left join curr
    on cast(opr."date" as DATE) = cast(curr."DATE" as DATE) and opr.currency = curr."CURRENCY SHORT"
    
    where case
    	when DATE_PART('month', cast(opr."date" as date)) >= 7 then DATE_PART('year', cast(opr."date" as date)) + 1
    	else DATE_PART('year', cast(opr."date" as date))
    end = {goal_year}
    
    group by 1
    order by 1
    
    '''

    query_counter_money_moved_total = f'''
    
    with curr as (
    select *,
    case
    	when "CURRENCY SHORT" in ('GBP', 'AUD', 'EUR') then "CURRENCY RATE"
    	when "CURRENCY SHORT" in ('CAD', 'SGD', 'CHF') then (1.00 / "CURRENCY RATE")
    end as "CURRENCY RATE FINAL"
    from public.oftw_currency_conversion
    )

    select 
    case
    	when DATE_PART('month', cast(opr."date" as date)) >= 7 then DATE_PART('year', cast(opr."date" as date)) + 1
    	else DATE_PART('year', cast(opr."date" as date))
    end as "Fiscal Year",


    SUM(case
    	when opr.currency = 'USD' then opr.amount * opr.counterfactuality
    	else (opr."amount" * curr."CURRENCY RATE FINAL") * opr.counterfactuality
    end) as "Counterfactuality Payment Amount",

    count(*) "Number of Payments"

    from public.oftw_payments_raw opr 
    left join curr
    on cast(opr."date" as DATE) = cast(curr."DATE" as DATE) and opr.currency = curr."CURRENCY SHORT"

    where case
    	when DATE_PART('month', cast(opr."date" as date)) >= 7 then DATE_PART('year', cast(opr."date" as date)) + 1
    	else DATE_PART('year', cast(opr."date" as date))
    end = {goal_year}

    group by 1
    order by 1

    '''

    ## Only looks at ARR at the current time
    ## Uses the latest currency date for each currency to best match latest date pulled ##
    query_current_arr_calculation = f'''

    with max_curr as (

    select "CURRENCY", "CURRENCY SHORT", MAX(cast("DATE" as date)) "max_date"
    from public.oftw_currency_conversion
    where "CURRENCY RATE" is not null
    group by "CURRENCY", "CURRENCY SHORT"

    )

    ,curr as (
    select curr_int.*,
    case
    	when curr_int."CURRENCY SHORT" in ('GBP', 'AUD', 'EUR') then curr_int."CURRENCY RATE"
    	when curr_int."CURRENCY SHORT" in ('CAD', 'SGD', 'CHF') then (1.00 / curr_int."CURRENCY RATE")
    	when curr_int."CURRENCY SHORT" in ('USD') then 1.00
    end as "CURRENCY RATE FINAL"
    from public.oftw_currency_conversion curr_int
    inner join max_curr
    on curr_int."CURRENCY SHORT" = max_curr."CURRENCY SHORT" 
    and curr_int."CURRENCY" = max_curr."CURRENCY" 
    and cast(curr_int."DATE" as date) = max_curr."max_date"
    )

    select 

    count(distinct pledge.pledge_id) "Number of Pledges",
    SUM(
    case
    
    	when pledge.frequency in ('Annually', 'One-Time', 'Unspecified') and pledge.currency = 'USD' then pledge.contribution_amount
    	when pledge.frequency in ('Monthly') and pledge.currency = 'USD' then (pledge.contribution_amount * 12)
    	when pledge.frequency in ('Quarterly') and pledge.currency = 'USD' then (pledge.contribution_amount * 4)
    	when pledge.frequency in ('Semi-Monthly') and pledge.currency = 'USD' then (pledge.contribution_amount * 24)
    
    	when pledge.frequency in ('Annually', 'One-Time', 'Unspecified') and pledge.currency != 'USD' then pledge.contribution_amount * curr."CURRENCY RATE FINAL"
    	when pledge.frequency in ('Monthly') and pledge.currency != 'USD' then (pledge.contribution_amount * 12) * curr."CURRENCY RATE FINAL"
    	when pledge.frequency in ('Quarterly') and pledge.currency != 'USD' then (pledge.contribution_amount * 4) * curr."CURRENCY RATE FINAL"
    	when pledge.frequency in ('Semi-Monthly') and pledge.currency != 'USD' then (pledge.contribution_amount * 24) * curr."CURRENCY RATE FINAL"
    
    end
    )::real as "Total Pledge Amount"

    from public.oftw_pledges_raw pledge
    left join curr
    on pledge.currency = curr."CURRENCY SHORT"
    where pledge.pledge_status = 'Active donor'
    

    '''


    query_arpp_payments = f'''

    with curr as (
    select *,
    case
    	when "CURRENCY SHORT" in ('GBP', 'AUD', 'EUR') then "CURRENCY RATE"
    	when "CURRENCY SHORT" in ('CAD', 'SGD', 'CHF') then (1.00 / "CURRENCY RATE")
    end as "CURRENCY RATE FINAL"
    from public.oftw_currency_conversion
    )

    select 
    case
    	when DATE_PART('month', cast(opr."date" as date)) >= 7 then DATE_PART('year', cast(opr."date" as date)) + 1
    	else DATE_PART('year', cast(opr."date" as date))
    end as "Fiscal Year",

    SUM(case
    	when opr.currency = 'USD' then opr.amount
    	else opr."amount" * curr."CURRENCY RATE FINAL"
    end) as "Total Payment Amount",

    count(distinct opr.pledge_id) "Number of Paying Pledges"


    from public.oftw_payments_raw opr 
    left join curr
    on cast(opr."date" as DATE) = cast(curr."DATE" as DATE) and opr.currency = curr."CURRENCY SHORT"

    where case
    	when DATE_PART('month', cast(opr."date" as date)) >= 7 then DATE_PART('year', cast(opr."date" as date)) + 1
    	else DATE_PART('year', cast(opr."date" as date))
    end in ({goal_year}, {goal_year - 1})

    group by 1
    order by 1 
    
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

            dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv1) * gv1_goal), 0), color='cyan'),
            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv1_goal * 1.00)) * (gv1 - gv1_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv1) * gv1_goal), 0)), color='green')

        ]

    else:

        gv1_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv1_goal*1.00)) * gv1), 0):.0f}%'), value=round(((100.00 / (gv1_goal * 1.00)) * gv1), 0), color='cyan')

        ]

    ## gv2_section ##
    gv2 = polars_counter_money_moved.select(pl.col("Counterfactuality Payment Amount")).item()
    gv2_goal = 1200000

    gv2_progress = []

    if round((gv2 / gv2_goal), 2) > 1.00:

        gv2_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv2) * gv2_goal), 0), color='cyan'),
            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv2_goal * 1.00)) * (gv2 - gv2_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv2) * gv2_goal), 0)), color='green')

        ]

    else:

        gv2_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv2_goal*1.00)) * gv2), 0):.0f}%'), value=round(((100.00 / (gv2_goal * 1.00)) * gv2), 0), color='cyan')

        ]

    
    ## gv3 Section ##
    ## gv3_Section ##
    gv3 = polars_current_arr_calculation.select(pl.col('Total Pledge Amount')).item()
    gv3_goal = 1200000

    gv3_progress = []

    if round((gv3 / gv3_goal), 2) > 1.00:

        gv3_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'100%'), value=round(((100.00 / gv3) * gv3_goal), 0), color='cyan'),
            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv3_goal * 1.00)) * (gv3 - gv3_goal)), 0):.0f}%'), value=(100 - round(((100.00 / gv3) * gv3_goal), 0)), color='green')

        ]

    else:

        gv3_progress = [

            dmc.ProgressSection(dmc.ProgressLabel(f'{round(((100.00 / (gv3_goal*1.00)) * gv3), 0):.0f}%'), value=round(((100.00 / (gv3_goal * 1.00)) * gv3), 0), color='cyan')

        ]


    ## gv4 section ##
    ## gv4_section ##
    gv4_current_year = polars_arpp_payments.filter(pl.col('Fiscal Year') == goal_year).select(pl.col('Average Revenue Per Pledge')).item()
    gv4_previous_year = polars_arpp_payments.filter(pl.col('Fiscal Year') == (goal_year - 1)).select(pl.col('Average Revenue Per Pledge')).item()

    gv4_total = gv4_previous_year + gv4_current_year

    gv4_progress = [

        dmc.ProgressSection(dmc.ProgressLabel(f'FY{goal_year - 1}'), value=round((gv4_previous_year / gv4_total) * 100, 0), color='#1971c2'),
        dmc.ProgressSection(dmc.ProgressLabel(f'FY{goal_year}'), value=round((gv4_current_year / gv4_total) * 100, 0), color='#845ef7')

    ]


    ## Returning Header for Money Moved Section
    header_return_array = [

        html.Span([
                
            html.H2('Key Objectives & Goals', style={'marginBottom': '0', 'fontSize': 'xx-large', 'marginTop': '0'}),
            html.H4('Money Related Objectives', style={'color': 'grey', 'margin': '0'})
                
        ])

    ]

    cards_return_array = [

        dmc.GridCol([

            ## Card for Total Money Moved within Fiscal Year ##
            dmc.Paper([

                html.H5('Total Money Moved', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                html.Small('Active & One Time Pledges', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                html.Small(f'Goal: {gv1_goal:.0f}', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                html.Span([

                    html.H2(f'{gv1:,.0f}', style={'marginTop': '0', 'marginBottom': '0'}), 

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

            ## Card for Current Annualized Run Rate ##
            ## Using Pledged Amounts from Pledges Data Set, Active Donor Pledges Only ##
            ## (Churned in Fiscal Year - Added in Fiscal Year) / Active Pledges at beginning of Fiscal Year ##
            ## Goal is $1.2 Million ##
            dmc.Paper([

                html.H5('Current ARR', style={'fontWeight': 'bold', 'marginTop': '0', 'marginBottom': '0.1em'}),
                html.Small('Active Donor Pledges', style={'fontSize': '65%', 'fontWeight': 'bold', 'color': 'grey'}),
                html.Small(f'Goal: {gv3_goal:,}', style={'fontSize': '65%', 'fontWeight': '500', 'color': 'grey', 'fontStyle': 'italic'}),

                html.Span([

                    html.H2(f'{gv3:,.0f}', style={'marginTop': '0', 'marginBottom': '0'}), 

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

                    html.H2(f'{(gv4_current_year / gv4_total):.1%}', style={'marginTop': '0', 'marginBottom': '0'}), 

                    dmc.ProgressRoot(

                        gv4_progress,
                        size='xl', mb='xs'

                    )

                ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-end', 'height': '100%'})

            ], shadow='lg', withBorder=True, radius='lg', px='md', py='xs', className='keys-objs-head-card')

        ],span={'base': 12, 'xs':6, 'md': 3})

    ]

    return header_return_array, cards_return_array