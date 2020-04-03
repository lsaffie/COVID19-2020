# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

def loadData(fileName, columnName):
    data = pd.read_csv(baseURL + fileName) \
             .drop(['Lat', 'Long'], axis=1) \
             .melt(id_vars=['Province/State', 'Country/Region'],
                 var_name='date', value_name=columnName) \
             .astype({'date':'datetime64[ns]', columnName:'Int64'},
                 errors='ignore')
    data['Province/State'].fillna('<all>', inplace=True)
    data[columnName].fillna(0, inplace=True)
    return data

ConfirmedCases = loadData(
    "time_series_covid19_confirmed_global.csv", "Cases")


# convert dates into rows

def ontario_data():
    df = ConfirmedCases[ConfirmedCases['Province/State'] == "Ontario"]
    df = df.reset_index().drop(columns=['Province/State', 'Country/Region'])
    return df

def country_df(country):
    df = ConfirmedCases[ConfirmedCases['Country/Region'] == country]
    df = df.reset_index().drop(columns=['Province/State'])
    return df.groupby('date').sum().reset_index()

def df_favs():
    df_favs = country_df("Chile")
    df_favs = df_favs.reset_index().drop(columns=['Cases'])

    for c in top_10_countries['Country/Region'].head(7):
        df_favs[c] = country_df(c).reset_index()['Cases']
        df_favs[c] = country_df(c).reset_index()['Cases']

    return df_favs.set_index('date')

def plot_timeseries_country(country, title):
    df = country_df(country).tail(30)
    return plot_timeseries_df(df, title, "Cases")

def plot_timeseries_df(df, title, series):
    return html.Div(
            dcc.Graph(
                id=title + '-graph',
                figure = px.line(df, x="date", y="Cases", title=title, text=df[series])),
            )

def plot_ontario_new_cases(column="new cases", title="Ontario New Cases"):
    return html.Div(
            dcc.Graph(id=column+'ontario-graph',
                figure = px.line(df_ontario, x="date", y=column, title=title, text=df_ontario[column]))
            )

def plot_timeseries_canada_province():
    df = ConfirmedCases[ConfirmedCases['Country/Region'] == "Canada"]
    df = df.groupby(['date', 'Province/State']).sum().reset_index().tail(300)
    df = df.sort_values('Cases', ascending=False)
    return html.Div(
            dcc.Graph(
                id='canada-province-graph',
                figure = px.line(df, x="date", y="Cases", title="Canada by Province", text=df["Cases"], color="Province/State")),)

def plot_top_countries():
    df_top = ConfirmedCases
    df_top = df_top.reset_index().drop(columns=['Province/State'])
    df_top = df_top[df_top['Country/Region'].isin(
        top_10_countries.head(5)['Country/Region'].to_list()
    )]
    df_top = df_top.sort_values('Cases', ascending=False)
    return html.Div(
            dcc.Graph(id='top_countries',
                figure = px.line(df_top, x="date", y='Cases', title="Top Countries", text=df_top["Cases"], color="Country/Region"))
            )

df_ontario = ontario_data().tail(30)
df_chile = country_df("Chile").tail(30)
df_us= country_df("US").tail(30)
top_10_countries = ConfirmedCases.groupby('Country/Region').max().sort_values('Cases', ascending=False).head(10).reset_index()
df_ontario['new cases'] = df_ontario['Cases'].diff()
df_ontario['new cases3'] = df_ontario['Cases'].diff(3)
df_favs = df_favs()

colors = {
        'background': '#111111',
        'text': '#7FDBFF'
        }

app.layout = html.Div(children=[
    html.H1(
        children='COVID19 Stats',
        style={
            'textAlign': 'center',
            'color': colors['text']
            }
        ),

    html.Div(
        dcc.Graph(
            id='example-graph-2',
            figure = {'data':[
                go.Bar(x=top_10_countries['Country/Region'],
                    y=top_10_countries['Cases'],
                    text = top_10_countries['Cases'], textposition='outside'),
                ],
                'layout': {
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                        }
                    }
                }
            ),
        ),

    plot_timeseries_country("Canada", "Canada Confirmed Cases")
    ,
    plot_timeseries_canada_province()
    ,
    plot_timeseries_df(df_ontario, "Ontario Confirmed Cases", "Cases")
    ,
    plot_ontario_new_cases()
    ,
    plot_ontario_new_cases("new cases3", "Ontario New Cases (3 day aggregation)")
    ,
    plot_top_countries()
    ,
    plot_timeseries_country("US", "US Confirmed Cases")
    ,
    plot_timeseries_country("Chile", "Chile Confirmed Cases")
    ,

    html.Div([
        dash_table.DataTable( id='table',
            columns=[{"name": i, "id": i} for i in top_10_countries.columns],
            data=top_10_countries.to_dict("rows"),
            )],
        ),

    ], style={'width': '80%', 'align-content': 'center', 'display': 'inline-block'})

if __name__ == '__main__':
    app.run_server(debug=True)
