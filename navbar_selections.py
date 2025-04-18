import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import os

def navbar_selection_html():

    return_array = [

        html.Span([
            html.H2('OFTW Metrics Chart Selection', style={'margin': '0.5rem 0 0.4rem 0'}),
            html.H5('Select an item below to display chart and KPI cards...', style={'margin': '0.4rem 0'}),
            html.Hr(style={'margin': '0.5em 1.5em 0.5em 1.5em'}),
            html.Span([

                DashIconify(icon='clarity:bar-chart-solid', height=36, width=36, style={'margin': '0 0.25em'}),
                DashIconify(icon='clarity:line-chart-solid', height=36, width=36, style={'margin': '0 0.25em'}),
                DashIconify(icon='clarity:coin-bag-solid', height=36, width=36, style={'margin': '0 0.25em'}),
                DashIconify(icon='clarity:users-solid', height=36, width=36, style={'margin': '0 0.25em'})

            ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'})],
            style={'display': 'flex', 'justify-content': 'center', 'flex-direction': 'column', 'text-align': 'center', 'color': 'ivory', 'background-color': '#0e4984', 'border-radius': '10px', 'margin': '1em', 'padding': '1em'}
        ),

        html.Div([

            ## Havigation Header for Objectives abd Key Results 
            html.Span([

                DashIconify(icon='clarity:check-circle-solid', height=24, width=24, style={'marginRight': '0.5rem'}),
                html.P('Objectives & Key Results', style={'fontSize': '1.1em', 'fontWeight': '500'}),
                dmc.Divider(variant='solid', size='xs', color='#dee2e6', orientation='horizontal', style={'flex': '1', 'margin-left': '0.75rem'})

            ], className='navigation-header-text'),

            ## Navigation Options for Objectives and Key Results
            dmc.NavLink(

                label='Created Pledges By Pledge Type',
                variant='filled',
                active=True,
                leftSection=DashIconify(icon='clarity:bar-chart-solid', height=24, width=24),
                className='navlink-option',
                color='#6495ed',
                id='navbar-okr-1',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                },
                style={'marginTop': '0'}

            ),

            dmc.NavLink(

                label='Created Pledges By Portfolio & Frequency',
                variant='filled',
                leftSection=DashIconify(icon='clarity:bar-chart-solid', height=24, width=24),
                className='navlink-option',
                color='#6495ed',
                id='navbar-okr-2',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                }

            ),

            dmc.NavLink(

                label='Change in Active Pledges By Fiscal Year',
                variant='filled',
                leftSection=DashIconify(icon='clarity:bar-chart-solid', height=24, width=24),
                className='navlink-option',
                color='#6495ed',
                id='navbar-okr-3',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                }

            ),

            dmc.NavLink(

                label='Churned Pledges Before Payment By Fiscal Year',
                variant='filled',
                leftSection=DashIconify(icon='clarity:bar-chart-solid', height=24, width=24),
                className='navlink-option',
                color='#6495ed',
                id='navbar-okr-4',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                }

            ),



        ], style={'margin': '1.5rem 0 0.625rem 0', 'padding':'0 1rem'}),

        html.Div([

            ## Revenue Metrics Header ##
            html.Span([

                DashIconify(icon='clarity:dollar-bill-solid', height=24, width=24, style={'marginRight': '0.5rem'}),
                html.P('Revenue Metrics', style={'fontSize': '1.1em', 'fontWeight': '500'}),
                dmc.Divider(variant='solid', size='xs', color='#dee2e6', orientation='horizontal', style={'flex': '1', 'margin-left': '0.75rem'})

            ], className='navigation-header-text-two'),


            dmc.NavLink(

                label = 'Total Payments Recieved (Annual)',
                variant='filled',
                className='navlink-option',
                leftSection=DashIconify(icon='clarity:bar-chart-solid', height=24, width=24),
                color='#6495ed',
                id='navbar-mmg-1',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                }

            ),

            dmc.NavLink(

                label = 'Total Payments Recieved (Monthly)',
                variant='filled',
                className='navlink-option',
                leftSection=DashIconify(icon='clarity:line-chart-solid', height=24, width=24),
                color='#6495ed',
                id='navbar-mmg-2',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                }

            ),

            dmc.NavLink(

                label = 'Average Revenue Per Pledge (Annual)',
                variant='filled',
                className='navlink-option',
                leftSection=DashIconify(icon='clarity:bar-chart-solid', height=24, width=24),
                color='#6495ed',
                id='navbar-mmg-3',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                }

            ),

            dmc.NavLink(

                label = 'Average Revenue Per Pledge (Monthly)',
                variant='filled',
                className='navlink-option',
                leftSection=DashIconify(icon='clarity:bar-chart-solid', height=24, width=24),
                color='#6495ed',
                id='navbar-mmg-4',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                }

            ),




        ], style={'margin': '1.5rem 0 0.625rem 0', 'padding':'0 1rem'}),



        html.Div([

            ## Revenue Metrics Header ##
            html.Span([

                DashIconify(icon='clarity:users-solid', height=24, width=24, style={'marginRight': '0.5rem'}),
                html.P('Efficiency Metrics', style={'fontSize': '1.1em', 'fontWeight': '500'}),
                dmc.Divider(variant='solid', size='xs', color='#dee2e6', orientation='horizontal', style={'flex': '1', 'margin-left': '0.75rem'})

            ], className='navigation-header-text-two'),


            dmc.NavLink(

                label = 'Time to First Payment (TFP, Annual)',
                variant='filled',
                className='navlink-option',
                leftSection=DashIconify(icon='clarity:bar-chart-solid', height=24, width=24),
                color='#6495ed',
                id='navbar-msc-1',
                styles={
                    'label': {'fontSize': '.75rem'},
                    'root': {'borderRadius': '10px'}
                }

            )

        ], style={'margin': '1.5rem 0 0.625rem 0', 'padding':'0 1rem'})

    ]

    return return_array