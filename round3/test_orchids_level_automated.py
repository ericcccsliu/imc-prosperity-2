from datamodel import OrderDepth, UserId, TradingState, Order, ConversionObservation
from typing import List
import string
import jsonpickle
import numpy as np
import math


class Product:
    ORCHIDS = "ORCHIDS"


PARAMS = {
    Product.ORCHIDS: {
        "edge": 2
    },
}


class Trader:
    def __init__(self, params=None):
        if params is None:
            params = PARAMS
        self.params = params

        self.LIMIT = {
            Product.ORCHIDS: 100,
        }

    def orchids_implied_bid_ask(
        self,
        observation: ConversionObservation,
    ) -> (float, float):
        return observation.bidPrice - observation.exportTariff - observation.transportFees - 0.1, observation.askPrice + observation.importTariff + observation.transportFees


    def orchids_arb_clear(self, position: int) -> int:
        conversions = -position
        return conversions

    def orchids_arb_make(
        self,
        observation: ConversionObservation,
        edge: float,
    ) -> (List[Order], int, int):
        orders: List[Order] = []
        position_limit = self.LIMIT[Product.ORCHIDS]

        implied_bid, implied_ask = self.orchids_implied_bid_ask(observation)
        foreign_mid = (observation.askPrice + observation.bidPrice) / 2
        ask = round(observation.askPrice) - edge

        print(f"IMPLIED_BID: {implied_bid}")
        print(f"IMPLIED_ASK: {implied_ask}")
        print(f"FOREIGN_ASK: {observation.askPrice}")
        print(f"FOREIGN_BID: {observation.bidPrice}")
        print(f"FOREIGN_MID: {(observation.askPrice + observation.bidPrice)/2}")
        print(f"TRANSPORT_FEES: {observation.transportFees}")
        print(f"EXPORT_TARIFF: {observation.exportTariff}")
        print(f"IMPORT_TARIFF: {observation.importTariff}")
        print(f"SUNLIGHT: {observation.sunlight}")
        print(f"HUMIDITY: {observation.humidity}")

        sell_quantity = position_limit
        if sell_quantity > 0:
            orders.append(
                Order(Product.ORCHIDS, round(ask), -sell_quantity)
            )  # Sell order

        return orders,

    def run(self, state: TradingState):
        traderObject = {}
        if state.traderData != None and state.traderData != "":
            traderObject = jsonpickle.decode(state.traderData)

        result = {}
        conversions = 0

        if Product.ORCHIDS in self.params and Product.ORCHIDS in state.order_depths:
            orchids_position = (
                state.position[Product.ORCHIDS]
                if Product.ORCHIDS in state.position
                else 0
            )
            edge = self.params[Product.ORCHIDS]['edge']

            conversions = self.orchids_arb_clear(orchids_position)

            orchids_position = 0

            orchids_make_orders, = self.orchids_arb_make(
                state.observations.conversionObservations[Product.ORCHIDS],
                edge,
            )

            result[Product.ORCHIDS] =  orchids_make_orders

        traderData = jsonpickle.encode(traderObject)

        return result, conversions, traderData
