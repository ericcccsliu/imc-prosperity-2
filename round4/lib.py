import pandas as pd
import json
import re
import io

def parse_log_file(log_file):
    with open(log_file, "r") as file:
        file_content = file.read()
    sections = file_content.split("Sandbox logs:")[1].split("Activities log:")
    activities_log = sections[1].split("Trade History:")[0]
    df = pd.read_csv(io.StringIO(activities_log), sep=";", header=0)
    # if "fair" not in df.columns:
        # calculate_fair(df)
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

    return df, trade_json, df_sandbox.to_json()