from typing import List
import jsonpickle
from datamodel import OrderDepth, UserId, TradingState, Order, ConversionObservation
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


PARAMS = {Product.GIFT_BASKET: {"min_width": 1, "max_width": 8, "mm_min_volume": 10}}


class Trader:
    def __init__(self, params=None):
        if params is None:
            params = PARAMS
        self.params = params

        self.LIMIT = {Product.GIFT_BASKET: 60}

    def run(self, state: TradingState):
        traderObject = {}
        if state.traderData != None and state.traderData != "":
            traderObject = jsonpickle.decode(state.traderData)

        result = {}
        conversions = 0

        if (
            Product.GIFT_BASKET in self.params
            and Product.GIFT_BASKET in state.order_depths
        ):
            basket_params = self.params[Product.GIFT_BASKET]
            basket_limit = self.LIMIT[Product.GIFT_BASKET]

            basket_position = (
                state.position[Product.GIFT_BASKET]
                if Product.GIFT_BASKET in state.position
                else 0
            )

            basket_order_depth = state.order_depths[Product.GIFT_BASKET]

            mm_bids = [
                level
                for level in basket_order_depth.buy_orders.keys()
                if abs(basket_order_depth.buy_orders[level]) >= basket_params["mm_min_volume"]
            ]
            mm_asks = [
                level
                for level in basket_order_depth.sell_orders.keys()
                if abs(basket_order_depth.sell_orders[level]) >= basket_params["mm_min_volume"]
            ]
            if len(mm_bids) > 0 and len(mm_asks) > 0:
                best_mm_bid = max(mm_bids)
                best_mm_ask = min(mm_asks)
                # truncate
                mm_mid = int((best_mm_bid + best_mm_ask)/2)

                num_levels = basket_params['max_width'] - basket_params['min_width'] + 1
                num_buy_levels = min(num_levels, basket_limit - basket_position)
                num_sell_levels = min(num_levels, basket_limit + basket_position)

                basket_orders = []
                for level in range(1, num_buy_levels + 1):
                    basket_orders.append(Order(Product.GIFT_BASKET, mm_mid - level, 1))
                for level in range(1, num_sell_levels + 1):
                    basket_orders.append(Order(Product.GIFT_BASKET, mm_mid + level, -1))
                
                result[Product.GIFT_BASKET] = basket_orders
        traderData = jsonpickle.encode(traderObject)

        return result, conversions, traderData
