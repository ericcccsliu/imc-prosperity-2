import json
import os
import pandas as pd

class Parser():
    def __init__(self, file_path, flatten = True, save_json = False):
        self.file_path = file_path
        self.save_json = save_json
        self.flatten = flatten
        self.log = self.convert_log()

    def convert_log(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} does not exist")
        with open(self.file_path, 'r') as file:
            log_data = file.read()

        log_data = log_data.split("\n")
        arr_data = []
        json_str = ""
        for line in log_data:
            line.strip()
            if line == '{':
                json_str = line
            elif line == '}':
                json_str += line
                arr_data.append(json.loads(json_str))
                json_str = ""
            else:
                json_str += line
    
        for i in range(len(arr_data)):
            arr_data[i] = {**arr_data[i] , **self.process_log(json.loads(arr_data[i]['lambdaLog']))}
            del arr_data[i]['lambdaLog']
        
        if self.flatten:
            flatten_data = []
            for log in arr_data:
                for listing in log['listings']:
                    fdl = {}
                    fdl['timestamp'] = log['timestamp']
                    fdl['listing'] = listing
                    fdl['orderDepths'] = log['orderDepths'][listing] if listing in log['orderDepths'] else None
                    fdl['midPrice'] = log['midPrice'][listing] if listing in log['midPrice'] else None
                    fdl['orders'] = self.flatten_orders(log['orders'], listing)
                    fdl['ownTrades'] = self.flatten_trades(log['ownTrades'], listing)
                    fdl['marketTrades'] = self.flatten_trades(log['marketTrades'], listing)
                    fdl['position'] = log['position'][listing] if listing in log['position'] else None
                    fdl['observations'] = log['observations']
                    fdl['conversions'] = log['conversions']
                    fdl['traderData'] = log['traderData']
                    flatten_data.append(fdl)
            
            arr_data = flatten_data        

        if self.save_json:
            with open(self.file_path.replace('.log', '.json'), 'w') as json_file:
                json.dump(arr_data, json_file)
        return arr_data

    def process_log(self, log):
        output = {}
        output['timestamp'] = log[0][0]
        output['traderData'] = log[0][1]
        output['listings'] = [x[0] for x in log[0][2]]
        output['orderDepths'] = log[0][3]
        output['midPrice'] = self._set_midPrice(output['orderDepths'])
        output['orders'] = log[1]
        output['ownTrades'] = log[0][4]
        output['marketTrades'] = log[0][5]
        output['position'] = log[0][6]
        output['observations'] = log[0][7]
        output['conversions'] = log[2]
        output['traderData'] = log[3]

        return output

    def _set_midPrice(self, orderDepths):
        midPrice = {}
        for listing in orderDepths.keys():
            high_bid = float(max(orderDepths[listing][0].keys()))
            low_ask = float(min(orderDepths[listing][1].keys()))
            midPrice[listing] = (high_bid + low_ask) / 2
        return midPrice

    def get_log(self):
        return self.log
    
    def get_pd(self, flatten = False):
        if flatten:
            return
        else:
            return pd.json_normalize(self.log)
    
    def flatten_orders(self, orders, listing):
        flatten_order = []
        for order in orders:
            if order[0] == listing:
                new_order = {}
                new_order['price'] = order[1]
                new_order['quantity'] = order[2]
                flatten_order.append(new_order)
        return flatten_order   
    
    def flatten_trades(self, trades, listing):
        flatten_trades = []
        for trade in trades:
            if trade[0] == listing:
                new_trade = {}
                new_trade['price'] = trade[1]
                new_trade['quantity'] = trade[2]
                new_trade['buyer'] = trade[3]
                new_trade['seller'] = trade[4]
                new_trade['timestamp'] = trade[5]
                flatten_trades.append(new_trade)
        return flatten_trades
