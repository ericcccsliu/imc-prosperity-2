# dashapp.py

from dash import Dash, html, Input, Output, dash_table, dcc, State, ctx
import pandas as pd
import json
import io
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
from graph import *
from lib import *

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)


def serve_layout():
    compare_types = ["pnl", "position", "trades", "price", "trades volume"]

    return html.Div(
        [
            dcc.Store(id="df-store", data=None, storage_type="memory"),
            dcc.Store(id="trade-store", data=None, storage_type="memory"),
            html.Div(
                [
                    html.H2(
                        children="orange chicken",
                        style={"textAlign": "center", "margin-top": "5vh"},
                        className="three columns",
                    ),
                    html.Div(
                        dcc.Input(
                            id="directory-input",
                            type="text",
                            placeholder="Enter directory path",
                            value="../round5/backtests",
                        ),
                        className="two columns",
                        style={"margin-top": "6.5vh"},
                    ),
                    html.Div(
                        dcc.Dropdown(
                            id="log-file-dropdown",
                            options=[],
                            value=None,
                            clearable=False,
                            style={"font-size": "12px"},
                        ),
                        className="four columns",
                        style={"margin-top": "6.5vh", "width": "300px"},
                    ),
                    html.Div(
                        dcc.Dropdown(
                            id="product-dropdown",
                            options=[],
                            value=None,
                            clearable=False,
                        ),
                        className="two columns",
                        style={"margin-top": "6.5vh"},
                    ),
                    html.Div(
                        html.Button("Load", id="load-btn", n_clicks=0),
                        className="one column",
                        style={"margin-top": "6.5vh"},
                    ),
                ],
                style={"width": "90%", "display": "inline-block"},
                className="row",
            ),
            html.Div(
                [
                    html.Div(
                        children=dcc.Graph(
                            id="mid-price-graph",
                            figure=go.Figure(),
                            style={"height": "50vh"},
                            animate=False,
                        ),
                        className="eight columns",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "Timestamp: ",
                                                style={"margin-right": "5px"},
                                            ),
                                            dcc.Input(
                                                id="timestamp-clicked",
                                                type="number",
                                                value=0,
                                                debounce=True,
                                                style={"width": "100px", "margin-right": "50px"},
                                            ),
                                        ],
                                        className="six columns",
                                        style={
                                            "text-align": "center",
                                            "padding-top": "10px",
                                            "display": "flex",
                                            "align-items": "center",
                                            "justify-content": "center",
                                        },
                                    ),
                                    html.Button(
                                        "<",
                                        id="btn-l",
                                        n_clicks=0,
                                        className="one columns",
                                    ),
                                    html.Button(
                                        ">",
                                        id="btn-r",
                                        n_clicks=0,
                                        className="one columns",
                                    ),
                                ],
                                className="row",
                            ),
                            html.Div(
                                children=[],
                                id="orderbook-table",
                                style={"margin-top": "20px", "margin-left": "10%"},
                                className="ten columns",
                            ),
                        ],
                        className="three columns",
                        style={"margin-left": "5%"},
                    ),
                ],
                className="row",
            ),
            html.Div(
                [
                    html.Div(
                        children=dcc.Graph(
                            id="pnl-graph",
                            figure=go.Figure(),
                            style={"height": "50vh", "margin-left": "5%"},
                            animate=False,
                        ),
                        className="eight columns",
                    ),
                    html.Div(
                        [
                            html.H4("shawarma"),
                            html.Div(
                                children=[],
                                id="stats-table",
                                className="four columns",
                                style={"margin-top": "60px"},
                            ),
                        ],
                        style={"margin-left": "7%"},
                    ),
                ],
                className="row",
            ),
            html.Div(
                [
                    dcc.Store(id="compare-1-store", data=None, storage_type="memory"),
                    dcc.Store(id="compare-2-store", data=None, storage_type="memory"),
                    dcc.Store(
                        id="compare-1-tradejson", data=None, storage_type="memory"
                    ),
                    dcc.Store(
                        id="compare-2-tradejson", data=None, storage_type="memory"
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.H4("taco"),
                                style={"textAlign": "center", "margin-top": "5vh"},
                                className="one columns",
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="compare-log-file-dropdown-1",
                                    options=[],
                                    value=None,
                                    clearable=False,
                                ),
                                className="two columns",
                                style={"margin-top": "6.5vh"},
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="compare-type-dropdown1",
                                    options=[
                                        {"label": f, "value": f} for f in compare_types
                                    ],
                                    value=None,
                                    clearable=False,
                                ),
                                className="one columns",
                                style={"margin-top": "6.5vh"},
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="compare-product-dropdown1",
                                    options=[],
                                    value=None,
                                    clearable=False,
                                ),
                                className="two columns",
                                style={"margin-top": "6.5vh"},
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="compare-log-file-dropdown-2",
                                    options=[],
                                    value=None,
                                    clearable=False,
                                ),
                                className="two columns",
                                style={"margin-top": "6.5vh"},
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="compare-type-dropdown2",
                                    options=[
                                        {"label": f, "value": f} for f in compare_types
                                    ],
                                    value=None,
                                    clearable=False,
                                ),
                                className="one columns",
                                style={"margin-top": "6.5vh"},
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="compare-product-dropdown2",
                                    options=[],
                                    value=None,
                                    clearable=False,
                                ),
                                className="two columns",
                                style={"margin-top": "6.5vh"},
                            ),
                            html.Div(
                                html.Button("Load", id="compare-load-btn", n_clicks=0),
                                className="one columns",
                                style={"margin-top": "6.5vh"},
                            ),
                        ],
                        className="row",
                        style={"font-size": "12px"},
                    ),
                    html.Div(
                        children=dcc.Graph(
                            id="compare-graph",
                            figure=go.Figure(),
                            style={"height": "50vh"},
                            animate=False,
                        ),
                        className="twelve columns",
                    ),
                ]
            ),
        ],
        style={"padding": "30px"},
    )


app.layout = serve_layout()


@app.callback(
    Output("df-store", "data"),
    [Input("product-dropdown", "value")],
    [Input("load-btn", "n_clicks")],
    [Input("log-file-dropdown", "value")],
    [State("directory-input", "value")],
    [State("df-store", "data")],
)
def update_product(product, load_btn, log_file, directory, df):
    if "load-btn" == ctx.triggered_id or "product-dropdown" == ctx.triggered_id:
        df, trade_json, df_sandbox = parse_log_file(
            os.path.join(directory, log_file), product
        )
        return df.to_json()
    return df


@app.callback(
    Output("trade-store", "data"),
    [Input("product-dropdown", "value")],
    [Input("load-btn", "n_clicks")],
    [Input("log-file-dropdown", "value")],
    [State("directory-input", "value")],
    [State("trade-store", "data")],
)
def update_trade_json(product, load_btn, log_file, directory, trade_json):
    if "load-btn" == ctx.triggered_id or "product-dropdown" == ctx.triggered_id:
        df, trade_json, df_sandbox = parse_log_file(
            os.path.join(directory, log_file), product
        )
        return trade_json
    return trade_json


@app.callback(
    Output("timestamp-clicked", "value"),
    [Input("btn-r", "n_clicks")],
    [Input("btn-l", "n_clicks")],
    [State("timestamp-clicked", "value")],
    [Input("mid-price-graph", "clickData")],
    [Input("pnl-graph", "clickData")],
    [Input("compare-graph", "clickData")],
)
def update_timestamp(btn1, btn2, timestamp, clickData, pnlClickData, compareClickData):
    if "btn-r" == ctx.triggered_id:
        timestamp += 100
    elif "btn-l" == ctx.triggered_id:
        timestamp -= 100
    elif "mid-price-graph" == ctx.triggered_id and clickData:
        timestamp = clickData["points"][0]["x"]
    elif "pnl-graph" == ctx.triggered_id and pnlClickData:
        timestamp = pnlClickData["points"][0]["x"]
    elif "compare-graph" == ctx.triggered_id and compareClickData:
        timestamp = compareClickData["points"][0]["x"]
    return timestamp


@app.callback(
    Output("orderbook-table", "children"),
    [Input("timestamp-clicked", "value")],
    [Input("product-dropdown", "value")],
    [Input("df-store", "data")],
)
def update_orderbook(timestamp, product, df):
    if df:
        df = pd.DataFrame(json.loads(df))
        return orderbook_table(df, product, timestamp)
    return []


@app.callback(
    Output("mid-price-graph", "figure"),
    [Input("timestamp-clicked", "value")],
    [State("mid-price-graph", "figure")],
    [Input("load-btn", "n_clicks")],
    [Input("product-dropdown", "value")],
    [Input("df-store", "data")],
    [Input("trade-store", "data")],
)
def update_vertical_line(timestamp, fig, load_btn, product, df, trade_json):
    if df and trade_json:
        if "load-btn" == ctx.triggered_id or "product-dropdown" == ctx.triggered_id:
            df = pd.DataFrame(json.loads(df))
            fig = price_graph(df, trade_json, product, timestamp)
        fig["layout"]["shapes"][0]["x0"] = timestamp
        fig["layout"]["shapes"][0]["x1"] = timestamp
    return fig


@app.callback(
    Output("pnl-graph", "figure"),
    [Input("timestamp-clicked", "value")],
    [State("pnl-graph", "figure")],
    [Input("load-btn", "n_clicks")],
    [Input("trade-store", "data")],
    [Input("df-store", "data")],
)
def update_pnl(timestamp, fig, load_btn, trade_json, df):
    if df and trade_json:
        if "load-btn" == ctx.triggered_id:
            df = pd.DataFrame(json.loads(df))
            fig = pnl_graph(df, trade_json, timestamp)

        if "shapes" in fig["layout"]:
            fig["layout"]["shapes"][0]["x0"] = timestamp
            fig["layout"]["shapes"][0]["x1"] = timestamp
    return fig


@app.callback(
    Output("log-file-dropdown", "options"), [Input("directory-input", "value")]
)
def update_log_file_options(directory):
    if directory:
        log_files = [f for f in os.listdir(directory) if f.endswith(".log")]
        return [{"label": f, "value": f} for f in log_files]
    return []


@app.callback(
    Output("product-dropdown", "options"),
    [Input("log-file-dropdown", "value")],
    [State("directory-input", "value")],
)
def update_product_options(log_file, directory):
    if log_file and directory:
        return parse_product_list(os.path.join(directory, log_file))
    return []


@app.callback(
    Output("stats-table", "children"),
    [Input("product-dropdown", "value")],
    [Input("load-btn", "n_clicks")],
    [Input("log-file-dropdown", "value")],
    [State("directory-input", "value")],
)
def update_stats_table(product, load_btn, log_file, directory):
    if log_file and directory and product:
        df, trade_json, df_sandbox = parse_log_file(
            os.path.join(directory, log_file), product
        )
        return stats_table(df, trade_json, product)
    return []


@app.callback(
    Output("compare-graph", "figure"),
    [State("compare-graph", "figure")],
    [Input("timestamp-clicked", "value")],
    [Input("compare-load-btn", "n_clicks")],
    [Input("compare-log-file-dropdown-1", "value")],
    [Input("compare-log-file-dropdown-2", "value")],
    [Input("compare-product-dropdown1", "value")],
    [Input("compare-product-dropdown2", "value")],
    [Input("compare-type-dropdown1", "value")],
    [Input("compare-type-dropdown2", "value")],
    [State("directory-input", "value")],
)
def update_compare_graph(
    fig,
    timestamp,
    load_btn,
    log_file1,
    log_file2,
    product1,
    product2,
    compare_type1,
    compare_type2,
    directory,
):
    if (
        log_file1
        and log_file2
        and product1
        and product2
        and directory
        and compare_type1
        and compare_type2
    ):
        if "timestamp-clicked" != ctx.triggered_id:
            df1, trade_json1, df_sandbox1 = parse_log_file(
                os.path.join(directory, log_file1), product1
            )
            df2, trade_json2, df_sandbox2 = parse_log_file(
                os.path.join(directory, log_file2), product2
            )
            fig = compare_graph(
                df1,
                df2,
                trade_json1,
                trade_json2,
                product1,
                product2,
                compare_type1,
                compare_type2,
            )

        fig["layout"]["shapes"][0]["x0"] = timestamp
        fig["layout"]["shapes"][0]["x1"] = timestamp
    return fig


@app.callback(
    Output("compare-log-file-dropdown-1", "options"),
    [Input("directory-input", "value")],
)
def update_compare_log_file_options_1(directory):
    if directory:
        log_files = [f for f in os.listdir(directory) if f.endswith(".log")]
        return [{"label": f, "value": f} for f in log_files]
    return []


@app.callback(
    Output("compare-log-file-dropdown-2", "options"),
    [Input("directory-input", "value")],
)
def update_compare_log_file_options_2(directory):
    if directory:
        log_files = [f for f in os.listdir(directory) if f.endswith(".log")]
        return [{"label": f, "value": f} for f in log_files]
    return []


@app.callback(
    Output("compare-product-dropdown1", "options"),
    [Input("compare-log-file-dropdown-1", "value")],
    [State("directory-input", "value")],
)
def update_compare_product_options1(log_file1, directory):
    if log_file1 and directory:
        products1 = parse_product_list(os.path.join(directory, log_file1))
        return [{"label": p, "value": p} for p in products1]
    return []


@app.callback(
    Output("compare-product-dropdown2", "options"),
    [Input("compare-log-file-dropdown-2", "value")],
    [State("directory-input", "value")],
)
def update_compare_product_options2(log_file2, directory):
    if log_file2 and directory:
        products2 = parse_product_list(os.path.join(directory, log_file2))
        return [{"label": p, "value": p} for p in products2]
    return []


app.run_server(debug=True)
