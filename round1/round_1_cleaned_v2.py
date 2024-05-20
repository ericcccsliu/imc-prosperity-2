# v2 Updates:
# 1. Amethysts making order width >= 2, except when abs(position) >= 10


from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle
import numpy as np
import math

class Product:
    AMETHYSTS = "AMETHYSTS"
    STARFRUIT = "STARFRUIT"

class Trader:
    def __init__(self):
        self.starfruit_prices = []
        self.starfruit_vwap = []
        self.starfruit_mmmid = []

        self.LIMIT = {
            Product.AMETHYSTS: 20,
            Product.STARFRUIT: 20
        }

    # Returns buy_order_volume, sell_order_volume
    def take_best_orders(self, product: str, fair_value: int, take_width:float, orders: List[Order], order_depth: OrderDepth, position: int, buy_order_volume: int, sell_order_volume: int, prevent_adverse: bool = False, adverse_volume: int = 0) -> (int, int):
        position_limit = self.LIMIT[product]
        if len(order_depth.sell_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_amount = -1*order_depth.sell_orders[best_ask]
            
            if best_ask <= fair_value - take_width:
                quantity = min(best_ask_amount, position_limit - position) # max amt to buy 
                if quantity > 0:
                    orders.append(Order(product, best_ask, quantity)) 
                    buy_order_volume += quantity

        if len(order_depth.buy_orders) != 0:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_amount = order_depth.buy_orders[best_bid]
            if best_bid >= fair_value + take_width:
                quantity = min(best_bid_amount, position_limit + position) # should be the max we can sell 
                if quantity > 0:
                    orders.append(Order(product, best_bid, -1 * quantity))
                    sell_order_volume += quantity

        return buy_order_volume, sell_order_volume
    
    def take_best_orders_with_adverse(self, product: str, fair_value: int, take_width: float, orders: List[Order], order_depth: OrderDepth, position: int, buy_order_volume: int, sell_order_volume: int, adverse_volume: int) -> (int, int):
        
        position_limit = self.LIMIT[product]
        if len(order_depth.sell_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_amount = -1*order_depth.sell_orders[best_ask]
            if abs(best_ask_amount) <= adverse_volume:
                if best_ask <= fair_value - take_width:
                    quantity = min(best_ask_amount, position_limit - position) # max amt to buy 
                    if quantity > 0:
                        orders.append(Order(product, best_ask, quantity)) 
                        buy_order_volume += quantity

        if len(order_depth.buy_orders) != 0:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_amount = order_depth.buy_orders[best_bid]
            if abs(best_bid_amount) <= adverse_volume:
                if best_bid >= fair_value + take_width:
                    quantity = min(best_bid_amount, position_limit + position) # should be the max we can sell 
                    if quantity > 0:
                        orders.append(Order(product, best_bid, -1 * quantity))
                        sell_order_volume += quantity

        return buy_order_volume, sell_order_volume

    def market_make(self, product: str, orders: List[Order], bid: int, ask: int, position: int, buy_order_volume: int, sell_order_volume: int) -> (int, int):
        buy_quantity = self.LIMIT[product] - (position + buy_order_volume)
        if buy_quantity > 0:
            orders.append(Order(product, bid, buy_quantity))  # Buy order

        sell_quantity = self.LIMIT[product] + (position - sell_order_volume)
        if sell_quantity > 0:
            orders.append(Order(product, ask, -sell_quantity))  # Sell order
        return buy_order_volume, sell_order_volume
    
    def clear_position_order(self, product: str, fair_value: float, width: int, orders: List[Order], order_depth: OrderDepth, position: int, buy_order_volume: int, sell_order_volume: int) -> List[Order]:
        
        position_after_take = position + buy_order_volume - sell_order_volume
        fair = round(fair_value)
        fair_for_bid = math.floor(fair_value)
        fair_for_ask = math.ceil(fair_value)
        # fair_for_ask = fair_for_bid = fair

        buy_quantity = self.LIMIT[product] - (position + buy_order_volume)
        sell_quantity = self.LIMIT[product] + (position - sell_order_volume)

        if position_after_take > 0:
            if fair_for_ask in order_depth.buy_orders.keys():
                clear_quantity = min(order_depth.buy_orders[fair_for_ask], position_after_take)
                # clear_quantity = position_after_take
                sent_quantity = min(sell_quantity, clear_quantity)
                orders.append(Order(product, fair_for_ask, -abs(sent_quantity)))
                sell_order_volume += abs(sent_quantity)

        if position_after_take < 0:
            if fair_for_bid in order_depth.sell_orders.keys():
                clear_quantity = min(abs(order_depth.sell_orders[fair_for_bid]), abs(position_after_take))
                # clear_quantity = abs(position_after_take)
                sent_quantity = min(buy_quantity, clear_quantity)
                orders.append(Order(product, fair_for_bid, abs(sent_quantity)))
                buy_order_volume += abs(sent_quantity)
    
        return buy_order_volume, sell_order_volume

    def starfruit_fair_value(self, order_depth: OrderDepth, timespan: int) -> float:
        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())
            filtered_ask = [price for price in order_depth.sell_orders.keys() if abs(order_depth.sell_orders[price]) >= 15]
            filtered_bid = [price for price in order_depth.buy_orders.keys() if abs(order_depth.buy_orders[price]) >= 15]
            mm_ask = min(filtered_ask) if len(filtered_ask) > 0 else best_ask
            mm_bid = max(filtered_bid) if len(filtered_bid) > 0 else best_bid

            mmmid_price = (mm_ask + mm_bid) / 2
            self.starfruit_prices.append(mmmid_price)

            volume = -1 * order_depth.sell_orders[best_ask] + order_depth.buy_orders[best_bid]
            vwap = (best_bid * (-1) * order_depth.sell_orders[best_ask] + best_ask * order_depth.buy_orders[best_bid]) / volume
            self.starfruit_vwap.append({"vol": volume, "vwap": vwap})

            if len(self.starfruit_vwap) > timespan:
                self.starfruit_vwap.pop(0)

            if len(self.starfruit_prices) > timespan:
                self.starfruit_prices.pop(0)

            return mmmid_price
        return None
    
    def make_amethyst_orders(self, order_depth: OrderDepth, fair_value: int, position: int, buy_order_volume: int, sell_order_volume: int, volume_limit: int) -> (List[Order], int, int):
        orders: List[Order] = []
        baaf = min([price for price in order_depth.sell_orders.keys() if price > fair_value + 1])
        bbbf = max([price for price in order_depth.buy_orders.keys() if price < fair_value - 1])
        
        if baaf <= fair_value + 2:
            if position <= volume_limit:
                baaf = fair_value + 3 # still want edge 2 if position is not a concern
        
        if bbbf >= fair_value - 2:
            if position >= -volume_limit:
                bbbf = fair_value - 3 # still want edge 2 if position is not a concern

        buy_order_volume, sell_order_volume = self.market_make(Product.AMETHYSTS, orders, bbbf + 1, baaf - 1, position, buy_order_volume, sell_order_volume)
        return orders, buy_order_volume, sell_order_volume
    
    def take_orders(self, product: str, order_depth: OrderDepth, fair_value: float, take_width: float, position: int, prevent_adverse: bool = False, adverse_volume: int = 0) -> (List[Order], int, int):
        orders: List[Order] = []
        buy_order_volume = 0
        sell_order_volume = 0

        if prevent_adverse:
            buy_order_volume, sell_order_volume = self.take_best_orders_with_adverse(product, fair_value, take_width, orders, order_depth, position, buy_order_volume, sell_order_volume, adverse_volume)
        else: 
            buy_order_volume, sell_order_volume = self.take_best_orders(product, fair_value, take_width, orders, order_depth, position, buy_order_volume, sell_order_volume)
        return orders, buy_order_volume, sell_order_volume

    def clear_orders(self, product: str, order_depth: OrderDepth, fair_value: float, clear_width: int, position: int, buy_order_volume: int, sell_order_volume: int) -> (List[Order], int, int):
        orders: List[Order] = []
        buy_order_volume, sell_order_volume = self.clear_position_order(product, fair_value, clear_width, orders, order_depth, position, buy_order_volume, sell_order_volume)
        return orders, buy_order_volume, sell_order_volume


    def make_starfruit_orders(self, order_depth: OrderDepth, fair_value: float, position: int, buy_order_volume: int, sell_order_volume: int) -> (List[Order], int, int):
        orders: List[Order] = []
        aaf = [price for price in order_depth.sell_orders.keys() if price > fair_value + 1]
        bbf = [price for price in order_depth.buy_orders.keys() if price < fair_value - 1]
        baaf = min(aaf) if len(aaf) > 0 else fair_value + 2
        bbbf = max(bbf) if len(bbf) > 0 else fair_value - 2
        buy_order_volume, sell_order_volume = self.market_make(Product.STARFRUIT, orders, bbbf + 1, baaf - 1, position, buy_order_volume, sell_order_volume)
        
        return orders, buy_order_volume, sell_order_volume
    
    def run(self, state: TradingState):
        result = {}

        amethyst_fair_value = 10000  # Participant should calculate this value
        amethyst_take_width = 1
        amethyst_clear_width = 1
        amethyst_position_limit = 20
        amethyst_volume_limit = 10

        starfruit_make_width = 3.5
        starfruit_take_width = 1
        starfruit_clear_width = 2
        starfruit_position_limit = 20
        starfruit_timespan = 10

        if Product.AMETHYSTS in state.order_depths:
            amethyst_position = state.position[Product.AMETHYSTS] if Product.AMETHYSTS in state.position else 0
            amethyst_take_orders, buy_order_volume, sell_order_volume = self.take_orders(Product.AMETHYSTS, state.order_depths[Product.AMETHYSTS], amethyst_fair_value, amethyst_take_width, amethyst_position)
            amethyst_clear_orders, buy_order_volume, sell_order_volume = self.clear_orders(Product.AMETHYSTS, state.order_depths[Product.AMETHYSTS], amethyst_fair_value, amethyst_clear_width, amethyst_position, buy_order_volume, sell_order_volume)
            amethyst_make_orders, _, _ = self.make_amethyst_orders(state.order_depths[Product.AMETHYSTS], amethyst_fair_value, amethyst_position, buy_order_volume, sell_order_volume, amethyst_volume_limit)
            result[Product.AMETHYSTS] = amethyst_take_orders + amethyst_clear_orders + amethyst_make_orders

        if Product.STARFRUIT in state.order_depths:
            starfruit_position = state.position[Product.STARFRUIT] if Product.STARFRUIT in state.position else 0
            starfruit_fair_value = self.starfruit_fair_value(state.order_depths[Product.STARFRUIT], starfruit_timespan)
            starfruit_take_orders, buy_order_volume, sell_order_volume = self.take_orders(Product.STARFRUIT, state.order_depths[Product.STARFRUIT], starfruit_fair_value, starfruit_take_width, starfruit_position, True, 20)
            starfruit_clear_orders, buy_order_volume, sell_order_volume = self.clear_orders(Product.STARFRUIT, state.order_depths[Product.STARFRUIT], starfruit_fair_value, starfruit_clear_width, starfruit_position, buy_order_volume, sell_order_volume)
            starfruit_make_orders, _, _ = self.make_starfruit_orders(state.order_depths[Product.STARFRUIT], starfruit_fair_value, starfruit_position, buy_order_volume, sell_order_volume)
            result[Product.STARFRUIT] = starfruit_take_orders + starfruit_clear_orders + starfruit_make_orders

        traderData = jsonpickle.encode({"starfruit_prices": self.starfruit_prices, "starfruit_vwap": self.starfruit_vwap})

        conversions = 1

        return result, conversions, traderData

    
