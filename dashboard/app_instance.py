# app_instance.py
# app_instance.py
import dash
import dash_bootstrap_components as dbc
from flask import Flask

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


