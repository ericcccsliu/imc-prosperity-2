from datamodel import OrderDepth, UserId, TradingState, Order, ConversionObservation
from typing import List
import jsonpickle
import numpy as np
import math


class Product:
    AMETHYSTS = "AMETHYSTS"
    STARFRUIT = "STARFRUIT"
    ORCHIDS = "ORCHIDS"
    GIFT_BASKET = "GIFT_BASKET"
    CHOCOLATE = "CHOCOLATE"
    STRAWBERRIES = "STRAWBERRIES"
    ROSES = "ROSES"


PARAMS = {
    Product.ROSES: {"take_orders_with_min_volume": 0, "take_orders_with_max_volume": 35}
}


class Trader:
    def __init__(self, params=None):
        if params is None:
            params = PARAMS
        self.params = params

        self.LIMIT = {Product.ROSES: 60}

    def run(self, state: TradingState):
        traderObject = {}
        if state.traderData != None and state.traderData != "":
            traderObject = jsonpickle.decode(state.traderData)

        result = {}
        conversions = 0

        if Product.ROSES in self.params and Product.ROSES in state.order_depths:
            roses_params = self.params[Product.ROSES]
            roses_limit = self.LIMIT[Product.ROSES]

            roses_position = (
                state.position[Product.ROSES] if Product.ROSES in state.position else 0
            )

            roses_order_depth = state.order_depths[Product.ROSES]

            best_bid = max(roses_order_depth.buy_orders.keys())
            best_bid_volume = roses_order_depth.buy_orders[best_bid]

            best_ask = min(roses_order_depth.sell_orders.keys())
            best_ask_volume = abs(roses_order_depth.sell_orders[best_ask])

            roses_orders = []
            if (
                best_bid_volume >= roses_params["take_orders_with_min_volume"]
                and best_bid_volume <= roses_params["take_orders_with_max_volume"]
            ):
                # sell to best bid
                trade_volume = min(best_bid_volume, roses_limit + roses_position)
                if trade_volume > 0:
                    roses_orders.append(Order(Product.ROSES, best_bid, -1* trade_volume))
            elif (
                best_ask_volume >= roses_params["take_orders_with_min_volume"]
                and best_ask_volume <= roses_params["take_orders_with_max_volume"]
            ):
                # buy from best ask
                trade_volume = min(best_ask_volume, roses_limit - roses_position)
                if trade_volume > 0: 
                    roses_orders.append(Order(Product.ROSES, best_ask, trade_volume))

            result[Product.ROSES] = roses_orders

        traderData = jsonpickle.encode(traderObject)

        return result, conversions, traderData
