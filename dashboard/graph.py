# graph.py

from dash import Dash, html, Input, Output, dash_table, dcc, State, ctx
import pandas as pd
import json
import io
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import threading
from lib import *


def price_graph(df, trades_json, product, timestamp):
    df_product = df[df["product"] == product]
    df_product["mm_bid"] = df_product.apply(
        lambda x: (
            x["bid_price_1"]
            if x["bid_volume_1"] > 25
            else (
                x["bid_price_2"]
                if x["bid_volume_2"] > 25
                else x["bid_price_3"] if x["bid_volume_3"] > 25 else np.nan
            )
        ),
        axis=1,
    )
    df_product["mm_ask"] = df_product.apply(
        lambda x: (
            x["ask_price_1"]
            if x["ask_volume_1"] > 25
            else (
                x["ask_price_2"]
                if x["ask_volume_2"] > 25
                else x["ask_price_3"] if x["ask_volume_3"] > 25 else np.nan
            )
        ),
        axis=1,
    )

    df_product["mm_mid"] = (df_product["mm_bid"] + df_product["mm_ask"]) / 2
    df_product["mm_mid"] = df_product["mm_mid"].fillna(method="ffill")
    fig = px.line(
        df_product, x="timestamp", y=["mid_price", "fair"], title="Price Over Time"
    )
    fig.add_trace(
        go.Scatter(
            x=df_product["timestamp"],
            y=df_product["mm_mid"],
            mode="lines",
            name=f"{product} MM",
        )
    )

    if product == "ORCHIDS":
        df_orchids_highest_level = pd.read_csv("orchids_highest_level.csv")
        df_orchids_highest_level = df_orchids_highest_level[df_orchids_highest_level["highest_level"] != 0]
        fig.add_trace(
            go.Scatter(
                x=df_orchids_highest_level["timestamp"],
                y=round(df_orchids_highest_level["highest_level"]),
                mode="markers",
                name="Highest Level",
                marker_size=4,
            )
        )

    if "implied_bid" in df_product.columns and df_product["implied_bid"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product["implied_bid"],
                mode="lines",
                name="Implied Bid",
                visible="legendonly",
            )
        )
    if "implied_ask" in df_product.columns and df_product["implied_ask"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product["implied_ask"],
                mode="lines",
                name="Implied Ask",
                visible="legendonly",
            )
        )

    if (
        "implied_bid" in df_product.columns
        and df_product["implied_bid"].notna().any()
        and "implied_ask" in df_product.columns
        and df_product["implied_ask"].notna().any()
    ):
        df_product["implied_mid"] = (
            df_product["implied_bid"] + df_product["implied_ask"]
        ) / 2
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product["implied_mid"],
                mode="lines",
                name="Implied Mid",
                visible="legendonly",
            )
        )

    if "foreign_bid" in df_product.columns and df_product["foreign_bid"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product["foreign_bid"],
                mode="lines",
                name="Foreign Bid",
                visible="legendonly",
            )
        )

    if "foreign_ask" in df_product.columns and df_product["foreign_ask"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product["foreign_ask"],
                mode="lines",
                name="Foreign Ask",
                visible="legendonly",
            )
        )

    if "algo_bid" in df_product.columns and df_product["algo_bid"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product["algo_bid"],
                mode="lines",
                name="Algo Bid",
                visible="legendonly",
            )
        )

    if "algo_ask" in df_product.columns and df_product["algo_ask"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product["algo_ask"],
                mode="lines",
                name="Algo Ask",
                visible="legendonly",
            )
        )

    # ... rest of the function ...
    for y in ["bid_price_1", "ask_price_1"]:
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product[y],
                mode="lines",
                name=y,
                marker_size=4,
                hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>Volume: %{text}",
                text=df_product[y.replace("price", "volume")],
                visible="legendonly",
            )
        )
    trades_df = pd.DataFrame(json.loads(trades_json))
    trades_df = trades_df[trades_df["symbol"] == product].copy().reset_index(drop=True)
    trades_df = trades_df.merge(
        df_product[
            [
                "timestamp",
                "ask_price_1",
                "ask_price_2",
                "ask_price_3",
                "bid_price_1",
                "bid_price_2",
                "bid_price_3",
            ]
        ],
        on="timestamp",
        how="left",
    )
   
    
    markets_trades = trades_df[
        (trades_df["buyer"] != "SUBMISSION") & (trades_df["seller"] != "SUBMISSION")
    ]
    buy_trades = (
        trades_df[trades_df["buyer"] == "SUBMISSION"].copy().reset_index(drop=True)
    )
    buy_trades["is_matched"] = buy_trades.apply(
        lambda x: x["price"] in [x["ask_price_1"], x["ask_price_2"], x["ask_price_3"]],
        axis=1,
    )
    buy_trades["type"] = buy_trades["is_matched"].apply(
        lambda x: "Take" if x else "Make"
    )
    buy_trades["text"] = buy_trades.apply(
        lambda x: f"Volume: {x['quantity']}<br>Type: {x['type']}", axis=1
    )
    sell_trades = (
        trades_df[trades_df["seller"] == "SUBMISSION"].copy().reset_index(drop=True)
    )
    sell_trades["is_matched"] = sell_trades.apply(
        lambda x: x["price"] in [x["bid_price_1"], x["bid_price_2"], x["bid_price_3"]],
        axis=1,
    )
    sell_trades["type"] = sell_trades["is_matched"].apply(
        lambda x: "Take" if x else "Make"
    )
    sell_trades["text"] = sell_trades.apply(
        lambda x: f"Volume: {x['quantity']}<br>Type: {x['type']}", axis=1
    )
    fig.add_trace(
        go.Scatter(
            x=buy_trades["timestamp"],
            y=buy_trades["price"],
            mode="markers",
            name="Buy Trades",
            marker_size=4,
            hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>%{text}",
            text=buy_trades["text"],
            visible="legendonly",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sell_trades["timestamp"],
            y=sell_trades["price"],
            mode="markers",
            name="Sell Trades",
            marker_size=4,
            hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>%{text}",
            text=sell_trades["text"],
            visible="legendonly",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=markets_trades["timestamp"],
            y=markets_trades["price"],
            mode="markers",
            name="Markets Trades",
            marker_size=4,
            hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>Volume: %{text}",
            text=markets_trades["quantity"],
            visible="legendonly",
        )
    )
    for y in ["bid_price_2", "ask_price_2", "bid_price_3", "ask_price_3"]:
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product[y],
                mode="markers",
                name=y,
                marker_size=4,
                hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>Volume: %{text}",
                text=df_product[y.replace("price", "volume")],
                visible="legendonly",
            )
        )
    fig.update_layout(xaxis_title="Timestamp", yaxis_title="Price")
    fig.update_layout(
        yaxis1=dict(
            title="Price",
        ),
        yaxis2=dict(overlaying="y", side="right"),
    )
    fig.add_vline(x=timestamp, line_width=1, line_dash="dash", line_color="black")
    fig.update_xaxes(spikemode="across")
    return fig


def pnl_graph(df, trades_json, timestamp, df_sandbox=None):
    fig = go.Figure()
    for product in df["product"].unique():
        df_product = df[df["product"] == product]
        fig.add_trace(
            go.Scatter(
                x=df_product["timestamp"],
                y=df_product["profit_and_loss"],
                mode="lines",
                name=f"{product} PnL",
            )
        )

    total_pnl = df.groupby("timestamp")["profit_and_loss"].sum()
    fig.add_trace(
        go.Scatter(
            x=total_pnl.index, y=total_pnl.values, mode="lines", name="Total PnL"
        )
    )
    fig.update_layout(xaxis_title="Timestamp", yaxis_title="PnL")
    fig.add_vline(x=timestamp, line_width=1, line_dash="dash", line_color="black")
    fig.update_xaxes(spikemode="across")

    df_trades = pd.DataFrame(json.loads(trades_json))
    for product in df_trades["symbol"].unique():
        if product == "ORCHIDS" and "orchids_position" in df_trades.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=df["orchids_position"],
                    mode="lines",
                    name=f"{product} Position",
                    yaxis="y2",
                    hovertemplate="Timestamp: %{x}<br>Position: %{y}",
                )
            )
        else:
            df_product = df_trades[df_trades["symbol"] == product]
            df_owntrades = df_product[
                (df_product["buyer"] == "SUBMISSION")
                | (df_product["seller"] == "SUBMISSION")
            ].copy()
            df_owntrades["volume"] = df_owntrades.apply(
                lambda x: (
                    x["quantity"] if x["buyer"] == "SUBMISSION" else -x["quantity"]
                ),
                axis=1,
            )
            position = df_owntrades[["timestamp", "volume"]].copy()

            if len(position) > 0:
                timestamp_min = min(df_owntrades["timestamp"].to_numpy())
                timestamp_max = max(df_owntrades["timestamp"].to_numpy())
                position = position.groupby("timestamp").sum().reset_index()
                position = (
                    position.set_index("timestamp")
                    .reindex(range(timestamp_min, timestamp_max + 1, 100), fill_value=0)
                    .reset_index()
                )
                position = position.groupby("timestamp").sum().reset_index()
                position = position.set_index("timestamp")
                position = position["volume"]

                fig.add_trace(
                    go.Scatter(
                        x=position.index,
                        y=position.values,
                        mode="lines",
                        name=f"{product} Volume",
                        yaxis="y2",
                        hovertemplate="Timestamp: %{x}<br>Volume: %{y}",
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=position.index,
                        y=position.values.cumsum(),
                        mode="lines",
                        name=f"{product} Position",
                        yaxis="y2",
                        hovertemplate="Timestamp: %{x}<br>Position: %{y}",
                    )
                )

    fig.update_layout(
        yaxis1=dict(
            title="PnL",
        ),
        yaxis2=dict(title="Position", overlaying="y", side="right"),
    )

    return fig


def stats_table(df, trades_json, product):
    total_pnl = df.groupby("timestamp")["profit_and_loss"].sum().iloc[-1]
    df_product = df[df["product"] == product]
    trades_product = pd.DataFrame(json.loads(trades_json))
    trades_product = trades_product[trades_product["symbol"] == product]
    if "fair" not in df_product.columns:
        calculate_fair(df_product)

    own_trades_product = trades_product[
        (trades_product["buyer"] == "SUBMISSION")
        | (trades_product["seller"] == "SUBMISSION")
    ].copy()
    if len(own_trades_product) == 0:
        return html.Div(children="No trades")
    own_trades_product["volume"] = own_trades_product.apply(
        lambda x: x["quantity"] if x["buyer"] == "SUBMISSION" else -x["quantity"],
        axis=1,
    )
    own_trades_product = own_trades_product.merge(
        df_product[["timestamp", "mid_price", "fair", "profit_and_loss"]],
        on="timestamp",
        how="left",
    )
    own_trades_product["total_edge"] = (
        abs(own_trades_product["price"] - own_trades_product["fair"])
        * own_trades_product["quantity"]
    )
    own_trades_product["avg_edge"] = (
        own_trades_product["total_edge"].sum() / own_trades_product["quantity"].sum()
    )
    own_trades_product["position"] = own_trades_product["volume"].cumsum()
    # buy_trades = own_trades_product[own_trades_product['buyer'] == 'SUBMISSION']
    # buy_trades['is_matched'] = buy_trades.apply(lambda x: x['price'] in [x['ask_price_1'], x['ask_price_2'], x['ask_price_3']], axis=1)
    # buy_trades['type'] = buy_trades['is_matched'].apply(lambda x: 'Take' if x else 'Make')
    # buy_trades['text'] = buy_trades.apply(lambda x: f"Volume: {x['quantity']}<br>Type: {x['type']}", axis=1)

    # sell_trades = own_trades_product[own_trades_product['seller'] == 'SUBMISSION']
    # sell_trades['is_matched'] = sell_trades.apply(lambda x: x['price'] in [x['bid_price_1'], x['bid_price_2'], x['bid_price_3']], axis=1)
    # sell_trades['type'] = sell_trades['is_matched'].apply(lambda x: 'Take' if x else 'Make')
    # sell_trades['text'] = sell_trades.apply(lambda x: f"Volume: {x['quantity']}<br>Type: {x['type']}", axis=1)

    # Calculate statistics
    pnl = own_trades_product["profit_and_loss"].iloc[-1]
    total_num_trades = own_trades_product["quantity"].count()
    avg_edge = (
        own_trades_product["total_edge"].sum() / own_trades_product["quantity"].sum()
    )
    avg_trade_size = own_trades_product["quantity"].mean()
    position = own_trades_product["position"].to_numpy()
    nonzero_count = np.count_nonzero(np.diff(np.sign(position)))
    avg_time_to_offset = (
        len(position) / nonzero_count * 100 if nonzero_count != 0 else 0
    )
    mad_10 = (
        (df_product["mid_price"].shift(10) - df_product["mid_price"])
        .dropna()
        .apply(abs)
        .mean()
    )
    volume = own_trades_product["quantity"].sum()
    table = pd.DataFrame(
        data=[
            ["Total PnL", total_pnl],
            [f"{product} PnL", pnl],
            ["Total Trades", total_num_trades],
            ["Total Volume", volume],
            ["Avg Edge", avg_edge],
            ["Avg Trade Size", avg_trade_size],
            ["10-mad-mid_price", mad_10],
            ["Avg Time to Offset", avg_time_to_offset],
        ],
        columns=["Statistic", "Value"],
    )
    dt = dash_table.DataTable(
        id="trades-stats",
        columns=[{"id": c, "name": c} for c in table.columns],
        data=table.to_dict("records"),
        style_table={"height": "40vh"},
        style_cell={"minWidth": "100px", "maxWidth": "100px", "width": "100px"},
        style_cell_conditional=[
            {"if": {"column_id": "Statistic"}, "textAlign": "center"}
        ],
    )
    return dt


compare_types = ["pnl", "position", "trades", "price", "trades volume"]


def compare_graph(
    df1, df2, trade_json1, trade_json2, product1, product2, compare_type1, compare_type2
):
    fig = go.Figure()
    draw_graph(fig, df1, trade_json1, product1, compare_type1, 1)
    draw_graph(fig, df2, trade_json2, product2, compare_type2, 2)

    fig.update_layout(
        yaxis1=layout_dict(compare_type1, 1), yaxis2=layout_dict(compare_type2, 2)
    )

    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="black")

    return fig


def layout_dict(compare_type, log_number):
    if compare_type == "pnl":
        if log_number == 1:
            return dict(title="PnL")
        else:
            return dict(title="PnL", overlaying="y", side="right")
    elif compare_type == "position":
        if log_number == 1:
            return dict(title="Position")
        else:
            return dict(title="Position", overlaying="y", side="right")
    elif compare_type == "trades":
        if log_number == 1:
            return dict(title="Trades")
        else:
            return dict(title="Trades", overlaying="y", side="right")
    elif compare_type == "price":
        if log_number == 1:
            return dict(title="Price")
        else:
            return dict(title="Price", overlaying="y", side="right")


def draw_graph(fig, df, trade_json, product, compare_type, log_number):
    if compare_type == "pnl":
        df_product = df[df["product"] == product]
        if log_number == 1:
            fig.add_trace(
                go.Scatter(
                    x=df_product["timestamp"],
                    y=df_product["profit_and_loss"],
                    mode="lines",
                    name=f"Log 1 {product} PnL",
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=df_product["timestamp"],
                    y=df_product["profit_and_loss"],
                    mode="lines",
                    name=f"Log 2 {product} PnL",
                    yaxis="y2",
                )
            )

    elif compare_type == "position":
        if product == "ORCHIDS" and "orchids_position" in df_trades.columns:
            if log_number == 1:
                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df["orchids_position"],
                        mode="lines",
                        name=f"Log {log_number} {product} Position",
                    )
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df["orchids_position"],
                        mode="lines",
                        name=f"Log {log_number} {product} Position",
                        yaxis="y2",
                    )
                )
        else:
            df_trades = pd.DataFrame(json.loads(trade_json))
            df_product1 = df_trades[df_trades["symbol"] == product]
            df_owntrades = (
                df_product1[
                    (df_product1["buyer"] == "SUBMISSION")
                    | (df_product1["seller"] == "SUBMISSION")
                ]
                .copy()
                .reset_index(drop=True)
            )
            df_owntrades["volume"] = df_owntrades.apply(
                lambda x: (
                    x["quantity"] if x["buyer"] == "SUBMISSION" else -x["quantity"]
                ),
                axis=1,
            )
            position = df_owntrades[["timestamp", "volume"]].copy()
            if len(position) > 0:
                timestamp_min = min(df_owntrades["timestamp"])
                timestamp_max = max(df_owntrades["timestamp"])
                position = position.groupby("timestamp").sum().reset_index()
                position = (
                    position.set_index("timestamp")
                    .reindex(range(timestamp_min, timestamp_max + 1, 100), fill_value=0)
                    .reset_index()
                )
                position = position.groupby("timestamp").sum().reset_index()
                position = position.set_index("timestamp")
                position = position["volume"]

                if log_number == 1:
                    fig.add_trace(
                        go.Scatter(
                            x=position.index,
                            y=position.values,
                            mode="lines",
                            name=f"Log {log_number} {product} Volume",
                            hovertemplate="Timestamp: %{x}<br>Volume: %{y}",
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=position.index,
                            y=position.values.cumsum(),
                            mode="lines",
                            name=f"Log {log_number} {product} Position",
                            hovertemplate="Timestamp: %{x}<br>Position: %{y}",
                        )
                    )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=position.index,
                            y=position.values,
                            mode="lines",
                            name=f"Log {log_number} {product} Volume",
                            yaxis="y2",
                            hovertemplate="Timestamp: %{x}<br>Volume: %{y}",
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=position.index,
                            y=position.values.cumsum(),
                            mode="lines",
                            name=f"Log {log_number} {product} Position",
                            yaxis="y2",
                            hovertemplate="Timestamp: %{x}<br>Position: %{y}",
                        )
                    )
    elif compare_type == "trades":
        trades_df = pd.DataFrame(json.loads(trade_json))
        trades_df = trades_df[trades_df["symbol"] == product]
        df_product = df[df["product"] == product]
        trades_df = trades_df.merge(
            df_product[
                [
                    "timestamp",
                    "ask_price_1",
                    "ask_price_2",
                    "ask_price_3",
                    "bid_price_1",
                    "bid_price_2",
                    "bid_price_3",
                ]
            ],
            on="timestamp",
            how="left",
        )

        markets_trades = trades_df[
            (trades_df["buyer"] != "SUBMISSION") & (trades_df["seller"] != "SUBMISSION")
        ]

        buy_trades = trades_df[trades_df["buyer"] == "SUBMISSION"]
        buy_trades["is_matched"] = buy_trades.apply(
            lambda x: x["price"]
            in [x["ask_price_1"], x["ask_price_2"], x["ask_price_3"]],
            axis=1,
        )
        buy_trades["type"] = buy_trades["is_matched"].apply(
            lambda x: "Take" if x else "Make"
        )
        buy_trades["text"] = buy_trades.apply(
            lambda x: f"Volume: {x['quantity']}<br>Type: {x['type']}", axis=1
        )

        sell_trades = trades_df[trades_df["seller"] == "SUBMISSION"]
        sell_trades["is_matched"] = sell_trades.apply(
            lambda x: x["price"]
            in [x["bid_price_1"], x["bid_price_2"], x["bid_price_3"]],
            axis=1,
        )
        sell_trades["type"] = sell_trades["is_matched"].apply(
            lambda x: "Take" if x else "Make"
        )
        sell_trades["text"] = sell_trades.apply(
            lambda x: f"Volume: {x['quantity']}<br>Type: {x['type']}", axis=1
        )

        if log_number == 1:
            fig.add_trace(
                go.Scatter(
                    x=buy_trades["timestamp"],
                    y=buy_trades["price"],
                    mode="markers",
                    name=f"Log {log_number} {product} Buy Trades",
                    marker_size=4,
                    hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>%{text}",
                    text=buy_trades["text"],
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=sell_trades["timestamp"],
                    y=sell_trades["price"],
                    mode="markers",
                    name=f"Log {log_number} {product} Sell Trades",
                    marker_size=4,
                    hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>%{text}",
                    text=sell_trades["text"],
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=markets_trades["timestamp"],
                    y=markets_trades["price"],
                    mode="markers",
                    name=f"Log {log_number} {product} Markets Trades",
                    marker_size=4,
                    hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>Volume: %{text}",
                    text=markets_trades["quantity"],
                    visible="legendonly",
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=buy_trades["timestamp"],
                    y=buy_trades["price"],
                    mode="markers",
                    name=f"Log {log_number} {product} Buy Trades",
                    marker_size=4,
                    hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>%{text}",
                    text=buy_trades["text"],
                    yaxis="y2",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=sell_trades["timestamp"],
                    y=sell_trades["price"],
                    mode="markers",
                    name=f"Log {log_number} {product} Sell Trades",
                    marker_size=4,
                    hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>%{text}",
                    text=sell_trades["text"],
                    yaxis="y2",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=markets_trades["timestamp"],
                    y=markets_trades["price"],
                    mode="markers",
                    name=f"Log {log_number} {product} Markets Trades",
                    marker_size=4,
                    hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>Volume: %{text}",
                    text=markets_trades["quantity"],
                    visible="legendonly",
                    yaxis="y2",
                )
            )
    elif compare_type == "price":
        df_product = df[df["product"] == product]
        if log_number == 1:
            fig.add_trace(
                go.Scatter(
                    x=df_product["timestamp"],
                    y=df_product["mid_price"],
                    mode="lines",
                    name=f"Log {log_number} {product} Mid Price",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df_product["timestamp"],
                    y=df_product["fair"],
                    mode="lines",
                    name=f"Log {log_number} {product} Fair Price",
                )
            )
            if (
                "implied_bid" in df_product.columns
                and df_product["implied_bid"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["implied_bid"],
                        mode="lines",
                        name=f"Log {log_number} {product} Implied Bid",
                        visible="legendonly",
                    )
                )
            if (
                "implied_ask" in df_product.columns
                and df_product["implied_ask"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["implied_ask"],
                        mode="lines",
                        name=f"Log {log_number} {product} Implied Ask",
                        visible="legendonly",
                    )
                )

            if (
                "implied_bid" in df_product.columns
                and df_product["implied_bid"].notna().any()
                and "implied_ask" in df_product.columns
                and df_product["implied_ask"].notna().any()
            ):
                df_product["implied_mid"] = (
                    df_product["implied_bid"] + df_product["implied_ask"]
                ) / 2
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["implied_mid"],
                        mode="lines",
                        name=f"Log {log_number} {product} Implied Mid",
                        visible="legendonly",
                    )
                )

            if (
                "foreign_bid" in df_product.columns
                and df_product["foreign_bid"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["foreign_bid"],
                        mode="lines",
                        name=f"Log {log_number} {product} Foreign Bid",
                        visible="legendonly",
                    )
                )

            if (
                "foreign_ask" in df_product.columns
                and df_product["foreign_ask"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["foreign_ask"],
                        mode="lines",
                        name=f"Log {log_number} {product} Foreign Ask",
                        visible="legendonly",
                    )
                )

            if (
                "algo_bid" in df_product.columns
                and df_product["algo_bid"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["algo_bid"],
                        mode="lines",
                        name=f"Log {log_number} {product} Algo Bid",
                        visible="legendonly",
                    )
                )

            if (
                "algo_ask" in df_product.columns
                and df_product["algo_ask"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["algo_ask"],
                        mode="lines",
                        name=f"Log {log_number} {product} Algo Ask",
                        visible="legendonly",
                    )
                )
        else:
            if (
                "implied_bid" in df_product.columns
                and df_product["implied_bid"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["implied_bid"],
                        mode="lines",
                        name=f"Log {log_number} {product} Implied Bid",
                        visible="legendonly",
                        yaxis="y2",
                    )
                )
            if (
                "implied_ask" in df_product.columns
                and df_product["implied_ask"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["implied_ask"],
                        mode="lines",
                        name=f"Log {log_number} {product} Implied Ask",
                        visible="legendonly",
                        yaxis="y2",
                    )
                )

            if (
                "implied_bid" in df_product.columns
                and df_product["implied_bid"].notna().any()
                and "implied_ask" in df_product.columns
                and df_product["implied_ask"].notna().any()
            ):
                df_product["implied_mid"] = (
                    df_product["implied_bid"] + df_product["implied_ask"]
                ) / 2
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["implied_mid"],
                        mode="lines",
                        name=f"Log {log_number} {product} Implied Mid",
                        visible="legendonly",
                        yaxis="y2",
                    )
                )

            if (
                "foreign_bid" in df_product.columns
                and df_product["foreign_bid"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["foreign_bid"],
                        mode="lines",
                        name=f"Log {log_number} {product} Foreign Bid",
                        visible="legendonly",
                        yaxis="y2",
                    )
                )

            if (
                "foreign_ask" in df_product.columns
                and df_product["foreign_ask"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["foreign_ask"],
                        mode="lines",
                        name=f"Log {log_number} {product} Foreign Ask",
                        visible="legendonly",
                        yaxis="y2",
                    )
                )

            if (
                "algo_bid" in df_product.columns
                and df_product["algo_bid"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["algo_bid"],
                        mode="lines",
                        name=f"Log {log_number} {product} Algo Bid",
                        visible="legendonly",
                        yaxis="y2",
                    )
                )

            if (
                "algo_ask" in df_product.columns
                and df_product["algo_ask"].notna().any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=df_product["timestamp"],
                        y=df_product["algo_ask"].round(),
                        mode="lines",
                        name=f"Log {log_number} {product} Algo Ask",
                        visible="legendonly",
                        yaxis="y2",
                    )
                )
            fig.add_trace(
                go.Scatter(
                    x=df_product["timestamp"],
                    y=df_product["mid_price"],
                    mode="lines",
                    name=f"Log {log_number} {product} Mid Price",
                    yaxis="y2",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df_product["timestamp"],
                    y=df_product["fair"],
                    mode="lines",
                    name=f"Log {log_number} {product} Fair Price",
                    yaxis="y2",
                )
            )

    elif compare_type == "trades volume":
        trades_df = pd.DataFrame(json.loads(trade_json))
        trades_df = trades_df[trades_df["symbol"] == product]
        trades_volume = trades_df.groupby("timestamp")["quantity"].sum()

        if log_number == 1:
            fig.add_trace(
                go.Bar(
                    x=trades_volume.index,
                    y=trades_volume.values,
                    name=f"Log {log_number} {product} Trade Volume",
                    hovertemplate="Timestamp: %{x}<br>Volume: %{y}",
                    text=trades_volume.values,
                )
            )
        else:
            fig.add_trace(
                go.Bar(
                    x=trades_volume.index,
                    y=trades_volume.values,
                    name=f"Log {log_number} {product} Trade Volume",
                    hovertemplate="Timestamp: %{x}<br>Volume: %{y}",
                    text=trades_volume.values,
                )
            )


def get_df_orderbook(df, timestamp):
    df_ob = df.copy()
    df_ob.index = df_ob["timestamp"]
    data = df_ob.loc[timestamp]
    min_bid = (
        round(min(data["bid_price_1"], data["bid_price_2"], data["bid_price_3"])) - 1
    )
    max_bid = round(max(data["bid_price_1"], data["bid_price_2"], data["bid_price_3"]))
    min_ask = round(min(data["ask_price_1"], data["ask_price_2"], data["ask_price_3"]))
    max_ask = (
        round(max(data["ask_price_1"], data["ask_price_2"], data["ask_price_3"])) + 1
    )
    fair = round(data["fair"]) if pd.isna(data["fair"]) == False else data["fair"]
    price_rng = np.arange(min_bid, max_ask + 1, 1)
    if fair not in price_rng:
        fair_id = np.searchsorted(price_rng, fair)
        price_rng = np.insert(price_rng, fair_id, fair)

    j = 0
    i = 0
    while i < len(price_rng):
        if price_rng[i] not in [
            data["bid_price_1"],
            data["bid_price_2"],
            data["bid_price_3"],
            data["ask_price_1"],
            data["ask_price_2"],
            data["ask_price_3"],
            fair,
        ]:
            j += 1
        else:
            j = 0
        if j == 3:
            price_rng = np.delete(price_rng, i)
            price_rng = np.delete(price_rng, i - 1)
            price_rng = np.delete(price_rng, i - 2)
            price_rng = np.insert(price_rng, i - 2, -1)
            j = 0
            i -= 2
        i += 1

    df_orderbook = pd.DataFrame(
        columns=["bid", "price", "ask"], index=range(len(price_rng))
    )
    # price_rng = np.arange(round(data['mid_price']) - depth, round(data['mid_price']) + depth, 1)
    i = 0
    for price in np.flip(price_rng):
        if data["bid_price_1"] == price:
            df_orderbook.iloc[i] = {
                "bid": int(data["bid_volume_1"]),
                "price": price,
                "ask": 0,
            }
        elif data["bid_price_2"] == price:
            df_orderbook.iloc[i] = {
                "bid": int(data["bid_volume_2"]),
                "price": price,
                "ask": 0,
            }
        elif data["bid_price_3"] == price:
            df_orderbook.iloc[i] = {
                "bid": int(data["bid_volume_3"]),
                "price": price,
                "ask": 0,
            }
        elif data["ask_price_1"] == price:
            df_orderbook.iloc[i] = {
                "bid": 0,
                "price": price,
                "ask": int(data["ask_volume_1"]),
            }
        elif data["ask_price_2"] == price:
            df_orderbook.iloc[i] = {
                "bid": 0,
                "price": price,
                "ask": int(data["ask_volume_2"]),
            }
        elif data["ask_price_3"] == price:
            df_orderbook.iloc[i] = {
                "bid": 0,
                "price": price,
                "ask": int(data["ask_volume_3"]),
            }
        else:
            df_orderbook.iloc[i] = {"bid": 0, "price": price, "ask": 0}
        i += 1
    df_orderbook = df_orderbook.reset_index(drop=True)

    return df_orderbook


def orderbook_table(df, product, timestamp):
    max_timeframe = 1999000
    df_product = df[df["product"] == product]
    df_product.index = df_product["timestamp"]
    df_concat = get_df_orderbook(df_product, timestamp)
    fair = df_product["fair"].loc[timestamp]
    if pd.isna(fair):
        dt = dash_table.DataTable(
            id="orderbook",
            data=df_concat.to_dict("records"),
            columns=[{"id": c, "name": c} for c in df_concat.columns],
            fixed_rows={"headers": True},
            style_table={"height": "60vh"},
            style_data_conditional=[
                {
                    "if": {"filter_query": "{{{}}} > 0".format("bid")},
                    "backgroundColor": "rgb(189, 215, 231)",
                    "fontWeight": "bold",
                },
                {
                    "if": {"filter_query": "{{{}}} > 0".format("ask")},
                    "backgroundColor": "rgb(231, 189, 189)",
                    "fontWeight": "bold",
                },
                {
                    "if": {"filter_query": "{{{}}} < 0".format("price")},
                    "backgroundColor": "gray",
                    "color": "transparent",
                },
                {"if": {"column_id": "bid"}, "width": "30%"},
                {"if": {"column_id": "price"}, "width": "40%"},
                {"if": {"column_id": "ask"}, "width": "30%"},
            ],
            style_cell={
                "minWidth": 50,
                "maxWidth": 50,
                "width": 50,
                "border": "1px solid black",
            },
            style_cell_conditional=[
                {"if": {"column_id": c}, "textAlign": "center"}
                for c in ["bid", "price", "ask"]
            ],
        )

    else:
        fair = round(fair)
        dt = dash_table.DataTable(
            id="orderbook",
            data=df_concat.to_dict("records"),
            columns=[{"id": c, "name": c} for c in df_concat.columns],
            fixed_rows={"headers": True},
            style_table={"height": "60vh"},
            style_data_conditional=[
                {
                    "if": {"filter_query": "{{{}}} = {}".format("price", fair)},
                    "backgroundColor": "rgb(189, 231, 189)",
                    "fontWeight": "bold",
                },
                {
                    "if": {
                        "filter_query": "{{{}}} > 0 && {{{}}} != {}".format(
                            "bid", "price", fair
                        )
                    },
                    "backgroundColor": "rgb(189, 215, 231)",
                    "fontWeight": "bold",
                },
                {
                    "if": {
                        "filter_query": "{{{}}} > 0 && {{{}}} != {}".format(
                            "ask", "price", fair
                        )
                    },
                    "backgroundColor": "rgb(231, 189, 189)",
                    "fontWeight": "bold",
                },
                {
                    "if": {"filter_query": "{{{}}} < 0".format("price")},
                    "backgroundColor": "gray",
                    "color": "transparent",
                },
                {"if": {"column_id": "bid"}, "width": "30%"},
                {"if": {"column_id": "price"}, "width": "40%"},
                {"if": {"column_id": "ask"}, "width": "30%"},
            ],
            style_cell={
                "minWidth": 50,
                "maxWidth": 50,
                "width": 50,
                "border": "1px solid black",
            },
            style_cell_conditional=[
                {"if": {"column_id": c}, "textAlign": "center"}
                for c in ["bid", "price", "ask"]
            ],
        )
    return dt
