# Define Dash layout components (optional)
# layouts.py

import dash_bootstrap_components as dbc
from dash import html, dcc

def create_login_modal():
    return dbc.Modal(
        [
            dbc.ModalBody(
                html.Div([
                    html.H2("RANFusion", className="text-center"),
                    html.P("", className="text-center"),
                    dbc.Input(id="username-input", placeholder="Username", type="text", className="mt-4"),
                    dbc.Input(id="password-input", placeholder="Password", type="password", className="mt-4"),
                    dbc.Button("Login", id="login-button", className="btn-block mt-4", n_clicks=0),
                ], className="login-modal-body")
            ),
        ],
        id="login-modal",
        is_open=True,  # Set to True to have the modal open by default
        centered=True,
        size="sm"
    )
def main_layout():
    return html.Div(id='main-layout', children=[
        dbc.Tabs([
            dbc.Tab(label="UE Level Report", tab_id="tab-ue"),
            dbc.Tab(label="Cell Level Report", tab_id="tab-cell"),
            dbc.Tab(label="gNodeB Level Report", tab_id="tab-gnodb"),
            dbc.Tab(label="Network Level Report", tab_id="tab-network"),
        ], id="tabs", active_tab="tab-ue"),
        html.Div(id="tab-content", children=[
            html.Iframe(
                id='map',
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2948.336261614217!2d-71.80329368420207!3d42.26259337919353!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89e4065daf44c81d%3A0x450d8f1f1330361!2sWorcester%2C%20MA%2C%20USA!5e0!3m2!1sen!2s!4v1631024739346",
                style={"height": "100vh", "width": "100%"}
            ),
        ]),
    ])

# Note: You still need to define the `*_level_report_layout` functions
