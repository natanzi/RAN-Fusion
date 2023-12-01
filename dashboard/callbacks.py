# callbacks.py
from dash import Output, Input, State, html
from app_instance import app

def check_credentials(username, password):
    return username == 'admin' and password == 'admin'

@app.callback(
    [Output('login-modal', 'is_open'), Output('main-content', 'style'), Output('login-error-message', 'children')],
    [Input('login-button', 'n_clicks')],
    [State('username-input', 'value'), State('password-input', 'value')]
)
def combined_callback(n_clicks_login, username, password):
    if n_clicks_login:
        if check_credentials(username, password):
            # Set visibility for main content and hide modal
            return False, {'display': 'block'}, ""
        else:
            # Display error and keep modal open
            return True, {'display': 'none'}, "Incorrect credentials"
    # Default state when the page loads
    return True, {'display': 'none'}, ""

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
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
    return html.Div()


