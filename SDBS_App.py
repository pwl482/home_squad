# -*- coding: utf-8 -*-

# visit http://127.0.0.1:8050/ in your web browser.
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import geopandas as gpd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from sqlalchemy import create_engine

with open('D:\GeospacialDBs_Data\countries.geo.json') as response:
    countries = json.load(response)

engine = create_engine("postgres://postgres:pw@localhost:5432/test_db")

app = dash.Dash(__name__)

colors = {
    'background': '#FFFFFF',
    'text': '#0A0A0A'
}

sql = ("SELECT a.date, c.country_region_code, c.country_region, a.new_cases, c.geometry "
        "FROM countries c, cases a " 
        "WHERE c.country_region_code = a.country_region_code")
df_cases = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")

max_cases = df_cases["new_cases"].max()

sql = ("SELECT a.date, c.country_region_code, c.geometry "
        "FROM countries c, apple a " 
        "WHERE c.country_region_code = a.country_region_code ")
df_dates = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")

slider_values = df_dates["date"].unique()
slider_labels = [(i, slider_values[i]) for i in range(len(slider_values)) if i % 20 == 0]

dropdown_colnames_dict = {
    "Driving % Change": "driving_percent_change_from_baseline",
    "Walking % Change": "walking_percent_change_from_baseline",
    "Retail % Change": "retail_and_recreation_percent_change_from_baseline",
    "Grocery % Change": "grocery_and_pharmacy_percent_change_from_baseline",
    "Parks % Change": "parks_percent_change_from_baseline",
    "Transit % Change": "transit_stations_percent_change_from_baseline",
    "Workplace % Change": "workplaces_percent_change_from_baseline",
    "Residential % Change": "residential_percent_change_from_baseline",
    "Flight Origin Count": "origin_count",
    "Flight Destination Count": "destination_count"
}

apple_vals = ["Driving % Change", "Walking % Change"]
google_vals = ["Retail % Change", "Grocery % Change", "Parks % Change", "Transit % Change", "Workplace % Change", "Residential % Change"]
flight_vals = ["Flight Origin Count", "Flight Destination Count"]

sql = ("SELECT c.country_region_code, c.country_region, c.geometry "
        "FROM countries c ")
df_countries = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")

countries_list = df_countries["country_region"].unique()
dict_list_countries = []
for i in countries_list:
    dict_list_countries.append({'label': i, 'value': i})

types_list = list(dropdown_colnames_dict.keys())
dict_list_type = []
for i in types_list:
    dict_list_type.append({'label': i, 'value': i})


@app.callback(Output('world_graph', 'figure'),
              [Input('dropdown', 'value'), Input('slider', 'value')])
def update_cloropleth(selected_dropdown_value, selected_slider_value):
    if selected_dropdown_value in apple_vals:
        sql = ("SELECT a.date, c.country_region_code, c.country_region, c.geometry, a." + dropdown_colnames_dict[selected_dropdown_value] + " "
                "FROM countries c, apple a "
                "WHERE c.country_region_code = a.country_region_code "
                "AND a.date='" + slider_values[selected_slider_value] + "'")
        df_sub = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")
        fig = px.choropleth(df_sub,
                            geojson=countries,
                            locations="country_region_code",
                            color=dropdown_colnames_dict[selected_dropdown_value],
                            projection="mercator",
                            range_color=(-200, 200),
                            color_continuous_scale="RdBu")
        fig.layout.coloraxis.colorbar.title = selected_dropdown_value
    elif selected_dropdown_value in google_vals:
        sql = ("SELECT a.date, c.country_region_code, c.country_region, c.geometry,  a." + dropdown_colnames_dict[selected_dropdown_value] + " "
                "FROM countries c, google a "
                "WHERE c.country_region_code = a.country_region_code "
                "AND a.date='" + slider_values[selected_slider_value] + "'")
        df_sub = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")
        fig = px.choropleth(df_sub,
                            geojson=countries,
                            locations="country_region_code",
                            color=dropdown_colnames_dict[selected_dropdown_value],
                            projection="mercator",
                            range_color=(-200, 200),
                            color_continuous_scale="RdBu")
        fig.layout.coloraxis.colorbar.title = selected_dropdown_value
    elif selected_dropdown_value in flight_vals:
        sql = ("SELECT a.date, c.country_region_code, c.country_region, c.geometry, a." + dropdown_colnames_dict[selected_dropdown_value] + " "
                "FROM countries c, flights a "
                "WHERE c.country_region_code = a.country_region_code "
                "AND a.date='" + slider_values[selected_slider_value] + "'")
        df_sub = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")
        fig = px.choropleth(df_sub,
                            geojson=countries,
                            locations="country_region_code",
                            color=dropdown_colnames_dict[selected_dropdown_value],
                            projection="mercator",
                            range_color=(0, 100),
                            color_continuous_scale="ice")
        fig.layout.coloraxis.colorbar.title = selected_dropdown_value
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'])
    return fig


@app.callback(Output('cases_graph', 'figure'),
              [Input('slider', 'value')])
def update_cases(selected_slider_value):
    sql = ("SELECT a.date, c.country_region_code, c.country_region, a.new_cases, c.geometry "
           "FROM countries c, cases a "
           "WHERE c.country_region_code = a.country_region_code "
           "AND a.date='" + slider_values[selected_slider_value] + "'")
    df_sub = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")
    fig = px.choropleth(df_sub,
                        geojson=countries,
                        locations="country_region_code",
                        color="new_cases",
                        projection="mercator",
                        range_color=(0, max_cases),
                        color_continuous_scale="Reds")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'],
                      legend_x=0.01, legend_y=1.3)
    return fig


@app.callback(Output('countries_graph', 'figure'),
              [Input('dropdown_countries', 'value'), Input('dropdown_types', 'value')])
def update_countries(selected_dropdown_values, selected_dropdown_values2):
    trace = []
    if not ((selected_dropdown_values is None) or (selected_dropdown_values2 is None)):
        for country in selected_dropdown_values:
            for type in selected_dropdown_values2:
                if type in apple_vals:
                    sql = ("SELECT a.date, c.country_region_code, c.country_region, c.geometry, a." + dropdown_colnames_dict[type] + " "
                            "FROM countries c, apple a "
                            "WHERE c.country_region_code = a.country_region_code "
                            "AND c.country_region='" + country + "'")
                    df_sub = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")
                    trace.append(go.Scatter(x=df_sub['date'],
                                            y=df_sub[dropdown_colnames_dict[type]],
                                            mode='lines',
                                            opacity=0.7,
                                            name=country + ":" + type,
                                            textposition='bottom center'))
                if type in google_vals:
                    sql = ("SELECT a.date, c.country_region_code, c.country_region, c.geometry, a." + dropdown_colnames_dict[type] + " "
                            "FROM countries c, google a "
                            "WHERE c.country_region_code = a.country_region_code "
                            "AND c.country_region='" + country + "'")
                    df_sub = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")
                    trace.append(go.Scatter(x=df_sub['date'],
                                            y=df_sub[dropdown_colnames_dict[type]],
                                            mode='lines',
                                            opacity=0.7,
                                            name=country + ":" + type,
                                            textposition='bottom center'))
                if type in flight_vals:
                    sql = ("SELECT a.date, c.country_region_code, c.country_region, c.geometry, a." + dropdown_colnames_dict[type] + " "
                            "FROM countries c, flights a "
                            "WHERE c.country_region_code = a.country_region_code "
                            "AND c.country_region='" + country + "'")
                    df_sub = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col="geometry")
                    trace.append(go.Scatter(x=df_sub['date'],
                                            y=df_sub[dropdown_colnames_dict[type]],
                                            mode='lines',
                                            opacity=0.7,
                                            name=country + ":" + type,
                                            textposition='bottom center'))
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    fig = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  font_size=10,
                  legend_x=0.01, legend_y=1.3
              )}
    return fig


@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))
def render_tab_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Label('Select Graph Type', style={'textAlign': 'center', 'color': colors['text']}),
            dcc.Dropdown(
                options=dict_list_type,
                value=types_list[0], style={
                    'textAlign': 'center',
                    'color': colors['text']},
                id='dropdown'
            ),
            dcc.Graph(id='world_graph')
            ])
    elif tab == 'tab-2':
        return html.Div([
            html.Div(className='country_selector', children=[
                    html.Label('Select Countries:', style={'textAlign': 'center', 'color': colors['text']}),
                    dcc.Dropdown(
                        options=dict_list_countries,
                        multi=True, style={
                            'textAlign': 'center',
                            'color': colors['text']},
                        id='dropdown_countries'
                    )], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'}),
            html.Div(className='class_selector', children=[
                html.Label('Select Type:', style={'textAlign': 'center', 'color': colors['text']}),
                dcc.Dropdown(
                    options=dict_list_type,
                    multi=True, style={
                        'textAlign': 'center',
                        'color': colors['text']},
                    id='dropdown_types'
                )], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'}),
            dcc.Graph(id='countries_graph')
        ])


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div(className='four columns div-user-controls', children=[
        html.H1(children='Covid-19 Cases and Traffic data app', style={
                'textAlign': 'center',
                'color': "white",
                'background': '#1abc9c',
                'font-size': '30px',
                'padding': '20px'}),
        html.Label('New Cases per Day:', style={'textAlign': 'center', 'color': colors['text']}),
        dcc.Graph(id='cases_graph')], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'}),
    html.Div(className='eight columns div-for-charts bg-grey', children=[
        dcc.Tabs(id='tabs-example', value='tab-1', children=[
            dcc.Tab(label='Change by Day (% change)', value='tab-1'),
            dcc.Tab(label='Change over whole Time (% change)', value='tab-2'),
        ]),
        html.Div(id='tabs-example-content')],
             style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'}),
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
