from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle
import numpy as np

class Trader:
    def init(self):
        pass

    def run(self, state: TradingState):
        result = {}
        traderData = ""


        result['AMETHYSTS'] = []
        if 'STARFRUIT' not in state.position.keys() or state.position.get('STARFRUIT', 0) == 0:
            result['STARFRUIT'] = [Order("STARFRUIT",  5042, 1)]
        else:
            result['STARFRUIT'] = []

        conversions = 1

        return result, conversions, traderData