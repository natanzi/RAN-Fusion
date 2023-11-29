# callbacks.py
from dash import Output, Input , State
from app_instance import app
from layouts import main_layout

def toggle_layout(n_clicks, username, password):
    if n_clicks and username == 'admin' and password == 'admin':
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
     [Output('login-modal', 'is_open'),  
      Output('main-content', 'style')],
     [Input('login-button', 'n_clicks')],
     [State('username', 'value'),
      State('password', 'value')]
)
def toggle_modal(n_clicks, username, password):
    if n_clicks and check_credentials(username, password):
        return False, {} # Close modal, display tabs
    return True, {'display': 'none'} 

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
    return html.Div()  # Default return if no tab is selected


    return html.Div()

