from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle
import numpy as np

class Trader:
    def __init__(self):
        pass

    def run(self, state: TradingState):
        result = {}
        traderData = ""
    
        print(state.observations)
        
        result['AMETHYSTS'] = []
        result['STARFRUIT'] = []
        result['ORCHIDS'] = []

        conversions = 0

        return result, conversions, traderData

    
