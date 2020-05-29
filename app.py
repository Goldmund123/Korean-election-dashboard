# Import required libraries
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import layout
from graph import geo_plots, plots
import pandas as pd
from config import config
from flask import Flask
from flask_caching import Cache

server = Flask(__name__)
server.secret_key ='test'
#server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(name = __name__, server = server)

cache = Cache(app.server, config={
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ['REDISCLOUD_URL']
})

variable_type = config.variable_type

metro_province = config.metro_province

# Create app layout
app.layout = layout.dashboard1

@app.callback(
    Output('metropolitan', 'options'),
    [Input('province', 'value')])
def select_provinces_options(selected):
    return [{'label': i, 'value': i} for i in metro_province[selected]]

@app.callback(
    Output('metropolitan', 'value'),
    [Input('metropolitan', 'options')])
def select_provinces_values(available_options):
    return available_options[0]['value']

@app.callback(
    Output('variable', 'options'),
    [Input('variable_type_selector', 'value')])
def select_variable_options(selected):
    if selected in ['democrate', 'unification']:
        return [{'label': ' '.join(i.split('_')[1:]).capitalize(), 'value': i} for i in variable_type[selected]]
    else:
        return [{'label': ' '.join(i.capitalize().split('_')), 'value': i} for i in variable_type[selected]]

@app.callback(
    Output('variable', 'value'),
    [Input('variable', 'options')])
def select_variable_values(available_options):
    return available_options[0]['value']

#graphs
@app.callback(
    Output('mapbox_graph', 'figure'),
    [Input('province', 'value'),
     Input('metropolitan', 'value'),
     Input('variable', 'value'),
    ])
@cache.memoize()
def mapbox_callback(province, metropolitan, target):
    return geo_plots.update_geo_graph(province, metropolitan, target)

@app.callback(
    [Output('democrate_text', 'children'),
     Output('unification_text', 'children'),
     Output('justice_text', 'children'),
     Output('no_party_text', 'children')],
    [Input('province', 'value'),
     Input('metropolitan', 'value'),
    ])
def panel_callback(province, metropolitan):
    return plots.update_panel(province, metropolitan)

@app.callback(
    Output('bar_graph', 'figure'),
    [Input('province', 'value'),
     Input('metropolitan', 'value'),
     Input('variable', 'value'),
     Input('highlow', 'value'),
    ])
@cache.memoize()
def bar_callback(province, metropolitan, variable, option):
    if option == 'highest':
        return plots.update_bar_top(province, metropolitan, variable)
    else:
        return plots.update_bar_bottom(province, metropolitan, variable)

@app.callback(
    dash.dependencies.Output('radar_graph', 'figure'),
    [dash.dependencies.Input('mapbox_graph', 'clickData')])
def radar_callback(clickData):
    metropolitan = clickData['points'][0]['customdata'][0]
    district = clickData['points'][0]['customdata'][1]
    return plots.update_radar(metropolitan, district)

@app.callback(
    Output('scatter_graph', 'figure'),
    [
     Input('scatter_variables', 'value'),
    ])
@cache.memoize()
def scatter_callback(variables):
    return plots.update_scatter(variables[0], variables[1])

@app.callback(
    [Output('histogram1', 'figure'),
    Output('histogram2', 'figure')],
    [
     Input('scatter_variables', 'value')
    ])
@cache.memoize()
def hist_callback(variables):
    return plots.update_histograms(variables[0], variables[1])

# Main
if __name__ == "__main__":
    app.run_server(port=8050, debug=False)