# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import geopandas as gpd
from dash.dependencies import Input, Output

filename = r'D:\GeospacialDBs_Data\countries.geo.json'
with open(filename, 'r') as file:
    df_countries = gpd.read_file(file)

with open('D:\GeospacialDBs_Data\countries.geo.json') as response:
    countries = json.load(response)

df_apple = pd.read_csv(r'D:\GeospacialDBs_Data\AppleMobilityData_reshaped.csv', header=0)

df_apple_geo = df_apple.join(df_countries.set_index('name'), on='region')
max_percentage = df_apple_geo["percentage"].max()

cases = pd.read_csv(r"D:\GeospacialDBs_Data\WHO-COVID-19-global-data.csv",header=0)
df_new_cases = cases.join(df_countries.set_index('name'), on='Country')
max_cases = df_new_cases["New_cases"].max()

app = dash.Dash(__name__)

colors = {
    'background': '#FFFFFF',
    'text': '#0A0A0A'
}

slider_values = df_apple["timestamp"].unique()
slider_labels = [(i, slider_values[i]) for i in range(len(slider_values)) if i % 20 == 0]


@app.callback(Output('world_graph', 'figure'),
              [Input('dropdown', 'value'), Input('slider', 'value')])
def update_cloropleth(selected_dropdown_value, selected_slider_value):
    df_sub = df_apple_geo[df_apple_geo['timestamp'] == slider_values[selected_slider_value]]
    df_sub = df_sub[df_sub['transportation_type'] == selected_dropdown_value]
    fig = px.choropleth(df_sub,
                        geojson=countries,
                        locations="id",
                        color="percentage",
                        projection="mercator",
                        range_color=(0, 200),
                        color_continuous_scale="RdBu")#,
                        #animation_frame="timestamp")
    #fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'])
    return fig


@app.callback(Output('cases_graph', 'figure'),
              [Input('slider', 'value')])
def update_cases(selected_slider_value):
    df_sub_new_cases = df_new_cases[df_new_cases['Date_reported'] == slider_values[selected_slider_value]]
    fig = px.choropleth(df_sub_new_cases,
                        geojson=countries,
                        locations="id",
                        color="New_cases",
                        projection="mercator",
                        range_color=(0, max_cases),
                        color_continuous_scale="Reds")#,
                        #animation_frame="timestamp")
    #fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'])
    return fig


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='Covid-19 Cases and Traffic data app', style={
            'textAlign': 'center',
            'color': colors['text']}),
    html.Div(className='four columns div-user-controls', children=[
        html.Label('New Cases per Day', style={'textAlign': 'center', 'color': colors['text']}),
        dcc.Graph(id='cases_graph')], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'}),
    html.Div(className='eight columns div-for-charts bg-grey', children=[
        html.Label('Select Graph Type', style={'textAlign': 'center', 'color': colors['text']}),
        dcc.Dropdown(
            options=[
                {'label': 'Driving', 'value': 'driving'},
                {'label': 'Walking', 'value': 'walking'},
                {'label': 'Transit', 'value': 'transit'}
            ],
            value='driving', style={
                'textAlign': 'center',
                'color': colors['text']},
            id='dropdown'
        ),
        dcc.Graph(id='world_graph')], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'}),
    html.Label('Date Slider', style={'textAlign': 'center', 'color': colors['text']}),
    dcc.Slider(
        min=0,
        max=(len(slider_values)-1),
        marks={i: '{}'.format(x) for i, x in slider_labels},
        value=0,
        id='slider'
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
