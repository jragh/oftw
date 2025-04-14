import polars as pl
import plotly_express as px
from dash import html, dcc, Input, Output, State, Dash, _dash_renderer, get_asset_url, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from flask import Flask, redirect

from new_signups_pledges_goals import generateNewSignupsPledgesGoals
from callbacks import pledges_donor_page_graph_selector
from navbar_selections import navbar_selection_html

_dash_renderer._set_react_version("18.2.0")

server = Flask(__name__)

app = Dash(__name__, external_stylesheets=dmc.styles.ALL, server=server)
app.config.suppress_callback_exceptions=True



layout = dmc.AppShell(

    [

        dmc.AppShellHeader(

            dmc.Group([

                html.Span([

                    html.Img(src=get_asset_url('OFTW-Secondary-Logo-RGB-White-4k.png'), style={'maxHeight': '3.5rem', 'background': 'cornflowerblue', 'align-self': 'center', 'margin-right': '1rem'}),
                    html.H2('OFTW Merics Dashboard', style={'color': 'ivory'})

                ],style={'margin': '0', 'padding': '0', 'display': 'flex', 'flex-direction': 'row'}),

                html.Span([dmc.Burger(id='navigation-burger',
                           size='sm',
                           hiddenFrom='sm',
                           opened=False,
                           color="rgb(255, 255, 240)")], style={'margin': '0', 'padding': '0', 'display': 'flex', 'flex-direction': 'row'})

            ],
            px='lg', style={"height": 'fit-content', 'justify-content': 'space-between'}),
            style={'background-color': '#1971c2', "height": 'fit-content', 'z-index': '1000'}

        ),

        dmc.AppShellNavbar(

            id='main-navbar',
            children=dmc.ScrollArea(navbar_selection_html())

        ),

        dmc.AppShellMain(

            dmc.Container(generateNewSignupsPledgesGoals(2025),className='objs-key-results-header'),
            style={'background-color': '#fafafa'}
        ),

        dmc.AppShellAside(children=[])

    ], padding='0',w='100%',
    header={'height': 75, 'width': 100},
    navbar={
        "width": 325,
        "breakpoint": "sm",
        "collapsed": {"mobile": True, "desktop": False},
    },
    aside={'collapsed': {"mobile": True, "desktop": True}, 'width': '0'},
    id='appshell'

)

app.layout = dmc.MantineProvider(layout)
pledges_donor_page_graph_selector(app)

@app.callback(
    Output("appshell", "navbar"),
    Input("navigation-burger", "opened"),
    State("appshell", "navbar"),
)
def toggle_navbar(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened, "desktop": False}
    return navbar


if __name__ == "__main__":
    app.run(debug=True)