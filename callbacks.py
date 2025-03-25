from dash.dependencies import Output, Input, State

from dash import no_update, dcc

from pledges_by_type_graph import pledges_by_type_graph
from pledges_by_portfolio_frequency_graph import pledges_by_portfolio_frequency_true

def pledges_donor_page_graph_selector(app):

    @app.callback(Output(component_id='pledges-donor-graph-title', component_property='children'),
                  Output(component_id='pledges-donor-graph-subtitle', component_property='children'),
                  Output(component_id='pledges-donor-graph-description', component_property='children'),
                  Output(component_id='pledges-donor-graph-figure-span', component_property='children'),
                  [Input(component_id='pledges-donors-graph-selection', component_property='value')],
                  prevent_initial_call=True)
    def update_pledges_donor_page_graph_selector(selected_graph):

        if selected_graph.strip() == '' or selected_graph is None:

            return no_update, no_update, no_update, no_update, no_update
        
        ## Graph 1
        elif selected_graph == 'Created Pledges By Pledge Type':

            description = '''Displays the number of Pledge sign ups based on OFTW's financial calendar (FY starts in July) on a quarterly basis.
                       Pledges are split into One-Time and Subscription (Ongoing, Annual, Monthly, etc.)
                       Focuses on when pledge was signed up, regardless if pledge is currently cancelled / churned.'''

            return 'Created Pledges By Pledge Type', 'Subscription & One-Time', description, dcc.Graph(style={'height': '34vh'}, figure=pledges_by_type_graph(), id='pledges-donor-graph-figure')
        
        ## Graph 2
        elif selected_graph == 'Created Pledges By Portfolio & Frequency':

            ## Hardcoded Top 8 portfolios, Maybe make this dynamic instead? ##
            starting_portfolio_list = [

                'OFTW Top Picks'
                ,'Entire OFTW Portfolio'
                ,'Custom Portfolio'
                ,'OFTW Top Pick: Against Malaria Foundation'
                ,'GiveWell (Maximum Impact Fund)'
                ,'OFTW Top Pick: GiveDirectly'
                ,'Auswahl durch Effektiv Spenden'
                ,'New Incentives'

            ]

            description = '''Displays the total number of pledges signed up by portfolio in the specified time period.
            This includes All pledges whether they are active or churned, and frequency includes subscription based and One - Time pledges.
            Use the Year Selection to choose fiscal year ranges, and the portfolio selector to choose portfolios.'''

            subtitle = 'FY2014 - FY2025 (Subscription & One Time)'

            return 'Created Pledges By Portfolio & Frequency', subtitle, description, dcc.Graph(style={'height': '34vh'}, figure=pledges_by_portfolio_frequency_true(2014, 2025, starting_portfolio_list), id='pledges-donor-graph-figure-2')