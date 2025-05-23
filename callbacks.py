from dash.dependencies import Output, Input, State

from dash import no_update, dcc, callback_context, html

import dash_mantine_components as dmc

from dash_iconify import DashIconify

from datetime import datetime, timedelta

from pledges_by_type_graph import pledges_by_type_graph
from pledges_by_portfolio_frequency_graph import pledges_by_portfolio_frequency_true
from churned_pledges_by_fiscal_year_graph import generate_churned_pledges_by_fiscal_year
from churned_before_payment_graph import generate_churned_before_payment_graph
from cards_goals_pledges_churn import generate_cards_goals_pledges_churn, generate_cards_goals_money_metrics
from money_moved_annual_monthly_graph import generate_money_moved_annual_graph, generate_arpp_annual_graph, generate_money_moved_monthly_graph, generate_arpp_monthly_graph
from ttv_by_fiscal_year_graph import generate_ttv_by_fiscal_year


def pledges_donor_page_graph_selector(app):
        
    ## Navigation Consts ##
    navigation_ids = ['navbar-okr-1','navbar-okr-2', 'navbar-okr-3', 'navbar-okr-4', 'navbar-mmg-1', 'navbar-mmg-2', 'navbar-mmg-3', 'navbar-mmg-4', 'navbar-msc-1']
    navigation_inputs = [Input(i, 'n_clicks') for i in navigation_ids]

    navigation_outputs = [Output(i, 'active') for i in navigation_ids]

    print(navigation_inputs)

    ## Portfolio Total List ##
    portfolio_listing_full = ['Animal Charity Evaluators',
    'Auswahl durch Effektiv Spenden',
    'Carbon180',
    'Clean Air Task Force',
    'Custom Portfolio',
    'D-Rev',
    'Development Media International',
    'END Fund (Deworming Program)',
    'Effektiv Spenden Operating Costs',
    'Entire OFTW Portfolio',
    'Evidence Action',
    'Evidence Action (Dispensers for Safe Water)',
    'Family Empowerment Media',
    'Fistula Foundation',
    'Food Fortification Initiative',
    'GiveWell (Maximum Impact Fund)',
    'GiveWell All Grants Fund',
    'Global Alliance for Improved Nutrition',
    'Innovations for Poverty Action',
    'Iodine Global Network',
    'Kirkland & Ellis Matching Fund',
    'Living Goods',
    'Nagel Custom Portfolio',
    'New Incentives',
    'OFTW Top Pick: Against Malaria Foundation',
    'OFTW Top Pick: Evidence Action (Deworming Program)',
    'OFTW Top Pick: GiveDirectly',
    'OFTW Top Pick: Helen Keller International',
    'OFTW Top Pick: Malaria Consortium',
    'OFTW Top Picks',
    'One Acre Fund',
    'Other Organization',
    'Oxfam',
    'Population Services International',
    'Possible',
    'Precision Agriculture for Development',
    'Project Healthy Children',
    'RC Forward Global Health Fund',
    'Schistosomiasis Control Initiative',
    'Seva',
    'Sightsavers (Deworming Program)',
    'StrongMinds',
    'The Humane League',
    'Village Enterprise',
    'Wild Animal Initiative',
    'Zusha']
   
    ## Navigation Chart and Div Replacement ##
    @app.callback(Output(component_id='pledges-donor-graph-title', component_property='children'),
                  Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
                  Output(component_id='pledges-donor-graph-description', component_property='children'),
                  Output(component_id='pledges-donor-graph-figure-span', component_property='children'),
                  navigation_inputs,
                  prevent_initial_call=True)
    def navigation_click_charts_update(*args):

        navigation_ids_intermediate = navigation_ids
        ctx = callback_context
        ctx_id_activated = ctx.triggered[0]['prop_id'].split('.')[0]

        if ctx.triggered is None:

            return no_update, no_update, no_update, no_update
        
        if ctx_id_activated == navigation_ids_intermediate[0]:

            description = '''Displays the number of Pledge sign ups based on OFTW's financial calendar (FY starts in July) on a quarterly basis.
                       Pledges are split into One-Time and Subscription (Ongoing, Annual, Monthly, etc.)
                       Focuses on when pledge was signed up, regardless if pledge is currently cancelled / churned.'''
            
            return 'Created Pledges By Pledge Type', 'Subscription & One-Time', description, dcc.Graph(style={'height': '38.5vh', 'margin-bottom': '0.6rem'}, figure=pledges_by_type_graph(), id='pledges-donor-graph-figure')
        
        elif ctx_id_activated == navigation_ids_intermediate[1]:

            ## Hardcoded Top 8 portfolios, Maybe make this dynamic instead? ##
            starting_portfolio_list = [

                'OFTW Top Picks'
                ,'Entire OFTW Portfolio'
                ,'Custom Portfolio'
                ,'OFTW Top Pick: Against Malaria Foundation'
                ,'GiveWell (Maximum Impact Fund)'
                

            ]

            description = '''Displays the total number of pledges signed up by portfolio in the specified time period.
            This includes All pledges whether they are active or churned, and frequency includes subscription based and One - Time pledges.
            Use the Year Selection to choose fiscal year ranges, and the portfolio selector to choose portfolios.'''

            subtitle = 'FY2014 - FY2025 (Subscription & One Time)'

            return 'Created Pledges By Portfolio & Frequency', subtitle, description, dcc.Graph(style={'height': '37vh', 'margin-bottom': '0.6rem'}, figure=pledges_by_portfolio_frequency_true(2014, 2025, starting_portfolio_list), id='pledges-donor-graph-figure-2')
        
        elif ctx_id_activated == navigation_ids_intermediate[2]:

            title = 'Change in Active Pledges By Fiscal Year'

            description = '''Displays the Total Change in Active Pledges between Fiscal Years. 
            The calculation uses Total Pledges Active at the beginning of Fiscal Year - Total Pledges Active at End of Fiscal Year.
            This handles pledges that were both started and churned within the same year.'''

            subtitle = 'FY2018 - FY2025 (Subscription Based Pledges)'

            return title, subtitle, description, dcc.Graph(style={'height': '40vh'}, figure=generate_churned_pledges_by_fiscal_year(2018, 2025), id='pledges-donor-graph-figure-3')
        

        elif ctx_id_activated == navigation_ids_intermediate[3]:

            title= 'Pledges Churned Before First Payment'

            subtitle = 'FY2018 - FY2025 (Subscription Based Pledges)'

            description = '''Displays the Number of Pledges Started vs Number of Pledges Churned without a single payment, based on the Fiscal Year of the pledge starting.
            Only includes Subscription based pledges; Churned Pledges are those with status of "Churned Doner" or "Payment Failed".'''

            return title, subtitle, description, dcc.Graph(style={'height': '39vh', 'margin-bottom': '0.6rem'}, figure=generate_churned_before_payment_graph(2018, 2025), id='pledges-donor-graph-figure-4')
        

        elif ctx_id_activated == navigation_ids_intermediate[4]:

            title= 'Payment Recieved By Fiscal Year'

            subtitle = 'FY2018 - FY2025 (One - Time & Subscription Based Payments)'

            description = '''Displays the Total Payments Recieved in USD in the specified Fiscal Year, split by Payment Frequency. Includes both One-Time and Subscription payments.'''

            return title, subtitle, description, dcc.Graph(style={'height': '38vh', 'margin-bottom': '0.6rem'}, figure=generate_money_moved_annual_graph(2018, 2025), id='pledges-donor-graph-figure-5')
        

        elif ctx_id_activated == navigation_ids_intermediate[5]:

            title= 'Payment Recieved By Fiscal Year & Month'

            subtitle = 'FY2024 - FY2025 (One - Time & Subscription Based Payments)'

            description = '''Displays the Total Payments Recieved in USD in the specified Fiscal Year, split by Payment Frequency. 
            Includes both One-Time and Subscription payments.
            Fiscal Year Starts in July, So July is Month 1, August is Month 2, etc.'''

            return title, subtitle, description, dcc.Graph(style={'height': '37.5vh', 'margin-bottom': '0.6rem'}, figure=generate_money_moved_monthly_graph(2024, 2025), id='pledges-donor-graph-figure-6')


        elif ctx_id_activated == navigation_ids_intermediate[6]:

            title = 'Average Revenue Per Pledge (Annual)'

            subtitle = 'FY2018 - FY2025 (One - Time & Subscription Based Payments)'

            description = '''Displays how much revenue, on average we can expect to generate per pledge.
            Calculated by dividing Total Payment Revenue by Total Distinct Pledges within a given fiscal year. 
            Split by One Time & Subscription Pledges.'''

            return title, subtitle, description, dcc.Graph(style={'height': '37.5vh', 'margin-bottom': '0.6rem'}, figure=generate_arpp_annual_graph(2018, 2025), id='pledges-donor-graph-figure-7')
        
        elif ctx_id_activated == navigation_ids_intermediate[7]:

            title = 'Average Revenue Per Pledge (Monthly)'

            subtitle = 'FY2024 - FY2025 (Subscription Payments Only)'

            description = '''Displays how much revenue, on average we can expect to generate per pledge.
            Calculated by dividing Total Payment Revenue by Total Distinct Pledges within a given Fiscal Year & Month. 
            Subscription Based Pledges only, Filter by Payment Platform in the options.'''

            return title, subtitle, description, dcc.Graph(style={'height': '37.5vh', 'margin-bottom': '0.6rem'}, figure=generate_arpp_monthly_graph(2024, 2025, []), id='pledges-donor-graph-figure-8')
        
        elif ctx_id_activated == navigation_ids_intermediate[8]:

            title = 'Time to First Payment (TFP) By Fiscal Year'

            subtitle = 'FY2016 - FY2025 (Subscription Payments Only)'

            description = '''Displays the Number of Subscription Pledges by Fiscal Year, split by the time between Pledge Creation Date & Pledge Start Date (TFP).
            TFP represents the duration it takes for OFTW to begin generating revenue from a subscrption. 
            A shorter TFP illustrates new donors are excited to begin donating and will most likely exhibit lower churn.
            A higher TFP increases the liklihood of churn, illustrates potential incorrect market fit, and ineffective conveyance of OFTW's mission and importance.'''

            return title, subtitle, description, dcc.Graph(style={'height': '35.75vh', 'margin-bottom': '0.6rem'}, figure=generate_ttv_by_fiscal_year(2016, 2025), id='pledges-donor-graph-figure-9') 
        
        else:

            return no_update, no_update, no_update, no_update
        

    ## Navigation Callbacks ##
    @app.callback(navigation_outputs, navigation_inputs, prevent_initial_call=True)

    def navigation_click_page_update(*args):

        navigation_ids_intermediate = navigation_ids

        ctx = callback_context

        if ctx.triggered is None:

            return [no_update for i in navigation_ids_intermediate]
        
        return_dict = {i: (ctx.triggered[0]['prop_id'].split('.')[0] == i) for i in navigation_ids_intermediate}

        print(list(return_dict.values()))
        
        return list(return_dict.values())
    
    ## Callback to change Settings Button and Associated Modal ##
    @app.callback(
        Output(component_id='chart-settings-span', component_property='children'),
        navigation_inputs,
        prevent_initial_call=True
    )

    def navigation_click_button_update(*args):

        navigation_ids_intermediate = navigation_ids

        ctx = callback_context

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if ctx.triggered is None:

            return no_update
        
        elif triggered_id == navigation_ids_intermediate[0]:

            return_array = [

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

            ]

            return return_array
        
        elif triggered_id == navigation_ids_intermediate[1]:

            ## Portfolio Dropdown Options
            selected_portfolio_list = [

                'OFTW Top Picks'
                ,'Entire OFTW Portfolio'
                ,'Custom Portfolio'
                ,'OFTW Top Pick: Against Malaria Foundation'
                ,'GiveWell (Maximum Impact Fund)'

            ]

            return_array = [

                dmc.Button(
                    children=[
                        
                        html.Div([
                            html.P('Chart Options', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                            dmc.Badge('2 Options', variant='filled', color='#1971c2', style={'marginBottom': '0.5rem'})
                                ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                            ],
                            leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                            color='#6495ed',
                            radius='md',
                            size='md',
                            variant='filled',
                            disabled=False,
                            style={'height': '100%'},
                            id='chart-settings-button-click'

                        ),

                dmc.Modal(
                    id='chart-settings-modal',
                    centered=True,
                    children=[
                        html.H2('Created Pledges By Portfolio & Frequency', style={'marginBottom': '0.05em', 'marginTop': '0'}),
                        html.P('Chart Options', className='text-muted'),
                        html.Hr(style={'margin': '0.5rem 0'}),

                        ## Fiscal Year Range Selection ##
                        dmc.YearPickerInput(
                            type='range',
                            label='Select Fiscal Year Range',
                            placeholder='Select a range of years...',
                            leftSection=DashIconify(icon='clarity:calendar-line', width=16, height=16),
                            minDate=datetime(2014, 1, 1),
                            maxDate=datetime(2025, 1, 1),
                            value=[datetime(2014, 1, 1), datetime(2025, 1, 1)],
                            id='date-filter-chart-2',
                            style={'marginBottom': '1.5rem'},
                            clearable=False
                        ),

                        dmc.MultiSelect(
                            hidePickedOptions=True,
                            searchable=True,
                            description='''Select Portfolios to be viewed based on the number of pledges signed up across selected fiscal years.''',
                            label='Portfolio Selection',
                            clearable=False,
                            id='portfolio-filter-chart-2',
                            value=selected_portfolio_list,
                            data=portfolio_listing_full,
                            maxDropdownHeight=200,
                            leftSectionPointerEvents="none",
                            leftSection=DashIconify(icon="bi-book"),
                            styles={'pillsList': {'overflowY': 'scroll', 'maxHeight': '150px'}},
                            style={'marginBottom': '1.5rem'}
                            
                        ),

                        dmc.Button("Click to set options",
                                   fullWidth=True, 
                                   variant='filled', 
                                   leftSection=DashIconify(icon='clarity:check-line', width=24, height=24),
                                   color="rgb(32, 201, 151)",
                                   id='modal-filter-accept-button-2'
                        )

                    ],
                    styles={
                        'body': {'padding': '0 2.5rem 3rem 2.5rem'},
                        'header': {'paddingTop': '0', 'paddingBottom': '0'}
                    }
                )

            ]

            return return_array
        
        elif triggered_id == navigation_ids_intermediate[2]:

            return_array = [

                ## Button Displayed to User ##
                dmc.Button(
                    children=[
                        
                        html.Div([
                            html.P('Chart Filters', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                            dmc.Badge('1 Option', variant='filled', color='#1971c2', style={'marginBottom': '0.5rem'})
                                ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                            ],
                            leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                            color='#6495ed',
                            radius='md',
                            size='md',
                            variant='filled',
                            disabled=False,
                            style={'height': '100%'},
                            id='chart-settings-button-click'

                ),

                ## Modal for Filtering ##
                dmc.Modal(
                    id='chart-settings-modal',
                    centered=True,
                    children=[
                        html.H2('Change in Active Pledges By Fiscal Year', style={'marginBottom': '0.05em', 'marginTop': '0'}),
                        html.P('Chart Options', className='text-muted'),
                        html.Hr(style={'margin': '0.5rem 0'}),

                        ## Fiscal Year Range Selection ##
                        dmc.YearPickerInput(
                            type='range',
                            label='Select Fiscal Year Range',
                            placeholder='Select a range of years...',
                            leftSection=DashIconify(icon='clarity:calendar-line', width=16, height=16),
                            minDate=datetime(2018, 1, 1),
                            maxDate=datetime(2025, 1, 1),
                            value=[datetime(2018, 1, 1), datetime(2025, 1, 1)],
                            id='date-filter-chart-3',
                            style={'marginBottom': '1.5rem'},
                            clearable=False
                        ),

                        dmc.Button("Click to set options",
                                   fullWidth=True, 
                                   variant='filled', 
                                   leftSection=DashIconify(icon='clarity:check-line', width=24, height=24),
                                   color="rgb(32, 201, 151)",
                                   id='modal-filter-accept-button-3'
                        )

                    ],
                    styles={
                        'body': {'padding': '0 2.5rem 3rem 2.5rem'},
                        'header': {'paddingTop': '0', 'paddingBottom': '0'}
                    }
                )

            ]

            return return_array
        
        elif triggered_id == navigation_ids_intermediate[3]:

            return_array = [

                ## Button Displayed to User ##
                dmc.Button(
                    children=[
                        
                        html.Div([
                            html.P('Chart Filters', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                            dmc.Badge('1 Option', variant='filled', color='#1971c2', style={'marginBottom': '0.5rem'})
                        ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                    ],
                    leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                    color='#6495ed',
                    radius='md',
                    size='md',
                    variant='filled',
                    disabled=False,
                    style={'height': '100%'},
                    id='chart-settings-button-click'

                ),

                ## Modal for Filtering ##
                dmc.Modal(
                    id='chart-settings-modal',
                    centered=True,
                    children=[
                        html.H2('Change in Active Pledges By Fiscal Year', style={'marginBottom': '0.05em', 'marginTop': '0'}),
                        html.P('Chart Options', className='text-muted'),
                        html.Hr(style={'margin': '0.5rem 0'}),

                        ## Fiscal Year Range Selection ##
                        dmc.YearPickerInput(
                            type='range',
                            label='Select Fiscal Year Range',
                            placeholder='Select a range of years...',
                            leftSection=DashIconify(icon='clarity:calendar-line', width=16, height=16),
                            minDate=datetime(2018, 1, 1),
                            maxDate=datetime(2025, 1, 1),
                            value=[datetime(2018, 1, 1), datetime(2025, 1, 1)],
                            id='date-filter-chart-4',
                            style={'marginBottom': '1.5rem'},
                            clearable=False
                        ),

                        dmc.Button("Click to set options",
                                   fullWidth=True, 
                                   variant='filled', 
                                   leftSection=DashIconify(icon='clarity:check-line', width=24, height=24),
                                   color="rgb(32, 201, 151)",
                                   id='modal-filter-accept-button-4'
                        )

                    ],
                    styles={
                        'body': {'padding': '0 2.5rem 3rem 2.5rem'},
                        'header': {'paddingTop': '0', 'paddingBottom': '0'}
                    }
                )

            ]

            return return_array
        
        elif triggered_id == navigation_ids_intermediate[4]:

            return_array = [

                ## Button displayed to the end user ##
                dmc.Button(
                    children=[
                        
                        html.Div([
                            html.P('Chart Filters', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                            dmc.Badge('1 Option', variant='filled', color='#1971c2', style={'marginBottom': '0.5rem'})
                        ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                    ],
                    leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                    color='#6495ed',
                    radius='md',
                    size='md',
                    variant='filled',
                    disabled=False,
                    style={'height': '100%'},
                    id='chart-settings-button-click'

                ),

                ## Modal for Filtering ##
                dmc.Modal(
                    id='chart-settings-modal',
                    centered=True,
                    children=[
                        html.H2('Change in Total Payments Recieved (Annual)', style={'marginBottom': '0.05em', 'marginTop': '0'}),
                        html.P('Chart Options', className='text-muted'),
                        html.Hr(style={'margin': '0.5rem 0'}),

                        ## Fiscal Year Range Selection ##
                        dmc.YearPickerInput(
                            type='range',
                            label='Select Fiscal Year Range',
                            placeholder='Select a range of Fiscal Years...',
                            leftSection=DashIconify(icon='clarity:calendar-line', width=16, height=16),
                            minDate=datetime(2018, 1, 1),
                            maxDate=datetime(2025, 1, 1),
                            value=[datetime(2018, 1, 1), datetime(2025, 1, 1)],
                            id='date-filter-chart-5',
                            style={'marginBottom': '1.5rem'},
                            clearable=False
                        ),

                        dmc.Button("Click to set options",
                                   fullWidth=True, 
                                   variant='filled', 
                                   leftSection=DashIconify(icon='clarity:check-line', width=24, height=24),
                                   color="rgb(32, 201, 151)",
                                   id='modal-filter-accept-button-5'
                        )

                    ],
                    styles={
                        'body': {'padding': '0 2.5rem 3rem 2.5rem'},
                        'header': {'paddingTop': '0', 'paddingBottom': '0'}
                    }
                )

            ]

            return return_array
        
        elif triggered_id == navigation_ids_intermediate[5]:

            return_array = [

                ## Button displayed to the end user ##
                dmc.Button(
                    children=[
                        
                        html.Div([
                            html.P('Chart Filters', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                            dmc.Badge('1 Option', variant='filled', color='#1971c2', style={'marginBottom': '0.5rem'})
                        ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                    ],
                    leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                    color='#6495ed',
                    radius='md',
                    size='md',
                    variant='filled',
                    disabled=False,
                    style={'height': '100%'},
                    id='chart-settings-button-click'

                ),

                ## Modal for Filtering ##
                dmc.Modal(
                    id='chart-settings-modal',
                    centered=True,
                    children=[
                        html.H2('Change in Total Payments Recieved (Monthly)', style={'marginBottom': '0.05em', 'marginTop': '0'}),
                        html.P('Chart Options', className='text-muted'),
                        html.Hr(style={'margin': '0.5rem 0'}),

                        ## Fiscal Year Range Selection ##
                        dmc.YearPickerInput(
                            type='range',
                            label='Select Fiscal Year Range',
                            placeholder='Select a range of Fiscal Years...',
                            leftSection=DashIconify(icon='clarity:calendar-line', width=16, height=16),
                            minDate=datetime(2018, 1, 1),
                            maxDate=datetime(2025, 1, 1),
                            value=[datetime(2024, 1, 1), datetime(2025, 1, 1)],
                            id='date-filter-chart-6',
                            style={'marginBottom': '1.5rem'},
                            clearable=False
                        ),

                        dmc.Button("Click to set options",
                                   fullWidth=True, 
                                   variant='filled', 
                                   leftSection=DashIconify(icon='clarity:check-line', width=24, height=24),
                                   color="rgb(32, 201, 151)",
                                   id='modal-filter-accept-button-6'
                        )

                    ],
                    styles={
                        'body': {'padding': '0 2.5rem 3rem 2.5rem'},
                        'header': {'paddingTop': '0', 'paddingBottom': '0'}
                    }
                )

            ]

            return return_array

        
        elif triggered_id == navigation_ids_intermediate[6]:

            return_array = [

                ## Button displayed to the end user ##
                dmc.Button(
                    children=[
                        
                        html.Div([
                            html.P('Chart Filters', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                            dmc.Badge('1 Option', variant='filled', color='#1971c2', style={'marginBottom': '0.5rem'})
                        ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                    ],
                    leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                    color='#6495ed',
                    radius='md',
                    size='md',
                    variant='filled',
                    disabled=False,
                    style={'height': '100%'},
                    id='chart-settings-button-click'

                ),

                ## Modal for Filtering ##
                dmc.Modal(
                    id='chart-settings-modal',
                    centered=True,
                    children=[
                        html.H2('Change in Average Revenue Per Pledge (Annual)', style={'marginBottom': '0.05em', 'marginTop': '0'}),
                        html.P('Chart Options', className='text-muted'),
                        html.Hr(style={'margin': '0.5rem 0'}),

                        ## Fiscal Year Range Selection ##
                        dmc.YearPickerInput(
                            type='range',
                            label='Select Fiscal Year Range',
                            placeholder='Select a range of Fiscal Years...',
                            leftSection=DashIconify(icon='clarity:calendar-line', width=16, height=16),
                            minDate=datetime(2018, 1, 1),
                            maxDate=datetime(2025, 1, 1),
                            value=[datetime(2018, 1, 1), datetime(2025, 1, 1)],
                            id='date-filter-chart-7',
                            style={'marginBottom': '1.5rem'},
                            clearable=False
                        ),

                        dmc.Button("Click to set options",
                                   fullWidth=True, 
                                   variant='filled', 
                                   leftSection=DashIconify(icon='clarity:check-line', width=24, height=24),
                                   color="rgb(32, 201, 151)",
                                   id='modal-filter-accept-button-7'
                        )

                    ],
                    styles={
                        'body': {'padding': '0 2.5rem 3rem 2.5rem'},
                        'header': {'paddingTop': '0', 'paddingBottom': '0'}
                    }
                )

            ]

            return return_array
        
        elif triggered_id == navigation_ids_intermediate[7]:

            payment_platform_selection_list = [

                'Donational'
                ,'Off Platform'
                ,'NFG'
                ,'Benevity'
                ,'Squarespace'
                ,'Gift Aid'
                
            ]

            return_array = [

                ## Button displayed to the end user ##
                dmc.Button(
                    children=[
                        
                        html.Div([
                            html.P('Chart Filters', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                            dmc.Badge('2 Options', variant='filled', color='#1971c2', style={'marginBottom': '0.5rem'})
                        ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                    ],
                    leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                    color='#6495ed',
                    radius='md',
                    size='md',
                    variant='filled',
                    disabled=False,
                    style={'height': '100%'},
                    id='chart-settings-button-click'

                ),

                ## Modal for Filtering ##
                dmc.Modal(
                    id='chart-settings-modal',
                    centered=True,
                    children=[
                        html.H2('Change in Annual Revenue Per Pledge (Monthly)', style={'marginBottom': '0.05em', 'marginTop': '0'}),
                        html.P('Chart Options', className='text-muted'),
                        html.Hr(style={'margin': '0.5rem 0'}),

                        ## Fiscal Year Range Selection ##
                        dmc.YearPickerInput(
                            type='range',
                            label='Select Fiscal Year Range',
                            placeholder='Select a range of years...',
                            leftSection=DashIconify(icon='clarity:calendar-line', width=16, height=16),
                            minDate=datetime(2018, 1, 1),
                            maxDate=datetime(2025, 1, 1),
                            value=[datetime(2024, 1, 1), datetime(2025, 1, 1)],
                            id='date-filter-chart-8',
                            style={'marginBottom': '1.5rem'},
                            clearable=False
                        ),

                        dmc.MultiSelect(
                            hidePickedOptions=True,
                            searchable=True,
                            description='''Select Payment Platforms to be viewed.''',
                            label='Payment Platform Selection',
                            clearable=False,
                            id='payment-filter-chart-8',
                            value=[],
                            data=payment_platform_selection_list,
                            maxDropdownHeight=200,
                            leftSectionPointerEvents="none",
                            leftSection=DashIconify(icon="bi-book"),
                            styles={'pillsList': {'overflowY': 'scroll', 'maxHeight': '150px'}},
                            style={'marginBottom': '1.5rem'}
                            
                        ),

                        dmc.Button("Click to set options",
                                   fullWidth=True, 
                                   variant='filled', 
                                   leftSection=DashIconify(icon='clarity:check-line', width=24, height=24),
                                   color="rgb(32, 201, 151)",
                                   id='modal-filter-accept-button-8'
                        )

                    ],
                    styles={
                        'body': {'padding': '0 2.5rem 3rem 2.5rem'},
                        'header': {'paddingTop': '0', 'paddingBottom': '0'}
                    }
                )

            ]

            return return_array
        
        elif triggered_id == navigation_ids_intermediate[8]:

            return_array = [

                ## Button displayed to the end user ##
                dmc.Button(
                    children=[
                        
                        html.Div([
                            html.P('Chart Filters', style={'fontSize': '0.85rem', 'margin': '0.5rem 0'}),
                            dmc.Badge('1 Option', variant='filled', color='#1971c2', style={'marginBottom': '0.5rem'})
                        ],style={'display': 'flex', 'flexDirection': 'column', 'flex': '1'})
                    ],
                    leftSection=DashIconify(icon='clarity:settings-solid', height=24, width=24),
                    color='#6495ed',
                    radius='md',
                    size='md',
                    variant='filled',
                    disabled=False,
                    style={'height': '100%'},
                    id='chart-settings-button-click'

                ),

                ## Modal for Filtering ##
                dmc.Modal(
                    id='chart-settings-modal',
                    centered=True,
                    children=[
                        html.H2('Change in Time to First Payment (TFP, Annual)', style={'marginBottom': '0.05em', 'marginTop': '0'}),
                        html.P('Chart Options', className='text-muted'),
                        html.Hr(style={'margin': '0.5rem 0'}),

                        ## Fiscal Year Range Selection ##
                        dmc.YearPickerInput(
                            type='range',
                            label='Select Fiscal Year Range',
                            placeholder='Select a range of Fiscal Years...',
                            leftSection=DashIconify(icon='clarity:calendar-line', width=16, height=16),
                            minDate=datetime(2016, 1, 1),
                            maxDate=datetime(2025, 1, 1),
                            value=[datetime(2016, 1, 1), datetime(2025, 1, 1)],
                            id='date-filter-chart-9',
                            style={'marginBottom': '1.5rem'},
                            clearable=False
                        ),

                        dmc.Button("Click to set options",
                                   fullWidth=True, 
                                   variant='filled', 
                                   leftSection=DashIconify(icon='clarity:check-line', width=24, height=24),
                                   color="rgb(32, 201, 151)",
                                   id='modal-filter-accept-button-9'
                        )

                    ],
                    styles={
                        'body': {'padding': '0 2.5rem 3rem 2.5rem'},
                        'header': {'paddingTop': '0', 'paddingBottom': '0'}
                    }
                )

            ]

            return return_array
        
        else:

            return no_update


    ## Callback for Button to open the Modal ##
    @app.callback(
    Output("chart-settings-modal", "opened"),
    Input("chart-settings-button-click", "n_clicks"),
    State("chart-settings-modal", "opened"),
    State("chart-settings-button-click", "disabled"),
    prevent_initial_call=True
    )
    
    def toggle_modal(n_clicks, opened, disabled):
        
        if disabled:

            return no_update
        
        else:

            return not opened


    
    ## Beginning Callbacks for Modals ##
    ## Created Pledges By Portfolio & Frequency ##
    @app.callback(

        Output('pledges-donor-graph-figure-2', 'figure'),
        Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
        Input('modal-filter-accept-button-2', 'n_clicks'),
        State('date-filter-chart-2', 'value'),
        State('portfolio-filter-chart-2', 'value'),
        prevent_initial_call=True,
        suppress_callback_exceptions=True)
    def update_filter_modal_2(n_clicks, fiscal_years, portfolios):

        ctx = callback_context

        if ('value' not in ctx.states_list[0].keys()) or ('value' not in ctx.states_list[1].keys()):

            return no_update, no_update
        
        print(ctx.states_list)
        
        years_selected = [ctx.states_list[0]['value'][0].split('-')[0], ctx.states_list[0]['value'][1].split('-')[0]]
        portfolios_selected = ctx.states_list[1]['value']

        return pledges_by_portfolio_frequency_true(years_selected[0], years_selected[1], portfolios_selected), f'''FY{years_selected[0]} - FY{years_selected[1]} (Subscription & One Time)'''
    

    ## Churned Pledges By Fiscal Year ##
    @app.callback(
            Output('pledges-donor-graph-figure-3', 'figure'),
            Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
            Input('modal-filter-accept-button-3', 'n_clicks'),
            State('date-filter-chart-3', 'value'),
            prevent_initial_call=True)
    def update_filter_modal_3(n_clicks, fiscal_years):

        ctx = callback_context

        if ('value' not in ctx.states_list[0].keys()):

            return no_update, no_update
        
        ## If no years are selected, default to 2018 - 2025 ##
        if ctx.states_list[0]['value'] == [] or (ctx.states_list[0]['value'][0] is None):

            subtitle = f'''FY2018 - FY2025 (Subscription Based Pledges)'''

            return generate_churned_pledges_by_fiscal_year(2018, 2025), subtitle
        
        ## If 1 year is selected only ##
        if (len(ctx.states_list[0]['value']) == 1) or (ctx.states_list[0]['value'][1] is None):

            first_year = ctx.states_list[0]['value'][0].split('-')[0]

            subtitle = f'''FY{first_year} - FY2025 (Subscription Based Pledges)'''

            return generate_churned_pledges_by_fiscal_year(first_year, 2026), subtitle
        
        ## Normal Conditions ##
        years_selected = [ctx.states_list[0]['value'][0].split('-')[0], ctx.states_list[0]['value'][1].split('-')[0]]

        subtitle = f'''FY{years_selected[0]} - FY{years_selected[1]} (Subscription Based Pledges)'''

        return generate_churned_pledges_by_fiscal_year(years_selected[0], years_selected[1]), subtitle
    

    ## Pledges Churned Without Any Payment ##
    @app.callback(
        
        Output('pledges-donor-graph-figure-4', 'figure'),
        Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
        Input('modal-filter-accept-button-4', 'n_clicks'),
        State('date-filter-chart-4', 'value'),
        prevent_initial_call=True)
    def update_filter_modal_4(n_clicks, fiscal_years):

        ctx = callback_context

        if ('value' not in ctx.states_list[0].keys()):

            return no_update, no_update
        
        ## If no years are selected, default to 2018 - 2025 ##
        if ctx.states_list[0]['value'] == [] or (ctx.states_list[0]['value'][0] is None):

            subtitle = f'''FY2018 - FY2025 (Subscription Based Pledges)'''

            return generate_churned_before_payment_graph(2018, 2025), subtitle
        
        ## If 1 year is selected only ##
        if (len(ctx.states_list[0]['value']) == 1) or (ctx.states_list[0]['value'][1] is None):

            first_year = ctx.states_list[0]['value'][0].split('-')[0]

            subtitle = f'''FY{first_year} - FY2025 (Subscription Based Pledges)'''

            return generate_churned_before_payment_graph(first_year, 2025), subtitle
        

        ## Normal Conditions ##
        years_selected = [ctx.states_list[0]['value'][0].split('-')[0], ctx.states_list[0]['value'][1].split('-')[0]]

        subtitle = f'''FY{years_selected[0]} - FY{years_selected[1]} (Subscription Based Pledges)'''

        return generate_churned_before_payment_graph(years_selected[0], years_selected[1]), subtitle
    
    ## Total Payments Recieved Annual (One-Time & Subscriptions) ##
    @app.callback(
            Output('pledges-donor-graph-figure-5', 'figure'),
            Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
            Input('modal-filter-accept-button-5', 'n_clicks'),
            State('date-filter-chart-5', 'value'),
            supress_ballback_exceptions=True,
            prevent_initial_call=True
            
    )
    def update_filter_modal_5(n_clicks, fiscal_years):

        ctx = callback_context

        if ('value' not in ctx.states_list[0].keys()):

            return no_update, no_update
        
        ## If no years are selected, default to 2018 - 2025 ##
        if ctx.states_list[0]['value'] == [] or (ctx.states_list[0]['value'][0] is None):

            subtitle = f'''FY2018 - FY2025 (One-Time & Subscription Payments)'''

            return generate_money_moved_annual_graph(2018, 2025), subtitle
        
        ## If 1 year is selected only ##
        if (len(ctx.states_list[0]['value']) == 1) or (ctx.states_list[0]['value'][1] is None):

            first_year = ctx.states_list[0]['value'][0].split('-')[0]

            subtitle = f'''FY{first_year} - FY2025 (One-Time & Subscription Payments)'''

            return generate_money_moved_annual_graph(first_year, 2025), subtitle
        
        ## Normal Conditions ##
        years_selected = [ctx.states_list[0]['value'][0].split('-')[0], ctx.states_list[0]['value'][1].split('-')[0]]

        subtitle = f'''FY{years_selected[0]} - FY{years_selected[1]} (One-Time & Subscription Payments)'''

        return generate_money_moved_annual_graph(years_selected[0], years_selected[1]), subtitle
    

    ## Revenue Generated By All Pledges Monthly (One-Time & Subscription Payments) ##
    @app.callback(
            Output('pledges-donor-graph-figure-6', 'figure'),
            Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
            Input('modal-filter-accept-button-6', 'n_clicks'),
            State('date-filter-chart-6', 'value'),
            supress_ballback_exceptions=True,
            prevent_initial_call=True
            
    )
    def update_filter_modal_6(n_clicks, fiscal_years):

        ctx = callback_context

        if ('value' not in ctx.states_list[0].keys()):

            return no_update, no_update
        
        ## If no years are selected, default to 2018 - 2025 ##
        if ctx.states_list[0]['value'] == [] or (ctx.states_list[0]['value'][0] is None):

            subtitle = f'''FY2024 - FY2025 (One - Time & Subscription Payments)'''

            return generate_money_moved_monthly_graph(2024, 2025), subtitle
        
        ## If 1 year is selected only ##
        if (len(ctx.states_list[0]['value']) == 1) or (ctx.states_list[0]['value'][1] is None):

            first_year = ctx.states_list[0]['value'][0].split('-')[0]

            subtitle = f'''FY{first_year} - FY2025 (One-Time & Subscription Payments)'''

            return generate_money_moved_monthly_graph(first_year, 2025), subtitle
        
        ## Normal Conditions ##
        years_selected = [ctx.states_list[0]['value'][0].split('-')[0], ctx.states_list[0]['value'][1].split('-')[0]]

        subtitle = f'''FY{years_selected[0]} - FY{years_selected[1]} (One-Time & Subscription Payments)'''

        return generate_money_moved_monthly_graph(years_selected[0], years_selected[1]), subtitle

    ## Average Revenue Per Pledge Annual (One-Time & Subscriptions) ##
    @app.callback(
            Output('pledges-donor-graph-figure-7', 'figure'),
            Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
            Input('modal-filter-accept-button-7', 'n_clicks'),
            State('date-filter-chart-7', 'value'),
            supress_ballback_exceptions=True,
            prevent_initial_call=True
            
    )
    def update_filter_modal_7(n_clicks, fiscal_years):

        ctx = callback_context

        if ('value' not in ctx.states_list[0].keys()):

            return no_update, no_update
        
        ## If no years are selected, default to 2018 - 2025 ##
        if ctx.states_list[0]['value'] == [] or (ctx.states_list[0]['value'][0] is None):

            subtitle = f'''FY2018 - FY2025 (One-Time & Subscription Payments)'''

            return generate_arpp_annual_graph(2018, 2025), subtitle
        
        ## If 1 year is selected only ##
        if (len(ctx.states_list[0]['value']) == 1) or (ctx.states_list[0]['value'][1] is None):

            first_year = ctx.states_list[0]['value'][0].split('-')[0]

            subtitle = f'''FY{first_year} - FY2025 (One-Time & Subscription Payments)'''

            return generate_arpp_annual_graph(first_year, 2025), subtitle
        
        ## Normal Conditions ##
        years_selected = [ctx.states_list[0]['value'][0].split('-')[0], ctx.states_list[0]['value'][1].split('-')[0]]

        subtitle = f'''FY{years_selected[0]} - FY{years_selected[1]} (One-Time & Subscription Payments)'''

        return generate_arpp_annual_graph(years_selected[0], years_selected[1]), subtitle
    


    ## Average Revenue Per Pledge Monthly Subscription Only ##
    @app.callback(
            Output('pledges-donor-graph-figure-8', 'figure'),
            Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
            Input('modal-filter-accept-button-8', 'n_clicks'),
            State('date-filter-chart-8', 'value'),
            State('payment-filter-chart-8', 'value'),
            supress_ballback_exceptions=True,
            prevent_initial_call=True)


    def update_filter_modal_8(n_clicks, fiscal_years, payment_platforms):

        ctx = callback_context

        if ('value' not in ctx.states_list[0].keys()):

            return no_update, no_update
        
        ## Payments do not need to be altered in if else ladder ##
        payments_selected = ctx.states_list[1]['value']
        
        ## If no years are selected, default to 2018 - 2025 ##
        if ctx.states_list[0]['value'] == [] or (ctx.states_list[0]['value'][0] is None):

            subtitle = f'''FY2024 - FY2025 (Subscription Payments Only)'''

            return generate_arpp_monthly_graph(2024, 2025, payments_selected), subtitle
        
        ## If 1 year is selected only ##
        if (len(ctx.states_list[0]['value']) == 1) or (ctx.states_list[0]['value'][1] is None):

            first_year = ctx.states_list[0]['value'][0].split('-')[0]

            subtitle = f'''FY{first_year} - FY2025 (Subscription Payments Only)'''

            return generate_arpp_monthly_graph(first_year, 2025, payments_selected), subtitle
        
        ## Normal Conditions ##
        years_selected = [ctx.states_list[0]['value'][0].split('-')[0], ctx.states_list[0]['value'][1].split('-')[0]]

        subtitle = f'''FY{years_selected[0]} - FY{years_selected[1]} (Subscription Payments Only)'''

        return generate_arpp_monthly_graph(years_selected[0], years_selected[1], payments_selected), subtitle
    

    ##### Section for Time to First Payment Annual #####
    @app.callback(
            Output('pledges-donor-graph-figure-9', 'figure'),
            Output(component_id='pledges-donor-graph-subtitle', component_property='children', allow_duplicate=True),
            Input('modal-filter-accept-button-9', 'n_clicks'),
            State('date-filter-chart-9', 'value'),
            supress_ballback_exceptions=True,
            prevent_initial_call=True
            
    )
    def update_filter_modal_9(n_clicks, fiscal_years):

        ctx = callback_context

        if ('value' not in ctx.states_list[0].keys()):

            return no_update, no_update
        
        ## If no years are selected, default to 2018 - 2025 ##
        if ctx.states_list[0]['value'] == [] or (ctx.states_list[0]['value'][0] is None):

            subtitle = f'''FY2016 - FY2025 (Subscription Payments Only)'''

            return generate_ttv_by_fiscal_year(2016, 2025), subtitle
        
        ## If 1 year is selected only ##
        if (len(ctx.states_list[0]['value']) == 1) or (ctx.states_list[0]['value'][1] is None):

            first_year = ctx.states_list[0]['value'][0].split('-')[0]

            subtitle = f'''FY{first_year} - FY2025 (Subscription Payments Only)'''

            return generate_ttv_by_fiscal_year(first_year, 2025), subtitle
        
        ## Normal Conditions ##
        years_selected = [ctx.states_list[0]['value'][0].split('-')[0], ctx.states_list[0]['value'][1].split('-')[0]]

        subtitle = f'''FY{years_selected[0]} - FY{years_selected[1]} (Subscription Payments Only)'''

        return generate_ttv_by_fiscal_year(years_selected[0], years_selected[1]), subtitle


    ###### Section for selecting and generating cards for analytics ######
    @app.callback(Output('keys-objs-head-title', 'children'),
                  Output('display-cards-group-main', 'children'),
                  navigation_inputs,
                  prevent_initial_call=True)
    def update_app_cards(*args):

        navigation_ids_intermediate = navigation_ids

        print(navigation_ids_intermediate)

        ctx = callback_context
        ctx_id_activated = ctx.triggered[0]['prop_id'].split('.')[0]

        if ctx_id_activated in navigation_ids_intermediate[0:4]:

            print(ctx_id_activated)

            title, cards = generate_cards_goals_pledges_churn(2025)

            return title, cards
        
        elif ctx_id_activated in navigation_ids_intermediate[4:9]:

            print(ctx_id_activated)

            title, cards = generate_cards_goals_money_metrics(2025)

            return title, cards
    



