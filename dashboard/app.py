# app.py
from dash import html, dcc
from app_instance import app  # Import the Dash app instance
from layouts import create_login_modal, main_layout
from callbacks import register_callbacks

app.layout = html.Div([
    create_login_modal(),
    main_layout(),  # Initially hidden
    dcc.Store(id='auth-store')
], className='body-background')

register_callbacks(app)  # Register the callbacks from callbacks.py

if __name__ == '__main__':
    app.run_server(debug=True)

