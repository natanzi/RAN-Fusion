# app.py
from dash import html
from app_instance import app
from layouts import create_login_modal, create_sidebar, create_main_content
from flask import Flask
from callbacks import register_callbacks
from layouts import create_login_modal, create_main_content, create_sidebar
register_callbacks(app)

# Ensure all these functions return valid Dash components
app.layout = html.Div([
    create_login_modal(),
    create_sidebar(),
    create_main_content(),
    html.Div(id='main-content', style={'display': 'none'})
], className='body-background')

if __name__ == '__main__':
    app.run_server(debug=True)
