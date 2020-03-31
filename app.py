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

ConfirmedCases_raw=pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
Deaths_raw=pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
Recoveries_raw=pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')


# convert dates into rows
def cleandata(df_raw):
    df_cleaned = df_raw.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_name = 'Cases', var_name='Date')
    df_cleaned = df_cleaned.set_index(['Country/Region', 'Date'])
    return df_cleaned


def ontario_data():
    df = ConfirmedCases[ConfirmedCases['Province/State'] == "Ontario"]
    df = df.reset_index().drop(columns=['Province/State', 'Lat', 'Long', 'Country/Region'])
    return df

def chile_data():
    df = ConfirmedCases.loc["Chile"]
    df = df.reset_index().drop(columns=['Province/State', 'Lat', 'Long'])
    return df

def df_favs():
    df_favs = ConfirmedCases.loc["Chile"]
    df_favs = df_favs.reset_index().drop(columns=['Province/State', 'Lat', 'Long', 'Cases'])

    for c in top_10_countries['Country/Region'].head(7):
        df_favs[c] = ConfirmedCases.loc[c].reset_index()['Cases']

    return df_favs.set_index('Date')


## Clean all datasets
ConfirmedCases = cleandata(ConfirmedCases_raw)
DeathCases = cleandata(Deaths_raw)
RecoveryCases = cleandata(Recoveries_raw)

df_ontario = ontario_data()
df_chile = chile_data()
top_10_countries = ConfirmedCases.max(level=0)['Cases'].reset_index().sort_values('Cases', ascending=False).head(10)
df_ontario['new cases'] = df_ontario['Cases'].diff()
df_favs = df_favs()

## Top countries
df_top = ConfirmedCases
df_top = df_top.reset_index().drop(columns=['Province/State', 'Lat', 'Long'])
df_top = df_top[df_top['Country/Region'].isin(
    top_10_countries.head(5)['Country/Region'].to_list()
)]



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
                    text = top_10_countries['Cases'],
                    textposition='outside'),
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

    html.Div(
        dcc.Graph(
            id='ontario-graph',
            figure = px.line(df_ontario,
                x="Date",
                y="Cases",
                title="Ontario Confirmed Cases",
                text=df_ontario["Cases"],
                ),
            ),
        ),

    html.Div(
        dcc.Graph(
            id='ontario-growth',
            figure = px.line(df_ontario, x="Date", y="new cases", title="Ontario Daily New Cases", text=df_ontario['new cases']),
        ),
    ),

    html.Div(
        dcc.Graph(
            id='top-growth',
            figure = px.line(df_top, x='Date', y='Cases', color='Country/Region', title="top countries")
        ),
    ),

    html.Div(
        dcc.Graph(
            id='chile-graph',
            figure = px.line(df_chile, x="Date", y="Cases", title="Chile Confirmed Cases", text=df_chile['Cases']),
        ),
    ),

    html.Div([
        dash_table.DataTable( id='table',
            columns=[{"name": i, "id": i} for i in top_10_countries.columns],
            data=top_10_countries.to_dict("rows"),
            )],
        ),

    ], style={'width': '100%', 'display': 'inline-block'})

if __name__ == '__main__':
    app.run_server(debug=True)
