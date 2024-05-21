# linear utility 📈
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

This repository contains research and algorithms for our team, Linear Utility, in IMC Prosperity 2024. We placed 2nd globally, with an overall score of 3,501,647 seashells, and took home $10,000 in prize money. 

## the team ✨

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/jcgs2503">
          <img src="https://avatars.githubusercontent.com/u/63511765?v=4?s=100" width="100px;" alt="Jerry Chang"/>
          <br /><sub><b>Jerry Chang</b></sub></a>
        <br /><sub><a href="https://www.linkedin.com/in/chieh-chang/" title="LinkedIn">🔗 LinkedIn</a></sub>
        <br /><a href="#research-jcgs2503" title="Research">🔬</a>
        <a href="https://github.com/ericcccsliu/imc-prosperity-2/commits?author=jcgs2503" title="Code">💻</a>
      </td>
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/ericcccsliu">
          <img src="https://avatars.githubusercontent.com/u/62641231?v=4?s=100" width="100px;" alt="Eric Liu"/>
          <br /><sub><b>Eric Liu</b></sub></a>
        <br /><sub><a href="https://www.linkedin.com/in/ericccccc/" title="LinkedIn">🔗 LinkedIn</a></sub>
        <br /><a href="#research-ericcccsliu" title="Research">🔬</a>
        <a href="https://github.com/ericcccsliu/imc-prosperity-2/commits?author=ericcccsliu" title="Code">💻</a>
      </td>
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/sreekar-bathula">
          <img src="https://avatars.githubusercontent.com/u/86486991?v=4?s=100" width="100px;" alt="Sreekar Bathula"/>
          <br /><sub><b>Sreekar Bathula</b></sub></a>
        <br /><sub><a href="https://www.linkedin.com/in/sreekar-bathula/" title="LinkedIn">🔗 LinkedIn</a></sub>
        <br /><a href="https://github.com/ericcccsliu/imc-prosperity-2/commits?author=sreekar-bathula" title="Code">💻</a>
      </td>
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/liu-nathan">
          <img src="https://avatars.githubusercontent.com/u/113719450?v=4?s=100" width="100px;" alt="liu-nathan"/>
          <br /><sub><b>liu-nathan</b></sub></a>
        <br /><sub><a href="https://www.linkedin.com/in/nl-nathanliu/" title="LinkedIn">🔗 LinkedIn</a></sub>
        <br /><a href="https://github.com/ericcccsliu/imc-prosperity-2/commits?author=liu-nathan" title="Research">🔬</a>
      </td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

## the competition 🏆

IMC Prosperity 2024 was an algorithmic trading competition that lasted over 15 days, with over 9000 teams participating globally. In the challenge, we were placed on our own archipelago, and tasked with trading various financial products, such as amethysts, starfruit, orchids, coconuts, and more, with the goal of maximizing seashells: the underlying currency of our island. The products available to trade started with amethysts and starfruit in round 1. With each subsequent round, more products would be added, and at the end of each round, our trading algorithm would be evaluated against bot participants in the marketplace, whose behavior we could try and predict through historical data. The PNL from this independent evaluation would then be compared against all other teams. 

In addition to the main algorithmic trading focus, the competition also consisted of manual trading challenges in each round. The focus of these varied widely, and in the end, manual trading accounted for just a small fraction of our PNL. 

For documentation on the algorithmic trading environment, and more context about the competition, feel free to consult the [Prosperity 2 Wiki](https://imc-prosperity.notion.site/Prosperity-2-Wiki-fe650c0292ae4cdb94714a3f5aa74c85). 

## organization 📂

This repository contains all of our code–including internal tools, research notebooks, raw data and backtesting logs, and all versions of our main algorithmic trader code. The repository is organized by round. Our backtester mostly remained unchanged from round 1, but we simply copied its files over to each subsequent round, so you'll find a version of that in each folder. Within each round, you can locate the algorithmic trading code we used in our final submission by looking for the latest version–for example, for round 1, we used [`round_1_v6.py`](https://github.com/ericcccsliu/imc-prosperity-2/blob/main/round1/round_1_v6.py) for our final submission. Our visualization dashboard is located in the `dashboard` folder. 

## tools 🛠️

Instead of relying heavily on open-source tools for visualization and backtesting, which many successful teams did, we decided instead to build our tools in-house. This, overall, was a good decision–while it didn't pay off as much as we hoped (more on this later), we were able to tailor our tools heavily for our own needs. We built two main tools for use throughout the competition: a backtester and a visualization dashboard. 

### backtester 🔙

### dashapp 💨

The dashapp we developed helped us a lot during the early rounds on finding how to generate more pnl and looking for desirable trades our algorithm didn't do or undesirable trades our algorithm did. The most helpful feature in my opinion was the syncing feature, where we coded out such that the whole dashapp would be synced to the exact timestamp whenever we clicked on the dash charts. We also enabled manually typing in timestamp and displaying the orderbook at the given timestamp. 

![332262673-fb1ab2d8-72a6-4d95-bbaa-ab15cd578a8d](https://github.com/ericcccsliu/imc-prosperity-2/assets/62641231/5878101d-53e3-46c1-a646-85bb84bd0b3d)
<p align="center">
  <em>we used to have actual section headers, but at some point we (Jerry and Eric) got hungry and started editing them</em>
</p>



## round 1️⃣

In round 1, we had access to two symbols to trade: amethysts and starfruit. 

### amethysts 🔮
Amethysts were fairly simple, as the fair price clearly never deviated from 10,000. As such, we wrote our algorithm to trade against bids above 10,000 and asks below 10,000. Besides taking orders, our algorithm also would market-make, placing bids and asks below and above 10,000, respectively, with a certain edge. Using our backtester, we gridsearched over several different values to find the most profitable edge to request. This worked well, getting us about 16k seashells over backtests

However, through looking at backtest logs in our dashapp, we discovered that many profitable trades were prevented by our position limits, as we were unable to long or short more than 20 amethysts (and starfruit) at any given moment. To fix this issue, we implemented a strategy to clear our position–our algorithm would do 0 ev trades, if available, just to get our position closer to 0, so that we'd be able to do more positive ev trades later on. This strategy bumped our pnl up by about 3%. 

### starfruit ⭐

Finding a good fair price for starfruit was tougher, as its price wasn't fixed–it would slowly randomwalk around. Nonetheless, we observed that the price was relatively stable locally. So we created a fair using a rolling average of the mid price over the last *n* timestamps, where *n* was a parameter which we could optimize over in backtests[^1]. Market-making, taking, and clearing (the same strategies we did with amethysts) worked quite well around this fair value. 

However, using the mid price–even in averaging over it–didn't seem to be the best, as the mid price was noisy from market participants continually putting orders past mid (orders that we thought were good to fair and therefore ones that we wanted to trade against). Looking at the orderbook, we found out that, at all times, there was a market making bot quoting relatively large sizes on both sides, at prices that were unaffected by smaller participants[^2]. Using this market maker's mid price as a fair turned out to be much less noisy and generated more pnl in backtests. 

<img width="744" alt="Screenshot 2024-05-20 at 11 54 46 PM" src="https://github.com/ericcccsliu/imc-prosperity-2/assets/62641231/26d2f65c-2a5a-4252-8094-34a35a280020">
<p align="center">
  <em>histograms of volumes on the first and second level of the bid side</em>
</p>

Surprisingly, when we tested our algorithm on the website, we figured out that the website was  marking our pnl to the market maker's mid instead of the actual mid price. We were able to verify this by backtesting a trading algorithm that bought 1 starfruit in the first timestamp and simply held it to the end–our pnl graph marked to market maker mid in our own backtesting environment exactly replicated the pnl graph on the website. This boosted our confidence in using the market maker mid as fair, as we realized that we'd just captured the true internal fair of the game. Besides this, some research on the fair price showed that starfruit was very slightly mean reverting[^3], and the rest was very similar to amethysts, where we took orders and quoted orders with a certain edge, optimizing all parameters in our internal backtester with a grid search.

After round 1, our team was ranked #3 in the world overall. We had an algo trading profit of 34,498 seashells–just 86 seashells behind first place.

## round 2️⃣

### orchids 🥀
Orchids were introduced in round 2, as well as a bunch of data on sunlight, humidity, import/export tariffs, and shipping costs. The premise was that orchids were grown on a separate island[^4], and had to be imported–subject to import tariffs and shipping costs, and that they would degrade with suboptimal levels of sunlight and humidity. We were able to trade orchids both in a market on our own island, as well as through importing them from the South archipelago. With this, we had two initial approaches. The obvious approach, to us, was to look for alpha in all the data available, investigating if the price of orchids could be predicted using sunlight, humidity, etc. The other approach involved understanding exactly how the mechanisms for trading orchids worked, as the documentation was fairly unclear. Thus, we split up: Eric looked for alpha in the historical data while Jerry worked on understanding the actual trading environment.

Finding tradable correlations in the historical data was tougher than we initially thought. Some things that we tried were[^5]: 
- Just trying to find correlations to orchids returns from returns in sunlight, humidity, tarriffs, costs. Initial results from this seemed interesting–but the correlations we found here were likely spurious.
- Linear regressions from returns in sunlight, humidity, etc., to returns in orchids. We tried varying timeframes–first predicting orchids returns in the same timeframe as the returns in the predictors, and then predicting using lagged returns–building models that predicted future orchids returns over some timeframe using past returns in each of the predictors.
- Feature engineering with the various features given and performing the previous two steps again with the newly constructed features
All of these failed to leave us with a convincing model, leading us to believe that the data given was a bit of a distraction[^6]. 

Meanwhile, Jerry was having much better luck. In experimenting around with the trading environment, we realized that there was a massive taker in the local orchids market. Sell orders–and just sell orders–just a bit above the best bids would be instantly taken for full size. This, combined with low implied ask prices from the foreign market, meant that we could simply put large sell orders locally and simultaneously buy from the south archipelago for an arbitrage. As a first pass, our algorithm running this strategy made 60k seashells over over a fifth of a day. From here, some quick further optimization brought our website test pnl to just over 100k seashells, giving us a projected profit of 500k over a full day. 

While we figured this out independently, someone in the discord leaked this same strategy–which was quite unfortunate from our standpoint, as we knew that many teams would be able to implement the exact same thing and get the same pnl as us. With some noise from slight differences in implementation, we knew that we very well could end up dropping many places, if other teams with the same strategy simply got a bit luckier. So, we spent lots of time desperately searching for any further optimization on the arbitrage. We tested out different prices for sell orders in the local market, and found that using a price of `foreign ask price - 2` worked best. However, with this fixed level for our sell orders, we worried about changes in the market preventing this level from being consistently filled. As such, we came up with an "adaptive edge" algorithm, which looked at how much volume we got at each iteration (with the maximum, nominal volume being 100 lots). If the average volume we received was below some threshold, we'd start moving our sell order level around, automatically searching for a new level to maximize profits. 

Even with these optimizations, we still were beat out by the surge of teams who also found the arbitrage. We dropped all the way to 17th place, with a profit of 573,000 seashells from algo trading. We were within 20k of the second place team, and 100k away from the first place team, Puerto Vallarta, who seemed to have figured something out this round that no other teams could find. 

## round 3️⃣

Gift baskets, chocolate, roses, and strawberries were introduced in round 3, and a gift basket consisted of 4 chocolate bars, 6 strawberries, and a single rose. This round, we mainly traded spreads, which we defined as `basket - synthetic`, with `synthetic` being the sum of the price of all products in a basket.

### spread 🧺
In this round, we quickly converged on two hypotheses. The first hypothesis was that the synthetic would be leading baskets or vice versa, where changes in the price of one would lead to later changes in the price of the other.  Our second hypothesis was that the spread might simply just be mean reverting. We observed that the price of the spread–which theoretically should be 0–hovered around some fixed value, which we could trade around. We looked into leading/lagging relationships between the synthetic and the basket, but this wasn't very fruitful, so we then investigated the spread price. 

![newplot (1)](https://github.com/ericcccsliu/imc-prosperity-2/assets/62641231/6e56f911-8f7c-484c-8dab-32a1603ad2de)

Looking at the spread, we found that the price oscillated around ~370 across all three days of our historical data. Thus, we could profitably trade a mean-reverting strategy, buying spreads (going long baskets and short synthetic) when the spread price was below average, and selling spreads when the price was above. We tried various different ways to parameterize this trade. Due to our position limits, which were relatively small (about 2x the volume on the book at any instant), and the relatively small number of mean-reverting trading opportunities, we realized that timing the trade correctly was critical, and could result in a large amount of additional pnl. 

We tried various approaches in parameterizing this trade. A simple, first-pass strategy was just to set hardcoded prices at which to trade–for example, trading only when the spread deviated from the average value by a certain amount. We backtested to optimize these hardcoded thresholds, and our best parameters netted us ~120k in projected pnl[^7]. However, with this strategy, we noticed that we could lose out on a lot of pnl if the spread price reverted before touching our threshold. To remedy this, we could set our thresholds closer, but then we'd also lose pnl from trading before the spread price reached a local max/min. 

Therefore, we developed a more adaptive algorithm for spreads. We traded on a modified z-score, using a hardcoded mean and a rolling window standard deviation, with the window set relatively small. Then, we thresholded the z-score, selling spreads when our z-score went above a certain value and buying when the z-score dropped below. The idea here was that we wanted to wait until the price of spreads reached a local minima/maxima before trading. By using a small window for our rolling standard deviation, we'd see our z-score spike when the standard deviation drastically dropped–and this would often happen right as the price started reverting. This idea bumped our backtest pnl up to ~135k. 


![newplot (2)](https://github.com/ericcccsliu/imc-prosperity-2/assets/62641231/0db11d51-8916-4ed5-83f6-82faeb846267)
<p align="center">
  <em>a plot of spread prices and our modified z-score, as well as z-score thresholds (in green) to trade at</em>
</p>

After results from this round were released, we found that our actual pnl had a significant amount of slippage compared to our backtests–we made only 111k seashells from our algo. Nevertheless, we got a bit lucky–all the teams ahead of us in this round seemed to overfit significantly more, as we were ranked #2 overall.

## round 4️⃣

### coconuts/coconut coupon :coconut:
Coconuts and coconut coupons were introduced in round 4. Coconut coupons were the 10,000 strike call option on coconuts, with a time to expiry of 250 days. The price of coconuts hovered around 10,000, so this option was near-the-money. 

This round was fairly simple. Using Black-Scholes, we calculated the implied volatility of the option, and once we plotted this out, it became clear that the implied vol oscillated around a value of ~16%. We implemented a mean reverting strategy similar to round 3, and calculated the delta of the coconut coupons at each time in order to hedge with coconuts and gain pure exposure to vol. However, the delta was around 0.53 while the position limits for coconuts/coconut coupons were 300/600, respectively. This meant that we couldn't be fully hedged when holding 600 coupons (we would be holding 18 delta). Since the coupon was far away from expiry (thus, gamma didn't matter as much) and holding delta with vega was still positive ev (but higher var), we ran the variance in hopes of making more from our exposure to vol. 

![newplot (3)](https://github.com/ericcccsliu/imc-prosperity-2/assets/62641231/21fc47f7-727f-48a4-bf4e-b9b9c5fd25a1)

While holding this variance worked out in our backtests, we experienced a fair amount of slippage in our submission–we got unlucky and lost money from our delta exposure. In retrospect, not fully delta hedging might not have been  a smart move–we were already second place and thus should've went for lower var to try and keep the lead. Our algorithm in this round made only 145k, dropping us down to a terrifying 26th place. However, in the results of this round, we saw Puerto Vallarta leap ahead with a whopping profit of 1.2 *million* seashells. We knew we could catch up and end up well within the top 10 if only we could figure out what they did. 

## round 5️⃣

![image](https://github.com/ericcccsliu/imc-prosperity-2/assets/62641231/5d3bbc3b-9d16-473e-a6da-954a84a66da9)



One intersting thing worth mentioning would be our dynamic programming algorithm. We were confused by why dp would perform better than simply buying/selling knowing how the market moves at the next timestep. With some quick examples and discussion, we quickly figured out that the reason dp outperforms is because for certain products even if you buy/sell all the existing orders you can't get to the desired position (basically the position limit). For certain products you'd need to buy everything for 3 timestamps in order to get to full desired position. A simple example you can probably go through is to imagine a product having a price over time being: 8 -> 7 -> 12, then settle at 10. If your position limit is 2, and you can buy/sell any quantity at the given price each iteration, the optimal trading would be: sell 2 -> buy 4 -> sell 4, pnl = 16. Now imagine you can at most buy/sell 2 at a time, then with the same logic you would want to sell 2 -> buy 2 -> sell 2, pnl =  6, but in reality you actually want to buy 2 -> buy 2 -> sell 2, pnl = 14. 

Knowing this, it's evident that a simple dp algorithm of 3 states (-1, 0, +1) as position is not enough, and we need to take into account both crossing spread as well as the volume we can take each iteration given the spread, and the volume limit. We were able to simplify and model this with this following dp algorithm:

```python
def optimal_trading_dp(prices, spread, volume_pct):
    n = len(prices)
    price_level_cnt = math.ceil(1/volume_pct)
    left_over_pct = 1 - (price_level_cnt - 1) * volume_pct

    dp = [[float('-inf')] * (price_level_cnt * 2 + 1) for _ in range(n)]  # From -3 to 3, 7 positions
    action = [[''] * (price_level_cnt * 2 + 1) for _ in range(n)]  # To store actions

    # Initialize the starting position (no stock held)
    dp[0][price_level_cnt] = 0  # Start with no position, Cash is 0
    action[0][price_level_cnt] = ''  # No action at start

    def position(j):
        if j > price_level_cnt:
            position = min((j - price_level_cnt) * volume_pct, 1)
        elif j < price_level_cnt:
            position = max((j - price_level_cnt) * volume_pct, -1)
        else:
            position = 0
        return position
    
    def position_list(list):
        return np.array([position(x) for x in list])

    for i in range(1, n):
        for j in range(0, price_level_cnt * 2 + 1):
            # Calculate PnL for holding, buying, or selling
            hold = dp[i-1][j] if dp[i-1][j] != float('-inf') else float('-inf')
            if j == price_level_cnt * 2:
                buy = dp[i-1][j-1] - left_over_pct*prices[i-1] -  left_over_pct*spread if j > 0 else float('-inf')
            elif j == 1:
                buy = dp[i-1][j-1] - left_over_pct*prices[i-1] -  left_over_pct*spread if j > 0 else float('-inf')
            else:
                buy = dp[i-1][j-1] - volume_pct*prices[i-1] - volume_pct*spread if j > 0 else float('-inf')

            if j ==  0:
                sell = dp[i-1][j+1] + left_over_pct*prices[i-1] - left_over_pct*spread if j < price_level_cnt * 2 else float('-inf')
            elif j == price_level_cnt * 2 - 1:
                sell = dp[i-1][j+1] + left_over_pct*prices[i-1] - left_over_pct*spread if j < price_level_cnt * 2 else float('-inf')
            else:
                sell = dp[i-1][j+1] + volume_pct*prices[i-1] - volume_pct*spread if j < price_level_cnt * 2 else float('-inf')
                
            # Choose the action with the highest PnL

            hold_pnl = hold + (j - price_level_cnt) * position(j) * prices[i]
            buy_pnl = buy + (j - price_level_cnt) * position(j) * prices[i]
            sell_pnl = sell + (j - price_level_cnt) * position(j) * prices[i]
            
            # print(hold_pnl, buy_pnl, sell_pnl)
            best_action = max(hold_pnl, buy_pnl, sell_pnl)
            if best_action == hold_pnl:
                dp[i][j] = hold
            elif best_action == buy_pnl:
                dp[i][j] = buy
            else:
                dp[i][j] = sell

            if best_action == hold_pnl:
                action[i][j] = 'h'
            elif best_action == buy_pnl:
                action[i][j] = 'b'
            else:
                action[i][j] = 's'
    # Backtrack to find the sequence of actions
    trades_list = []
    # Start from the position with maximum PnL at time n-1

    pnl = np.array(dp[n-1]) + (position_list(np.arange(0,price_level_cnt*2+1)) * prices[n-1])
    current_position = np.argmax(pnl)
    for i in range(n-1, -1, -1):
        trades_list.append(action[i][current_position])
        if action[i][current_position] == 'b':
            current_position -= 1
        elif action[i][current_position] == 's':
            current_position += 1

    trades_list.reverse()
    trades_list.append('h')
    return dp, trades_list, pnl[np.argmax(pnl)]  # Return the actions and the maximum PnL

# Example usage
dp, trades, max_pnl = optimal_trading_dp(coconut_past_price, 0.99, 185/300)
# print(trades)
print("Max PnL:", max_pnl)
```
prices being the price over time, volume percentage being on average how much percentage of volume limit you can buy/sell, and spread being the average spread you'd need to cross for each trade. This dp turned out to perform way better than naive dp algorithm and for round 5 alone we were able to generate the most pnl out of all teams including the ranked 1 team.


[^1]: in the discord, we saw many teams using linear regression on past prices for this, likely inspired by [last year's second place submission](https://github.com/ShubhamAnandJain/IMC-Prosperity-2023-Stanford-Cardinal) 🌲. imho this was a bit silly! doing a linear regression in price space is really just a slightly worse way of performing an average, and you get high multicollinearity since each previous price is highly correlated with its neighbors, and you can really easily overfit (for example, if prices in your data slowly trended up, your learned LR coefficients can add up to be >1, meaning that your algo will bias towards buying, which might be spurious) 
[^2]: more specifically, we identified two participants in this market: a market making bot with order sizes quite uniform between 20 and 30, and a small bot that would occasionally cross fair with sizes uniform between 1 and 5.
[^3]: this was very very likely overfit, but the magnitude was so small that it didn't really make a difference in our pnl at all
[^4]: the south archipelago, where the ducks purportedly live
[^5]: a lot of our efforts here can be found in [this notebook](https://github.com/ericcccsliu/imc-prosperity-2/blob/main/round2/eric-research.ipynb)
[^6]: this conviction was strengthened by the fact that the sunlight, humidity data changed very gradually over very long timeframes–even if we could monetize this data, we'd only be able to monetize changes only a couple times each round, which didn't really seem to fit in this higher-frequency trading paradigm
[^7]: our backtests here occasionally incurred a bit of lookahead bias, as for most experiments we kept the mean value constant, which was calculated over the same data. we were aware of this, and decided that since the mean didn't really move around too much across days, the effect of this would be minimal (and not worth adjusting our backtester to correct for) 
