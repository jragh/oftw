import polars as pl

from dash import dcc, html
import dash_mantine_components as dbc
import plotly_express as px
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import os

def navbar_selection_html():

    return_array = [

        html.H2('OFTW Performance Dashboard'),
        html.H4('Main Navigation'),
        html.Span(html.P('Key Goals & Objectives - Donors & Pledges', style={'margin': '0.4em 0.75em'}), className = 'style-pill-navbar'),

        html.Div([

            ## Havigation Header for Objectives abd Key Results 
            html.Span([

                DashIconify(icon='clarity:check-circle-solid', height=24, width=24),
                html.P('Objectives & Key Results'),
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

            )

        ], style={'margin': '2.5rem 0 0.625rem 0', 'padding':'0 1rem'})

    ]

    return return_array