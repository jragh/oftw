import polars as pl
import plotly_express as px
from dash import html, dcc, Input, Output, State, Dash, _dash_renderer, get_asset_url, no_update
import dash_mantine_components as dmc

from flask import Flask, redirect

from new_signups_pledges_goals import generateNewSignupsPledgesGoals
from callbacks import pledges_donor_page_graph_selector

_dash_renderer._set_react_version("18.2.0")

app = Dash(external_stylesheets=dmc.styles.ALL)



layout = dmc.AppShell(

    [

        dmc.AppShellHeader(

            dmc.Group([

                html.Img(src=get_asset_url('OFTW-Secondary-Logo-RGB-White-4k.png'), style={'maxHeight': '3.5rem', 'background': 'cornflowerblue'}),

                html.H2('Hello World To My New App!')



            ],
            h='100%', px='lg')

        ),

        dmc.AppShellNavbar(

            id='main-navbar',
            children=[

                html.H2('OFTW Performance Dashboard'),
                html.H4('Main Navigation'),
                html.Span(html.P('Key Goals & Objectives - Donors & Pledges', style={'margin': '0.4em 0.75em'}), className = 'style-pill-navbar')

            ]

        ),

        dmc.AppShellMain(

            dmc.Container(generateNewSignupsPledgesGoals(2025),className='objs-key-results-header')
        )

    ], padding='xs',
    header={'height': 75, 'width': 100},
    navbar={
        "width": 300,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    }

)

app.layout = dmc.MantineProvider(layout)
pledges_donor_page_graph_selector(app)


if __name__ == "__main__":
    app.run(debug=True)