from datamodel import OrderDepth, UserId, TradingState, Order, ConversionObservation
from typing import List, Dict, Any
import string
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
    SYNTHETIC = "SYNTHETIC"
    SPREAD = "SPREAD"
    COCONUT = "COCONUT"
    COCONUT_COUPON = "COCONUT_COUPON"


PARAMS = {
    Product.AMETHYSTS: {
        "fair_value": 10000,
        "take_width": 1,
        "clear_width": 0.5,
        "volume_limit": 0,
    },
    Product.STARFRUIT: {
        "take_width": 1,
        "clear_width": 0,
        "prevent_adverse": True,
        "adverse_volume": 15,
        "reversion_beta": -0.229,
        "starfruit_min_edge": 2,
    },
    Product.ORCHIDS: {
        "gift_basket_beta": -5.2917,
        "returns_threshold": 0.01,
        "clear_threshold": 0,
        "make_probability": 0.800,
    },
    Product.SPREAD: {
        "default_spread_mean": 379.50439988484239,
        "default_spread_std": 76.07966,
        "spread_std_window": 45,
        "zscore_threshold": 7,
        "target_position": 58,
    },
    Product.COCONUT_COUPON: {
        "mean_volatility": 0.15959997370608378,
        "threshold": 0.00163,
        "strike": 10000,
        "starting_time_to_expiry": 247 / 250,
        "std_window": 30,
        "zscore_threshold": 5.1
    },
}

BASKET_WEIGHTS = {
    Product.CHOCOLATE: 4,
    Product.STRAWBERRIES: 6,
    Product.ROSES: 1,
}

from math import log, sqrt, exp
from statistics import NormalDist


class BlackScholes:
    @staticmethod
    def black_scholes_call(spot, strike, time_to_expiry, volatility):
        d1 = (
            log(spot) - log(strike) + (0.5 * volatility * volatility) * time_to_expiry
        ) / (volatility * sqrt(time_to_expiry))
        d2 = d1 - volatility * sqrt(time_to_expiry)
        call_price = spot * NormalDist().cdf(d1) - strike * NormalDist().cdf(d2)
        return call_price

    @staticmethod
    def black_scholes_put(spot, strike, time_to_expiry, volatility):
        d1 = (log(spot / strike) + (0.5 * volatility * volatility) * time_to_expiry) / (
            volatility * sqrt(time_to_expiry)
        )
        d2 = d1 - volatility * sqrt(time_to_expiry)
        put_price = strike * NormalDist().cdf(-d2) - spot * NormalDist().cdf(-d1)
        return put_price

    @staticmethod
    def delta(spot, strike, time_to_expiry, volatility):
        d1 = (
            log(spot) - log(strike) + (0.5 * volatility * volatility) * time_to_expiry
        ) / (volatility * sqrt(time_to_expiry))
        return NormalDist().cdf(d1)

    @staticmethod
    def gamma(spot, strike, time_to_expiry, volatility):
        d1 = (
            log(spot) - log(strike) + (0.5 * volatility * volatility) * time_to_expiry
        ) / (volatility * sqrt(time_to_expiry))
        return NormalDist().pdf(d1) / (spot * volatility * sqrt(time_to_expiry))

    @staticmethod
    def vega(spot, strike, time_to_expiry, volatility):
        d1 = (
            log(spot) - log(strike) + (0.5 * volatility * volatility) * time_to_expiry
        ) / (volatility * sqrt(time_to_expiry))
        # print(f"d1: {d1}")
        # print(f"vol: {volatility}")
        # print(f"spot: {spot}")
        # print(f"strike: {strike}")
        # print(f"time: {time_to_expiry}")
        return NormalDist().pdf(d1) * (spot * sqrt(time_to_expiry)) / 100

    @staticmethod
    def implied_volatility(
        call_price, spot, strike, time_to_expiry, max_iterations=200, tolerance=1e-10
    ):
        low_vol = 0.01
        high_vol = 1.0
        volatility = (low_vol + high_vol) / 2.0  # Initial guess as the midpoint
        for _ in range(max_iterations):
            estimated_price = BlackScholes.black_scholes_call(
                spot, strike, time_to_expiry, volatility
            )
            diff = estimated_price - call_price
            if abs(diff) < tolerance:
                break
            elif diff > 0:
                high_vol = volatility
            else:
                low_vol = volatility
            volatility = (low_vol + high_vol) / 2.0
        return volatility


class Trader:
    def __init__(self, params=None):
        if params is None:
            params = PARAMS
        self.params = params

        self.LIMIT = {
            Product.AMETHYSTS: 20,
            Product.STARFRUIT: 20,
            Product.ORCHIDS: 100,
            Product.GIFT_BASKET: 60,
            Product.CHOCOLATE: 250,
            Product.STRAWBERRIES: 350,
            Product.ROSES: 60,
            Product.COCONUT: 300,
            Product.COCONUT_COUPON: 600,
        }

    # Returns buy_order_volume, sell_order_volume
    def take_best_orders(
        self,
        product: str,
        fair_value: int,
        take_width: float,
        orders: List[Order],
        order_depth: OrderDepth,
        position: int,
        buy_order_volume: int,
        sell_order_volume: int,
        prevent_adverse: bool = False,
        adverse_volume: int = 0,
    ) -> (int, int):
        position_limit = self.LIMIT[product]
        if len(order_depth.sell_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_amount = -1 * order_depth.sell_orders[best_ask]

            if best_ask <= fair_value - take_width:
                quantity = min(
                    best_ask_amount, position_limit - position
                )  # max amt to buy
                if quantity > 0:
                    orders.append(Order(product, best_ask, quantity))
                    buy_order_volume += quantity
                    order_depth.sell_orders[best_ask] += quantity
                    if order_depth.sell_orders[best_ask] == 0:
                        del order_depth.sell_orders[best_ask]

        if len(order_depth.buy_orders) != 0:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_amount = order_depth.buy_orders[best_bid]
            if best_bid >= fair_value + take_width:
                quantity = min(
                    best_bid_amount, position_limit + position
                )  # should be the max we can sell
                if quantity > 0:
                    orders.append(Order(product, best_bid, -1 * quantity))
                    sell_order_volume += quantity
                    order_depth.buy_orders[best_bid] -= quantity
                    if order_depth.buy_orders[best_bid] == 0:
                        del order_depth.buy_orders[best_bid]
        return buy_order_volume, sell_order_volume

    def take_best_orders_with_adverse(
        self,
        product: str,
        fair_value: int,
        take_width: float,
        orders: List[Order],
        order_depth: OrderDepth,
        position: int,
        buy_order_volume: int,
        sell_order_volume: int,
        adverse_volume: int,
    ) -> (int, int):

        position_limit = self.LIMIT[product]
        if len(order_depth.sell_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_amount = -1 * order_depth.sell_orders[best_ask]
            if abs(best_ask_amount) <= adverse_volume:
                if best_ask <= fair_value - take_width:
                    quantity = min(
                        best_ask_amount, position_limit - position
                    )  # max amt to buy
                    if quantity > 0:
                        orders.append(Order(product, best_ask, quantity))
                        buy_order_volume += quantity
                        order_depth.sell_orders[best_ask] += quantity
                        if order_depth.sell_orders[best_ask] == 0:
                            del order_depth.sell_orders[best_ask]

        if len(order_depth.buy_orders) != 0:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_amount = order_depth.buy_orders[best_bid]
            if abs(best_bid_amount) <= adverse_volume:
                if best_bid >= fair_value + take_width:
                    quantity = min(
                        best_bid_amount, position_limit + position
                    )  # should be the max we can sell
                    if quantity > 0:
                        orders.append(Order(product, best_bid, -1 * quantity))
                        sell_order_volume += quantity
                        order_depth.buy_orders[best_bid] -= quantity
                        if order_depth.buy_orders[best_bid] == 0:
                            del order_depth.buy_orders[best_bid]

        return buy_order_volume, sell_order_volume

    def market_make(
        self,
        product: str,
        orders: List[Order],
        bid: int,
        ask: int,
        position: int,
        buy_order_volume: int,
        sell_order_volume: int,
    ) -> (int, int):
        buy_quantity = self.LIMIT[product] - (position + buy_order_volume)
        if buy_quantity > 0:
            orders.append(Order(product, round(bid), buy_quantity))  # Buy order

        sell_quantity = self.LIMIT[product] + (position - sell_order_volume)
        if sell_quantity > 0:
            orders.append(Order(product, round(ask), -sell_quantity))  # Sell order
        return buy_order_volume, sell_order_volume

    def clear_position_order(
        self,
        product: str,
        fair_value: float,
        width: int,
        orders: List[Order],
        order_depth: OrderDepth,
        position: int,
        buy_order_volume: int,
        sell_order_volume: int,
    ) -> List[Order]:
        position_after_take = position + buy_order_volume - sell_order_volume
        fair_for_bid = round(fair_value - width)
        fair_for_ask = round(fair_value + width)

        buy_quantity = self.LIMIT[product] - (position + buy_order_volume)
        sell_quantity = self.LIMIT[product] + (position - sell_order_volume)

        if position_after_take > 0:
            # Aggregate volume from all buy orders with price greater than fair_for_ask
            clear_quantity = sum(
                volume
                for price, volume in order_depth.buy_orders.items()
                if price >= fair_for_ask
            )
            clear_quantity = min(clear_quantity, position_after_take)
            sent_quantity = min(sell_quantity, clear_quantity)
            if sent_quantity > 0:
                orders.append(Order(product, fair_for_ask, -abs(sent_quantity)))
                sell_order_volume += abs(sent_quantity)

        if position_after_take < 0:
            # Aggregate volume from all sell orders with price lower than fair_for_bid
            clear_quantity = sum(
                abs(volume)
                for price, volume in order_depth.sell_orders.items()
                if price <= fair_for_bid
            )
            clear_quantity = min(clear_quantity, abs(position_after_take))
            sent_quantity = min(buy_quantity, clear_quantity)
            if sent_quantity > 0:
                orders.append(Order(product, fair_for_bid, abs(sent_quantity)))
                buy_order_volume += abs(sent_quantity)

        return buy_order_volume, sell_order_volume

    def starfruit_fair_value(self, order_depth: OrderDepth, traderObject) -> float:
        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())
            filtered_ask = [
                price
                for price in order_depth.sell_orders.keys()
                if abs(order_depth.sell_orders[price])
                >= self.params[Product.STARFRUIT]["adverse_volume"]
            ]
            filtered_bid = [
                price
                for price in order_depth.buy_orders.keys()
                if abs(order_depth.buy_orders[price])
                >= self.params[Product.STARFRUIT]["adverse_volume"]
            ]
            mm_ask = min(filtered_ask) if len(filtered_ask) > 0 else None
            mm_bid = max(filtered_bid) if len(filtered_bid) > 0 else None
            if mm_ask == None or mm_bid == None:
                if traderObject.get("starfruit_last_price", None) == None:
                    mmmid_price = (best_ask + best_bid) / 2
                else:
                    mmmid_price = traderObject["starfruit_last_price"]
            else:
                mmmid_price = (mm_ask + mm_bid) / 2

            if traderObject.get("starfruit_last_price", None) != None:
                last_price = traderObject["starfruit_last_price"]
                last_returns = (mmmid_price - last_price) / last_price
                pred_returns = (
                    last_returns * self.params[Product.STARFRUIT]["reversion_beta"]
                )
                fair = mmmid_price + (mmmid_price * pred_returns)
            else:
                fair = mmmid_price
            traderObject["starfruit_last_price"] = mmmid_price
            return fair
        return None

    def make_amethyst_orders(
        self,
        order_depth: OrderDepth,
        fair_value: int,
        position: int,
        buy_order_volume: int,
        sell_order_volume: int,
        volume_limit: int,
    ) -> (List[Order], int, int):
        orders: List[Order] = []
        baaf = min(
            [
                price
                for price in order_depth.sell_orders.keys()
                if price > fair_value + 1
            ]
        )
        bbbf = max(
            [price for price in order_depth.buy_orders.keys() if price < fair_value - 1]
        )

        if baaf <= fair_value + 2:
            if position <= volume_limit:
                baaf = fair_value + 3  # still want edge 2 if position is not a concern

        if bbbf >= fair_value - 2:
            if position >= -volume_limit:
                bbbf = fair_value - 3  # still want edge 2 if position is not a concern

        buy_order_volume, sell_order_volume = self.market_make(
            Product.AMETHYSTS,
            orders,
            bbbf + 1,
            baaf - 1,
            position,
            buy_order_volume,
            sell_order_volume,
        )
        return orders, buy_order_volume, sell_order_volume

    def take_orders(
        self,
        product: str,
        order_depth: OrderDepth,
        fair_value: float,
        take_width: float,
        position: int,
        prevent_adverse: bool = False,
        adverse_volume: int = 0,
    ) -> (List[Order], int, int):
        orders: List[Order] = []
        buy_order_volume = 0
        sell_order_volume = 0

        if prevent_adverse:
            buy_order_volume, sell_order_volume = self.take_best_orders_with_adverse(
                product,
                fair_value,
                take_width,
                orders,
                order_depth,
                position,
                buy_order_volume,
                sell_order_volume,
                adverse_volume,
            )
        else:
            buy_order_volume, sell_order_volume = self.take_best_orders(
                product,
                fair_value,
                take_width,
                orders,
                order_depth,
                position,
                buy_order_volume,
                sell_order_volume,
            )
        return orders, buy_order_volume, sell_order_volume

    def clear_orders(
        self,
        product: str,
        order_depth: OrderDepth,
        fair_value: float,
        clear_width: int,
        position: int,
        buy_order_volume: int,
        sell_order_volume: int,
    ) -> (List[Order], int, int):
        orders: List[Order] = []
        buy_order_volume, sell_order_volume = self.clear_position_order(
            product,
            fair_value,
            clear_width,
            orders,
            order_depth,
            position,
            buy_order_volume,
            sell_order_volume,
        )
        return orders, buy_order_volume, sell_order_volume

    def make_starfruit_orders(
        self,
        order_depth: OrderDepth,
        fair_value: float,
        min_edge: float,
        position: int,
        buy_order_volume: int,
        sell_order_volume: int,
    ) -> (List[Order], int, int):
        orders: List[Order] = []
        aaf = [
            price
            for price in order_depth.sell_orders.keys()
            if price >= round(fair_value + min_edge)
        ]
        bbf = [
            price
            for price in order_depth.buy_orders.keys()
            if price <= round(fair_value - min_edge)
        ]
        baaf = min(aaf) if len(aaf) > 0 else round(fair_value + min_edge)
        bbbf = max(bbf) if len(bbf) > 0 else round(fair_value - min_edge)
        buy_order_volume, sell_order_volume = self.market_make(
            Product.STARFRUIT,
            orders,
            bbbf + 1,
            baaf - 1,
            position,
            buy_order_volume,
            sell_order_volume,
        )

        return orders, buy_order_volume, sell_order_volume

    def orchids_implied_bid_ask(
        self,
        observation: ConversionObservation,
    ) -> (float, float):
        return (
            observation.bidPrice - observation.exportTariff - observation.transportFees,
            observation.askPrice + observation.importTariff + observation.transportFees,
        )

    def orchids_arb_take(
        self,
        order_depth: OrderDepth,
        observation: ConversionObservation,
        position: int,
    ) -> (List[Order], int, int):
        orders: List[Order] = []
        position_limit = self.LIMIT[Product.ORCHIDS]
        buy_order_volume = 0
        sell_order_volume = 0
        if observation.implied_bid:
            implied_bid = observation.implied_bid
            implied_ask = observation.implied_ask
        else:
            implied_bid, implied_ask = self.orchids_implied_bid_ask(observation)

        buy_quantity = position_limit - position
        sell_quantity = position_limit + position

        ask = round(observation.askPrice) - 2

        if ask > implied_ask:
            edge = (ask - implied_ask) * self.params[Product.ORCHIDS][
                "make_probability"
            ]
        else:
            edge = 0

        for price in sorted(list(order_depth.sell_orders.keys())):
            if price > implied_bid - 0.1 - edge:
                break

            if price < implied_bid - 0.1 - edge:
                quantity = min(
                    abs(order_depth.sell_orders[price]), buy_quantity
                )  # max amount to buy
                if quantity > 0:
                    orders.append(Order(Product.ORCHIDS, round(price), quantity))
                    buy_order_volume += quantity

        for price in sorted(list(order_depth.buy_orders.keys()), reverse=True):
            if price < implied_ask + edge:
                break

            if price > implied_ask + edge:
                quantity = min(
                    abs(order_depth.buy_orders[price]), sell_quantity
                )  # max amount to sell
                if quantity > 0:
                    orders.append(Order(Product.ORCHIDS, round(price), -quantity))
                    sell_order_volume += quantity

        return orders, buy_order_volume, sell_order_volume

    def orchids_arb_clear(self, position: int) -> int:
        conversions = -position
        return conversions

    def orchids_arb_make(
        self,
        observation: ConversionObservation,
        position: int,
        buy_order_volume: int,
        sell_order_volume: int,
    ) -> (List[Order], int, int):
        orders: List[Order] = []
        position_limit = self.LIMIT[Product.ORCHIDS]

        # Implied Bid = observation.bidPrice - observation.exportTariff - observation.transportFees - 0.1
        # Implied Ask = observation.askPrice + observation.importTariff + observation.transportFees
        if observation.implied_bid:
            implied_bid = observation.implied_bid
            implied_ask = observation.implied_ask
        else:
            implied_bid, implied_ask = self.orchids_implied_bid_ask(observation)

        aggressive_ask = round(observation.askPrice) - 2
        aggressive_bid = round(observation.bidPrice) + 2

        if aggressive_bid < implied_bid - 0.1:
            bid = aggressive_bid
        else:
            bid = None

        if aggressive_ask >= implied_ask + 0.5:
            ask = aggressive_ask
        elif aggressive_ask + 1 >= implied_ask + 0.5:
            ask = aggressive_ask + 1
        else:
            ask = None

        # print(f"ALGO_ASK: {round(ask)}")
        # print(f"IMPLIED_BID: {implied_bid}")
        # print(f"IMPLIED_ASK: {implied_ask}")
        # print(f"FOREIGN_ASK: {observation.askPrice}")
        # print(f"FOREIGN_BID: {observation.bidPrice}")

        buy_quantity = position_limit - (position + buy_order_volume)
        if bid != None:
            if buy_quantity > 0:
                orders.append(Order(Product.ORCHIDS, round(bid), buy_quantity))

        if ask != None:
            sell_quantity = position_limit + (position - sell_order_volume)
            if sell_quantity > 0:
                orders.append(Order(Product.ORCHIDS, round(ask), -sell_quantity))

        return orders, buy_order_volume, sell_order_volume

    def get_swmid(self, order_depth) -> float:
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        best_bid_vol = abs(order_depth.buy_orders[best_bid])
        best_ask_vol = abs(order_depth.sell_orders[best_ask])
        return (best_bid * best_ask_vol + best_ask * best_bid_vol) / (
            best_bid_vol + best_ask_vol
        )

    def get_synthetic_basket_order_depth(
        self, order_depths: Dict[str, OrderDepth]
    ) -> OrderDepth:
        # Constants
        CHOCOLATE_PER_BASKET = BASKET_WEIGHTS[Product.CHOCOLATE]
        STRAWBERRIES_PER_BASKET = BASKET_WEIGHTS[Product.STRAWBERRIES]
        ROSES_PER_BASKET = BASKET_WEIGHTS[Product.ROSES]

        # Initialize the synthetic basket order depth
        synthetic_order_price = OrderDepth()

        # Calculate the best bid and ask for each component
        chocolate_best_bid = (
            max(order_depths[Product.CHOCOLATE].buy_orders.keys())
            if order_depths[Product.CHOCOLATE].buy_orders
            else 0
        )
        chocolate_best_ask = (
            min(order_depths[Product.CHOCOLATE].sell_orders.keys())
            if order_depths[Product.CHOCOLATE].sell_orders
            else float("inf")
        )
        strawberries_best_bid = (
            max(order_depths[Product.STRAWBERRIES].buy_orders.keys())
            if order_depths[Product.STRAWBERRIES].buy_orders
            else 0
        )
        strawberries_best_ask = (
            min(order_depths[Product.STRAWBERRIES].sell_orders.keys())
            if order_depths[Product.STRAWBERRIES].sell_orders
            else float("inf")
        )
        roses_best_bid = (
            max(order_depths[Product.ROSES].buy_orders.keys())
            if order_depths[Product.ROSES].buy_orders
            else 0
        )
        roses_best_ask = (
            min(order_depths[Product.ROSES].sell_orders.keys())
            if order_depths[Product.ROSES].sell_orders
            else float("inf")
        )

        # Calculate the implied bid and ask for the synthetic basket
        implied_bid = (
            chocolate_best_bid * CHOCOLATE_PER_BASKET
            + strawberries_best_bid * STRAWBERRIES_PER_BASKET
            + roses_best_bid * ROSES_PER_BASKET
        )
        implied_ask = (
            chocolate_best_ask * CHOCOLATE_PER_BASKET
            + strawberries_best_ask * STRAWBERRIES_PER_BASKET
            + roses_best_ask * ROSES_PER_BASKET
        )

        # Calculate the maximum number of synthetic baskets available at the implied bid and ask
        if implied_bid > 0:
            chocolate_bid_volume = (
                order_depths[Product.CHOCOLATE].buy_orders[chocolate_best_bid]
                // CHOCOLATE_PER_BASKET
            )
            strawberries_bid_volume = (
                order_depths[Product.STRAWBERRIES].buy_orders[strawberries_best_bid]
                // STRAWBERRIES_PER_BASKET
            )
            roses_bid_volume = (
                order_depths[Product.ROSES].buy_orders[roses_best_bid]
                // ROSES_PER_BASKET
            )
            implied_bid_volume = min(
                chocolate_bid_volume, strawberries_bid_volume, roses_bid_volume
            )
            synthetic_order_price.buy_orders[implied_bid] = implied_bid_volume

        if implied_ask < float("inf"):
            chocolate_ask_volume = (
                -order_depths[Product.CHOCOLATE].sell_orders[chocolate_best_ask]
                // CHOCOLATE_PER_BASKET
            )
            strawberries_ask_volume = (
                -order_depths[Product.STRAWBERRIES].sell_orders[strawberries_best_ask]
                // STRAWBERRIES_PER_BASKET
            )
            roses_ask_volume = (
                -order_depths[Product.ROSES].sell_orders[roses_best_ask]
                // ROSES_PER_BASKET
            )
            implied_ask_volume = min(
                chocolate_ask_volume, strawberries_ask_volume, roses_ask_volume
            )
            synthetic_order_price.sell_orders[implied_ask] = -implied_ask_volume

        return synthetic_order_price

    def convert_synthetic_basket_orders(
        self, synthetic_orders: List[Order], order_depths: Dict[str, OrderDepth]
    ) -> Dict[str, List[Order]]:
        # Initialize the dictionary to store component orders
        component_orders = {
            Product.CHOCOLATE: [],
            Product.STRAWBERRIES: [],
            Product.ROSES: [],
        }

        # Get the best bid and ask for the synthetic basket
        synthetic_basket_order_depth = self.get_synthetic_basket_order_depth(
            order_depths
        )
        best_bid = (
            max(synthetic_basket_order_depth.buy_orders.keys())
            if synthetic_basket_order_depth.buy_orders
            else 0
        )
        best_ask = (
            min(synthetic_basket_order_depth.sell_orders.keys())
            if synthetic_basket_order_depth.sell_orders
            else float("inf")
        )

        # Iterate through each synthetic basket order
        for order in synthetic_orders:
            # Extract the price and quantity from the synthetic basket order
            price = order.price
            quantity = order.quantity

            # Check if the synthetic basket order aligns with the best bid or ask
            if quantity > 0 and price >= best_ask:
                # Buy order - trade components at their best ask prices
                chocolate_price = min(
                    order_depths[Product.CHOCOLATE].sell_orders.keys()
                )
                strawberries_price = min(
                    order_depths[Product.STRAWBERRIES].sell_orders.keys()
                )
                roses_price = min(order_depths[Product.ROSES].sell_orders.keys())
            elif quantity < 0 and price <= best_bid:
                # Sell order - trade components at their best bid prices
                chocolate_price = max(order_depths[Product.CHOCOLATE].buy_orders.keys())
                strawberries_price = max(
                    order_depths[Product.STRAWBERRIES].buy_orders.keys()
                )
                roses_price = max(order_depths[Product.ROSES].buy_orders.keys())
            else:
                # The synthetic basket order does not align with the best bid or ask
                continue

            # Create orders for each component
            chocolate_order = Order(
                Product.CHOCOLATE,
                chocolate_price,
                quantity * BASKET_WEIGHTS[Product.CHOCOLATE],
            )
            strawberries_order = Order(
                Product.STRAWBERRIES,
                strawberries_price,
                quantity * BASKET_WEIGHTS[Product.STRAWBERRIES],
            )
            roses_order = Order(
                Product.ROSES, roses_price, quantity * BASKET_WEIGHTS[Product.ROSES]
            )

            # Add the component orders to the respective lists
            component_orders[Product.CHOCOLATE].append(chocolate_order)
            component_orders[Product.STRAWBERRIES].append(strawberries_order)
            component_orders[Product.ROSES].append(roses_order)

        return component_orders

    def execute_spread_orders(
        self,
        target_position: int,
        basket_position: int,
        order_depths: Dict[str, OrderDepth],
    ):

        if target_position == basket_position:
            return None

        target_quantity = abs(target_position - basket_position)
        basket_order_depth = order_depths[Product.GIFT_BASKET]
        synthetic_order_depth = self.get_synthetic_basket_order_depth(order_depths)

        if target_position > basket_position:
            basket_ask_price = min(basket_order_depth.sell_orders.keys())
            basket_ask_volume = abs(basket_order_depth.sell_orders[basket_ask_price])

            synthetic_bid_price = max(synthetic_order_depth.buy_orders.keys())
            synthetic_bid_volume = abs(
                synthetic_order_depth.buy_orders[synthetic_bid_price]
            )

            orderbook_volume = min(basket_ask_volume, synthetic_bid_volume)
            execute_volume = min(orderbook_volume, target_quantity)

            basket_orders = [
                Order(Product.GIFT_BASKET, basket_ask_price, execute_volume)
            ]
            synthetic_orders = [
                Order(Product.SYNTHETIC, synthetic_bid_price, -execute_volume)
            ]

            aggregate_orders = self.convert_synthetic_basket_orders(
                synthetic_orders, order_depths
            )
            aggregate_orders[Product.GIFT_BASKET] = basket_orders
            return aggregate_orders

        else:
            basket_bid_price = max(basket_order_depth.buy_orders.keys())
            basket_bid_volume = abs(basket_order_depth.buy_orders[basket_bid_price])

            synthetic_ask_price = min(synthetic_order_depth.sell_orders.keys())
            synthetic_ask_volume = abs(
                synthetic_order_depth.sell_orders[synthetic_ask_price]
            )

            orderbook_volume = min(basket_bid_volume, synthetic_ask_volume)
            execute_volume = min(orderbook_volume, target_quantity)

            basket_orders = [
                Order(Product.GIFT_BASKET, basket_bid_price, -execute_volume)
            ]
            synthetic_orders = [
                Order(Product.SYNTHETIC, synthetic_ask_price, execute_volume)
            ]

            aggregate_orders = self.convert_synthetic_basket_orders(
                synthetic_orders, order_depths
            )
            aggregate_orders[Product.GIFT_BASKET] = basket_orders
            return aggregate_orders

    def spread_orders(
        self,
        order_depths: Dict[str, OrderDepth],
        product: Product,
        basket_position: int,
        spread_data: Dict[str, Any],
    ):
        if Product.GIFT_BASKET not in order_depths.keys():
            return None

        basket_order_depth = order_depths[Product.GIFT_BASKET]
        synthetic_order_depth = self.get_synthetic_basket_order_depth(order_depths)
        basket_swmid = self.get_swmid(basket_order_depth)
        synthetic_swmid = self.get_swmid(synthetic_order_depth)
        spread = basket_swmid - synthetic_swmid
        spread_data["spread_history"].append(spread)

        if (
            len(spread_data["spread_history"])
            < self.params[Product.SPREAD]["spread_std_window"]
        ):
            return None
        elif (
            len(spread_data["spread_history"])
            > self.params[Product.SPREAD]["spread_std_window"]
        ):
            spread_data["spread_history"].pop(0)

        spread_std = np.std(spread_data["spread_history"])

        zscore = (
            spread - self.params[Product.SPREAD]["default_spread_mean"]
        ) / spread_std

        if zscore >= self.params[Product.SPREAD]["zscore_threshold"]:
            if basket_position != -self.params[Product.SPREAD]["target_position"]:
                return self.execute_spread_orders(
                    -self.params[Product.SPREAD]["target_position"],
                    basket_position,
                    order_depths,
                )

        if zscore <= -self.params[Product.SPREAD]["zscore_threshold"]:
            if basket_position != self.params[Product.SPREAD]["target_position"]:
                return self.execute_spread_orders(
                    self.params[Product.SPREAD]["target_position"],
                    basket_position,
                    order_depths,
                )

        spread_data["prev_zscore"] = zscore
        return None

    def get_coconut_coupon_mid_price(
        self, coconut_coupon_order_depth: OrderDepth, traderData: Dict[str, Any]
    ):
        if (
            len(coconut_coupon_order_depth.buy_orders) > 0
            and len(coconut_coupon_order_depth.sell_orders) > 0
        ):
            best_bid = max(coconut_coupon_order_depth.buy_orders.keys())
            best_ask = min(coconut_coupon_order_depth.sell_orders.keys())
            traderData["prev_coupon_price"] = (best_bid + best_ask) / 2
            return (best_bid + best_ask) / 2
        else:
            return traderData["prev_coupon_price"]
      
    def coconut_hedge_orders(
        self,
        coconut_order_depth: OrderDepth,
        coconut_coupon_order_depth: OrderDepth,
        coconut_coupon_orders: List[Order],
        coconut_position: int,
        coconut_coupon_position: int,
        delta: float
    ) -> List[Order]:
        if coconut_coupon_orders == None or len(coconut_coupon_orders) == 0:
            coconut_coupon_position_after_trade = coconut_coupon_position
        else:
            coconut_coupon_position_after_trade = coconut_coupon_position + sum(order.quantity for order in coconut_coupon_orders)
        
        target_coconut_position = -delta * coconut_coupon_position_after_trade
        
        if target_coconut_position == coconut_position:
            return None
        
        target_coconut_quantity = target_coconut_position - coconut_position

        orders: List[Order] = []
        if target_coconut_quantity > 0:
            # Buy COCONUT
            best_ask = min(coconut_order_depth.sell_orders.keys())
            quantity = min(
                abs(target_coconut_quantity),
                self.LIMIT[Product.COCONUT] - coconut_position,
            )
            if quantity > 0:
                orders.append(Order(Product.COCONUT, best_ask, round(quantity)))
        
        elif target_coconut_quantity < 0:
            # Sell COCONUT
            best_bid = max(coconut_order_depth.buy_orders.keys())
            quantity = min(
                abs(target_coconut_quantity),
                self.LIMIT[Product.COCONUT] + coconut_position,
            )
            if quantity > 0:
                orders.append(Order(Product.COCONUT, best_bid, -round(quantity)))
        
        return orders

    def coconut_coupon_orders(
        self,
        coconut_coupon_order_depth: OrderDepth,
        coconut_coupon_position: int,
        traderData: Dict[str, Any],
        volatility: float,
    ) -> List[Order]:
        traderData['past_coupon_vol'].append(volatility)
        if len(traderData['past_coupon_vol']) < self.params[Product.COCONUT_COUPON]['std_window']:
            return None, None

        if len(traderData['past_coupon_vol']) > self.params[Product.COCONUT_COUPON]['std_window']:
            traderData['past_coupon_vol'].pop(0)
        
        vol_z_score = (volatility - self.params[Product.COCONUT_COUPON]['mean_volatility']) / np.std(traderData['past_coupon_vol'])
        # print(f"vol_z_score: {vol_z_score}")
        # print(f"zscore_threshold: {self.params[Product.COCONUT_COUPON]['zscore_threshold']}")
        if (
            vol_z_score 
            >= self.params[Product.COCONUT_COUPON]['zscore_threshold']
        ):
            if coconut_coupon_position != -self.LIMIT[Product.COCONUT_COUPON]:
                target_coconut_coupon_position = -self.LIMIT[Product.COCONUT_COUPON]
                if len(coconut_coupon_order_depth.buy_orders) > 0:
                    best_bid = max(coconut_coupon_order_depth.buy_orders.keys())
                    target_quantity = abs(target_coconut_coupon_position - coconut_coupon_position)
                    quantity = min(
                        target_quantity,
                        abs(coconut_coupon_order_depth.buy_orders[best_bid]),
                    )
                    quote_quantity = target_quantity - quantity
                    if quote_quantity == 0:
                        return [Order(Product.COCONUT_COUPON, best_bid, -quantity)], []
                    else:
                        return [Order(Product.COCONUT_COUPON, best_bid, -quantity)], [Order(Product.COCONUT_COUPON, best_bid, -quote_quantity)]

        elif (
            vol_z_score
            <= -self.params[Product.COCONUT_COUPON]["zscore_threshold"]
        ):
            if coconut_coupon_position != self.LIMIT[Product.COCONUT_COUPON]:
                target_coconut_coupon_position = self.LIMIT[Product.COCONUT_COUPON]
                if len(coconut_coupon_order_depth.sell_orders) > 0:
                    best_ask = min(coconut_coupon_order_depth.sell_orders.keys())
                    target_quantity = abs(target_coconut_coupon_position - coconut_coupon_position)
                    quantity = min(
                        target_quantity,
                        abs(coconut_coupon_order_depth.sell_orders[best_ask]),
                    )
                    quote_quantity = target_quantity - quantity
                    if quote_quantity == 0:
                        return [Order(Product.COCONUT_COUPON, best_ask, quantity)], []
                    else:
                        return [Order(Product.COCONUT_COUPON, best_ask, quantity)], [Order(Product.COCONUT_COUPON, best_ask, quote_quantity)]

        return None, None

    def get_past_returns(
        self,
        traderObject: Dict[str, Any],
        order_depths: Dict[str, OrderDepth],
        timeframes: Dict[str, int],
    ):
        returns_dict = {}

        for symbol, timeframe in timeframes.items():
            traderObject_key = f"{symbol}_price_history"
            if traderObject_key not in traderObject:
                traderObject[traderObject_key] = []

            price_history = traderObject[traderObject_key]

            if symbol in order_depths:
                order_depth = order_depths[symbol]
                if len(order_depth.buy_orders) > 0 and len(order_depth.sell_orders) > 0:
                    current_price = (
                        max(order_depth.buy_orders.keys())
                        + min(order_depth.sell_orders.keys())
                    ) / 2
                else:
                    if len(price_history) > 0:
                        current_price = float(price_history[-1])
                    else:
                        returns_dict[symbol] = None
                        continue
            else:
                if len(price_history) > 0:
                    current_price = float(price_history[-1])
                else:
                    returns_dict[symbol] = None
                    continue

            price_history.append(
                f"{current_price:.1f}"
            )  # Convert float to string with 1 decimal place

            if len(price_history) > timeframe:
                price_history.pop(0)

            if len(price_history) == timeframe:
                past_price = float(price_history[0])  # Convert string back to float
                returns = (current_price - past_price) / past_price
                returns_dict[symbol] = returns
            else:
                returns_dict[symbol] = None

        return returns_dict

    def run(self, state: TradingState):
        traderObject = {}
        if state.traderData != None and state.traderData != "":
            traderObject = jsonpickle.decode(state.traderData)

        past_returns_timeframes = {"GIFT_BASKET": 500}
        past_returns_dict = self.get_past_returns(
            traderObject, state.order_depths, past_returns_timeframes
        )

        result = {}
        conversions = 0

        if Product.AMETHYSTS in self.params and Product.AMETHYSTS in state.order_depths:
            amethyst_position = (
                state.position[Product.AMETHYSTS]
                if Product.AMETHYSTS in state.position
                else 0
            )
            amethyst_take_orders, buy_order_volume, sell_order_volume = (
                self.take_orders(
                    Product.AMETHYSTS,
                    state.order_depths[Product.AMETHYSTS],
                    self.params[Product.AMETHYSTS]["fair_value"],
                    self.params[Product.AMETHYSTS]["take_width"],
                    amethyst_position,
                )
            )
            amethyst_clear_orders, buy_order_volume, sell_order_volume = (
                self.clear_orders(
                    Product.AMETHYSTS,
                    state.order_depths[Product.AMETHYSTS],
                    self.params[Product.AMETHYSTS]["fair_value"],
                    self.params[Product.AMETHYSTS]["clear_width"],
                    amethyst_position,
                    buy_order_volume,
                    sell_order_volume,
                )
            )
            amethyst_make_orders, _, _ = self.make_amethyst_orders(
                state.order_depths[Product.AMETHYSTS],
                self.params[Product.AMETHYSTS]["fair_value"],
                amethyst_position,
                buy_order_volume,
                sell_order_volume,
                self.params[Product.AMETHYSTS]["volume_limit"],
            )
            result[Product.AMETHYSTS] = (
                amethyst_take_orders + amethyst_clear_orders + amethyst_make_orders
            )

        if Product.STARFRUIT in self.params and Product.STARFRUIT in state.order_depths:
            starfruit_position = (
                state.position[Product.STARFRUIT]
                if Product.STARFRUIT in state.position
                else 0
            )
            starfruit_fair_value = self.starfruit_fair_value(
                state.order_depths[Product.STARFRUIT], traderObject
            )
            starfruit_take_orders, buy_order_volume, sell_order_volume = (
                self.take_orders(
                    Product.STARFRUIT,
                    state.order_depths[Product.STARFRUIT],
                    starfruit_fair_value,
                    self.params[Product.STARFRUIT]["take_width"],
                    starfruit_position,
                    self.params[Product.STARFRUIT]["prevent_adverse"],
                    self.params[Product.STARFRUIT]["adverse_volume"],
                )
            )
            starfruit_clear_orders, buy_order_volume, sell_order_volume = (
                self.clear_orders(
                    Product.STARFRUIT,
                    state.order_depths[Product.STARFRUIT],
                    starfruit_fair_value,
                    self.params[Product.STARFRUIT]["clear_width"],
                    starfruit_position,
                    buy_order_volume,
                    sell_order_volume,
                )
            )
            starfruit_make_orders, _, _ = self.make_starfruit_orders(
                state.order_depths[Product.STARFRUIT],
                starfruit_fair_value,
                self.params[Product.STARFRUIT]["starfruit_min_edge"],
                starfruit_position,
                buy_order_volume,
                sell_order_volume,
            )
            result[Product.STARFRUIT] = (
                starfruit_take_orders + starfruit_clear_orders + starfruit_make_orders
            )

        if Product.ORCHIDS in self.params and Product.ORCHIDS in state.order_depths:
            orchids_position = (
                state.position[Product.ORCHIDS]
                if Product.ORCHIDS in state.position
                else 0
            )
            # print(f"ORCHIDS POSITION: {orchids_position}")

            if "orchids_target_position" not in traderObject:
                traderObject["orchids_target_position"] = 0

            target_position = traderObject["orchids_target_position"]

            gift_basket_returns = past_returns_dict.get("GIFT_BASKET")
            if gift_basket_returns is not None:
                pred_orchids_returns = (
                    gift_basket_returns
                    * self.params[Product.ORCHIDS]["gift_basket_beta"]
                )
                if (
                    pred_orchids_returns
                    > self.params[Product.ORCHIDS]["returns_threshold"]
                ):
                    target_position = 0  # Adjust target position to never go positive
                elif (
                    pred_orchids_returns
                    < -self.params[Product.ORCHIDS]["returns_threshold"]
                ):
                    target_position = -self.LIMIT[Product.ORCHIDS]

                # Clear the position if predicted returns cross the clearing threshold
                if (
                    target_position < 0
                    and pred_orchids_returns
                    > self.params[Product.ORCHIDS]["clear_threshold"]
                ):
                    target_position = 0
                elif (
                    target_position > 0
                    and pred_orchids_returns
                    < -self.params[Product.ORCHIDS]["clear_threshold"]
                ):
                    target_position = 0

            traderObject["orchids_target_position"] = target_position

            orchids_take_orders, buy_order_volume, sell_order_volume = (
                self.orchids_arb_take(
                    state.order_depths[Product.ORCHIDS],
                    state.observations.conversionObservations[Product.ORCHIDS],
                    0,  # Pass 0 as the orchids_position for arb_take
                )
            )

            orchids_make_orders, _, _ = self.orchids_arb_make(
                state.observations.conversionObservations[Product.ORCHIDS],
                0,  # Pass 0 as the orchids_position for arb_make
                buy_order_volume,
                sell_order_volume,
            )

            if len(orchids_make_orders) > 0:   
                print("ARB MAKE AND TAKE")
                # Arb is in play, clear the position and send arb orders
                conversions = self.orchids_arb_clear(orchids_position)
                result[Product.ORCHIDS] = orchids_take_orders + orchids_make_orders
            
            elif len(orchids_take_orders) > 0:
                print("ARB TAKE")
                take_order_quantity = sum([order.quantity for order in orchids_take_orders])
                conversions = max(target_position - orchids_position - take_order_quantity, 0)
                result[Product.ORCHIDS] = orchids_take_orders

            else:
                # Arb is not in play, try to reach the target position
                # print("NO ARB")
                position_diff = target_position - orchids_position
                orders: List[Order] = []

                if position_diff < 0:
                    # Enter a short position
                    bid = round(state.observations.conversionObservations[Product.ORCHIDS].askPrice) - 2
                    quantity = abs(position_diff)
                    orders.append(Order(Product.ORCHIDS, bid, -quantity))
                elif position_diff > 0:
                    # Clear a short position
                    best_ask = min(
                        state.order_depths[Product.ORCHIDS].sell_orders.keys()
                    )
                    implied_ask = self.orchids_implied_bid_ask(
                        state.observations.conversionObservations[Product.ORCHIDS]
                    )[1]
                    if best_ask <= implied_ask:
                        # Buy from the best_ask
                        quantity = position_diff
                        orders.append(Order(Product.ORCHIDS, best_ask, quantity))
                    else:
                        # Buy from the implied_ask
                        conversions = position_diff

                result[Product.ORCHIDS] = orders

        if Product.SPREAD not in traderObject:
            traderObject[Product.SPREAD] = {
                "spread_history": [],
                "prev_zscore": 0,
                "clear_flag": False,
                "curr_avg": 0,
            }

        basket_position = (
            state.position[Product.GIFT_BASKET]
            if Product.GIFT_BASKET in state.position
            else 0
        )
        spread_orders = self.spread_orders(
            state.order_depths,
            Product.GIFT_BASKET,
            basket_position,
            traderObject[Product.SPREAD],
        )

        if spread_orders != None:
            result[Product.CHOCOLATE] = spread_orders[Product.CHOCOLATE]
            result[Product.STRAWBERRIES] = spread_orders[Product.STRAWBERRIES]
            result[Product.ROSES] = spread_orders[Product.ROSES]
            result[Product.GIFT_BASKET] = spread_orders[Product.GIFT_BASKET]

        if Product.COCONUT_COUPON not in traderObject:
            traderObject[Product.COCONUT_COUPON] = {
                "prev_coupon_price": 0,
                "past_coupon_vol": []
            }

        if (
            Product.COCONUT_COUPON in self.params
            and Product.COCONUT_COUPON in state.order_depths
        ):
            coconut_coupon_position = (
                state.position[Product.COCONUT_COUPON]
                if Product.COCONUT_COUPON in state.position
                else 0
            )

            coconut_position = (
                state.position[Product.COCONUT]
                if Product.COCONUT in state.position
                else 0
            )
            # print(f"coconut_coupon_position: {coconut_coupon_position}")
            # print(f"coconut_position: {coconut_position}")
            coconut_order_depth = state.order_depths[Product.COCONUT]
            coconut_coupon_order_depth = state.order_depths[Product.COCONUT_COUPON]
            coconut_mid_price = (
                min(coconut_order_depth.buy_orders.keys())
                + max(coconut_order_depth.sell_orders.keys())
            ) / 2
            coconut_coupon_mid_price = self.get_coconut_coupon_mid_price(
                coconut_coupon_order_depth, traderObject[Product.COCONUT_COUPON]
            )
            tte = (
                self.params[Product.COCONUT_COUPON]["starting_time_to_expiry"]
                - (state.timestamp) / 1000000 / 250
            )
            volatility = BlackScholes.implied_volatility(
                coconut_coupon_mid_price,
                coconut_mid_price,
                self.params[Product.COCONUT_COUPON]["strike"],
                tte,
            )
            delta = BlackScholes.delta(
                coconut_mid_price,
                self.params[Product.COCONUT_COUPON]["strike"],
                tte,
                volatility,
            )
    
            coconut_coupon_take_orders, coconut_coupon_make_orders = self.coconut_coupon_orders(
                state.order_depths[Product.COCONUT_COUPON],
                coconut_coupon_position,
                traderObject[Product.COCONUT_COUPON],
                volatility,
            )

            coconut_orders = self.coconut_hedge_orders(
                state.order_depths[Product.COCONUT],
                state.order_depths[Product.COCONUT_COUPON],
                coconut_coupon_take_orders,
                coconut_position,
                coconut_coupon_position,
                delta
            )

            if coconut_coupon_take_orders != None or coconut_coupon_make_orders != None:
                result[Product.COCONUT_COUPON] = coconut_coupon_take_orders + coconut_coupon_make_orders
                # print(f"COCONUT_COUPON: {result[Product.COCONUT_COUPON]}")

            if coconut_orders != None:
                result[Product.COCONUT] = coconut_orders
                # print(f"COCONUT: {result[Product.COCONUT]}")

        traderData = jsonpickle.encode(traderObject)

        return result, conversions, traderData
