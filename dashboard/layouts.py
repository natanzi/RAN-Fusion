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
    return html.Div([
        dbc.Row([
            dbc.Col(html.Iframe(
                id='map',
                src="https://www.google.com/maps/embed?pb=...",
                style={"height": "100vh", "width": "100%"}
            ), width=12),  # Full width for map
        ]),
        dbc.Row([  # Row for tabs at the bottom
            dbc.Col(dbc.Tabs(id="tabs", children=[
                dbc.Tab(label="UE Level Report", tab_id="tab-ue"),
                dbc.Tab(label="Cell Level Report", tab_id="tab-cell"),
                dbc.Tab(label="gNodeB Level Report", tab_id="tab-gnodb"),
                dbc.Tab(label="Network Level Report", tab_id="tab-network"),
            ], active_tab="tab-ue"), width=12)
        ]),
        html.Div(id="tab-content")  # Content for selected tab
    ])
# Placeholder functions for each report's content
def ue_level_report_layout():
    return html.Div([
        html.H3("UE Level Report"),
        # Add more components for UE Level Report here
    ])

def cell_level_report_layout():
    return html.Div([
        html.H3("Cell Level Report"),
        # Add more components for Cell Level Report here
    ])

def gnodb_level_report_layout():
    return html.Div([
        html.H3("gNodeB Level Report"),
        # Add more components for gNodeB Level Report here
    ])

def network_level_report_layout():
    return html.Div([
        html.H3("Network Level Report"),
        # Add more components for Network Level Report here
    ])


# Note: You still need to define the `*_level_report_layout` functions
