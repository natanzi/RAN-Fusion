# app_instance.py
# app_instance.py
from dash import Dash
import dash_bootstrap_components as dbc
from flask import Flask

server = Flask(__name__)  # Flask server instance
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Dash app instance

