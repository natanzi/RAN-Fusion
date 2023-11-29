# app.py
# app.py
import dash 
import dash_bootstrap_components as dbc
from layouts import create_login_modal, main_layout
from callbacks import register_callbacks
from app_instance import app

# Import html  
import html

app = dash.Dash(__name__)

app.layout = html.Div([
    create_login_modal(),
    html.Div(id='main-content', style={'display': 'none'}), 
])

register_callbacks(app)

if __name__ == '__main__':
   app.run_server(debug=True)



