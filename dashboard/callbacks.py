# callbacks.py
import html
from dash import Output, Input, State, dcc
from app_instance import app  # Import the Dash app instance
from layouts import ue_level_report_layout, cell_level_report_layout, gnodb_level_report_layout, network_level_report_layout
from layouts import main_layout
def check_credentials(username, password):
    return username == "admin" and password == "admin"


def register_callbacks(app):
    @app.callback(
        Output('login-modal', 'is_open'),
        Output('main-layout-container', 'style'),  # Update the style instead of children
        [Input("login-button", "n_clicks")],
        [State("username-input", "value"), State("password-input", "value")]
    )
    def toggle_modal(n_clicks, username, password):
        if n_clicks and check_credentials(username, password):
            return False, {}  # On successful login, close modal and display main layout
        return True, {'display': 'none'}  # Keep hidden initially or on failed loginge loads

@app.callback(
        Output("tab-content", "children"),
        [Input("tabs", "active_tab")],
    )
def switch_tab(active_tab):
        if active_tab == "tab-ue":
            return ue_level_report_layout()
        elif active_tab == "tab-cell":
            return cell_level_report_layout()
        elif active_tab == "tab-gnodb":
            return gnodb_level_report_layout()
        elif active_tab == "tab-network":
            return network_level_report_layout()
        return html.Div()  # Default return if no tab is selected</selectedCode>











