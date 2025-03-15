import polars as pl
import plotly_express as px
from dash import html, dcc, Input, Output, State, Dash, _dash_renderer, get_asset_url
import dash_mantine_components as dmc

from flask import Flask, redirect

from new_signups_pledges_goals import generateNewSignupsPledgesGoals

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

        dmc.AppShellMain(

            dmc.Container(generateNewSignupsPledgesGoals(2025),className='objs-key-results-header')
        )

    ], padding='sm',
    header={'height': 75, 'width': 100, }

)

app.layout = dmc.MantineProvider(layout)



if __name__ == "__main__":
    app.run(debug=True)