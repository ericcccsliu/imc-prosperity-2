# lib.py

from dash import Dash, html, Input, Output, dash_table, dcc, State, ctx
import pandas as pd
import json
import io
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import threading
import re


def parse_product_list(log_file):
    with open(f"../data/{log_file}", "r") as file:
        file_content = file.read()
    sections = file_content.split("Sandbox logs:")[1].split("Activities log:")
    activities_log = sections[1].split("Trade History:")[0]
    df = pd.read_csv(io.StringIO(activities_log), sep=";", header=0)
    return df["product"].unique()


def calculate_fair(df):
    for product in df["product"].unique():
        if product == "AMETHYSTS":
            df.loc[df["product"] == product, "fair"] = 10000
        elif product == "STARFRUIT":
            df["mm_bid"] = df.apply(
                lambda x: (
                    x["bid_price_1"]
                    if x["bid_volume_1"] > 15
                    else (
                        x["bid_price_2"] if x["bid_volume_2"] > 15 else x["bid_price_3"]
                    )
                ),
                axis=1,
            )
            df["mm_ask"] = df.apply(
                lambda x: (
                    x["ask_price_1"]
                    if x["ask_volume_1"] > 15
                    else (
                        x["ask_price_2"] if x["ask_volume_2"] > 15 else x["ask_price_3"]
                    )
                ),
                axis=1,
            )
            df.loc[df["product"] == product, "fair"] = (df["mm_bid"] + df["mm_ask"]) / 2
            # Rolling Avg
            # df.loc[df['product'] == product, 'fair'] = df.loc[df['product'] == product, 'mid_price'].rolling(window=10, min_periods=1).mean()
        else:
            df.loc[df["product"] == product, "fair"] = (
                df["bid_price_1"] + df["ask_price_1"]
            ) / 2  # mid


def parse_log_file(log_file, product):
    with open(log_file, "r") as file:
        file_content = file.read()
    sections = file_content.split("Sandbox logs:")[1].split("Activities log:")
    activities_log = sections[1].split("Trade History:")[0]
    df = pd.read_csv(io.StringIO(activities_log), sep=";", header=0)
    if "fair" not in df.columns:
        calculate_fair(df)
    trade_json = pd.json_normalize(
        json.loads(sections[1].split("Trade History:")[1])
    ).to_json()
    sandbox_logs = []
    logs_data = sections[0].strip()
    start_index = 0
    while start_index < len(logs_data):
        if logs_data[start_index] == "{":
            end_index = logs_data.find("}", start_index) + 1
            log_entry = logs_data[start_index:end_index]
            sandbox_logs.append(json.loads(log_entry))
            start_index = end_index
        else:
            start_index += 1
    df_sandbox = pd.DataFrame(sandbox_logs)
    df_sandbox["product"] = "ORCHIDS"
    if "lambdaLog" in df_sandbox.columns:
        if df_sandbox["lambdaLog"].str.contains("IMPLIED_BID").any():
            df_sandbox['implied_bid'] = df_sandbox['lambdaLog'].apply(lambda x: float(re.search(r'IMPLIED_BID: (\d+\.\d+)', x).group(1)) if re.search(r'IMPLIED_BID: (\d+\.\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'implied_bid']], on=['timestamp', 'product'], how='left')
        if df_sandbox["lambdaLog"].str.contains("IMPLIED_ASK").any():
            df_sandbox['implied_ask'] = df_sandbox['lambdaLog'].apply(lambda x: float(re.search(r'IMPLIED_ASK: (\d+\.\d+)', x).group(1)) if re.search(r'IMPLIED_ASK: (\d+\.\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'implied_ask']], on=['timestamp', 'product'], how='left')
        if df_sandbox["lambdaLog"].str.contains("ORCHIDS_POSITION").any():
            df_sandbox['orchids_position'] = df_sandbox['lambdaLog'].apply(lambda x: int(re.search(r'ORCHIDS_POSITION: (-?\d+)', x).group(1)) if re.search(r'ORCHIDS_POSITION: (-?\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'orchids_position']], on=['timestamp', 'product'], how='left')
        elif df_sandbox["lambdaLog"].str.contains("ORCHIDS POSITION").any():
            df_sandbox['orchids_position'] = df_sandbox['lambdaLog'].apply(lambda x: int(re.search(r'ORCHIDS POSITION: (-?\d+)', x).group(1)) if re.search(r'ORCHIDS POSITION: (-?\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'orchids_position']], on=['timestamp', 'product'], how='left')
        if df_sandbox["lambdaLog"].str.contains("FOREIGN_BID").any():
            df_sandbox['foreign_bid'] = df_sandbox['lambdaLog'].apply(lambda x: float(re.search(r'FOREIGN_BID: (\d+\.\d+)', x).group(1)) if re.search(r'FOREIGN_BID: (\d+\.\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'foreign_bid']], on=['timestamp', 'product'], how='left')
        if df_sandbox["lambdaLog"].str.contains("FOREIGN_ASK").any():
            df_sandbox['foreign_ask'] = df_sandbox['lambdaLog'].apply(lambda x: float(re.search(r'FOREIGN_ASK: (\d+\.\d+)', x).group(1)) if re.search(r'FOREIGN_ASK: (\d+\.\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'foreign_ask']], on=['timestamp', 'product'], how='left')
        if df_sandbox["lambdaLog"].str.contains("ALGO_BID").any():
            df_sandbox['algo_bid'] = df_sandbox['lambdaLog'].apply(lambda x: float(re.search(r'ALGO_BID: (\d+\.\d+)', x).group(1)) if re.search(r'ALGO_BID: (\d+\.\d+)', x) else 
                                                                             float(re.search(r'ALGO_BID: (\d+)', x).group(1)) if re.search(r'ALGO_BID: (\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'algo_bid']], on=['timestamp', 'product'], how='left')
        if df_sandbox["lambdaLog"].str.contains("ALGO_ASK").any():
            df_sandbox['algo_ask'] = df_sandbox['lambdaLog'].apply(lambda x: float(re.search(r'ALGO_ASK: (\d+\.\d+)', x).group(1)) if re.search(r'ALGO_ASK: (\d+\.\d+)', x) else 
                                                                             float(re.search(r'ALGO_ASK: (\d+)', x).group(1)) if re.search(r'ALGO_ASK: (\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'algo_ask']], on=['timestamp', 'product'], how='left')
        if  df_sandbox["lambdaLog"].str.contains("IMPORT_TARIFF").any():
            df_sandbox['import_tariff'] = df_sandbox['lambdaLog'].apply(lambda x: float(re.search(r'IMPORT_TARIFF: (-?\d+\.\d+)', x).group(1)) if re.search(r'IMPORT_TARIFF: (-?\d+\.\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'import_tariff']], on=['timestamp', 'product'], how='left')
        if  df_sandbox["lambdaLog"].str.contains("TRANSPORT_FEES").any():
            df_sandbox['transport_fees'] = df_sandbox['lambdaLog'].apply(lambda x: float(re.search(r'TRANSPORT_FEES: (\d+\.\d+)', x).group(1)) if re.search(r'TRANSPORT_FEES: (\d+\.\d+)', x) else None)
            df = df.merge(df_sandbox[['timestamp', 'product', 'transport_fees']], on=['timestamp', 'product'], how='left')
    return df, trade_json, df_sandbox.to_json()
