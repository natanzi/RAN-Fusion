# app.py
# app.py
from dash import html, dcc
from app_instance import app
from layouts import create_login_modal, main_layout
from callbacks import register_callbacks

app.layout = html.Div([
    create_login_modal(),
    html.Div(id='main-layout-container', style={'display': 'none'}),  # Initially hidden
    dcc.Store(id='auth-store')  # If needed for state management
], className='body-background')

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)



