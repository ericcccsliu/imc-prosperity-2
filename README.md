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

Surprisingly, when we tested our algorithm on the website, we figured out that the website was  marking our pnl to the market maker's mid instead of the actual mid price. We were able to verify this by backtesting a trading algorithm that bought 1 starfruit in the first timestamp and simply held it to the end–our pnl graph marked to market maker mid in our own backtesting environment exactly replicated the pnl graph on the website. This boosted our confidence in using the market maker mid as fair, as we realized that we'd just captured the true internal fair of the game. Besides this, some research on the fair price showed that starfruit was very slightly mean reverting[^3], and the rest was very similar to amethysts, where we took orders and quoted orders with a certain edge, optimizing all parameters in our internal backtester with a grid search.

After round 1, our team was ranked #3 in the world overall.

## round 2️⃣

Orchids were introduced in round 2.

### orchids
For orchids, we had two initial thoughts about the round. The obvious one was to look for alpha in humidity and sunlight, and the slightly non trivial one was to look for arbitrage opportunities from import/export (the negative import tariff sort of triggered us to look into arb). Thus, we separated our work into eric looking for alpha in humidity and sunlight while jerry look for arbitrage opportunities. It turned out that eric couldn't find any alpha from humidity and sunlight, and even if there was it was very insignificant due to the amount of data we were given. We were desperate for a while until jerry uploaded his script and printed the straightest pnl line we've ever seen (60k in 100k timestamps). It was quite obvious at that point that we should focus more on arb than alpha. With more optimization on edge and deeper understandings about how the import/export works, we were able to double the amount of pnl to 120k in 100k timestamps. At this point, we should've just tested out how the bots trade against our quotes and do some quantitative analysis on it, but instead what we did was to manually optimizing over quoting with different edges and simply try to "guess" the best level of quoting. We turned out using the foreign ask price - 2 as our quoting level, which turned out to be pretty good but could've been better if we had did quantitative analysis on levels and found out about some rounding issues. The concern we had after this was that we might've been overfiting and the stake was high since if we ever quoted above the highest level the bot would trade at then we would've gotten 0 volume and made 0 pnl, therefore, we came up with an algorithm that detects how much volume we're getting each iteration and adapt the edge of quoting to that data. In backtest, we were able to get adaptive edge to around 100k but nothing more. We ended up using a combination of foreign ask - 2 and adaptive edge with adaptive edge triggered if we're not getting any volume at the level we're quoting at. This turned out to be kinda silly because the adpative edge algorithm was somewhat complicated and hard to control.

## round 3️⃣

Gift baskets, chocolate, roses, and strawberries were introduced in round 3. This round we mainly traded spreads, meaning the product of basket - synthetic, where synthetic is the sum of the price of products in a basket.

### Spread
This round, similar to last round, we had two hypotheses when staring at the given data. First hypothesis is that the synthetic would be leading baskets or vice versa, and the second hypothesis was that the spread is simply just mean reverting. We also seperated our workload and had eric work on leading indicators while jerry working on spread mean reverting strategy. **Eric, again, was unable to find any significant result cuz he's shit. Meanwhile, jerry made all the pnl with his incredible mean reverting strategy.** Initially, the mean reverting strategy was naive and hardcoded with a numbers optimized from past data. However, we didn't like hardcoding thresholds since hardcoding itself is very overfitting. Therefore, we came up with an adaptive yet simple formula for spreads. Our idea was that the mean of spread could be hardcoded because there should be an underlying reason for the spread value (i.e. the price of the basket itself), and the value itself wouldn't change drastically over a short period of time. However, the volatility of the spread itself is not really meaningful besides the fluctuations caused by supply/demand. Therefore we used a modified z score, using a hardcoded mean while a moving standard deviation. This turned out to work decently since the performance was similar across different days and dataset, while if we optimize the hardcoded threshold over different days, the pnl would have a high variance due to the hindsight bias of optimization. Although the pnl we generated this round was much less than round 2, we had faith because we thought the goal of round 3 is to not overfit and not lose money instead of make a lot of pnl.

After round 3, our team was ranked #2 overall.

## round 4️⃣

## round 5️⃣

[^1]: in the discord, we saw many teams using linear regression on past prices for this, likely inspired by [last year's second place submission](https://github.com/ShubhamAnandJain/IMC-Prosperity-2023-Stanford-Cardinal) 🌲. imho this was a bit silly! doing a linear regression in price space is really just a slightly worse way of performing an average, and you get high multicollinearity since each previous price is highly correlated with its neighbors, and you can really easily overfit (for example, if prices in your data slowly trended up, your learned LR coefficients can add up to be >1, meaning that your algo will bias towards buying, which might be spurious) 
[^2]: more specifically, we identified two participants in this market: a market making bot with order sizes quite uniform between 20 and 30, and a small bot that would occasionally cross fair with sizes uniform between 1 and 5.
[^3]: this was very very likely overfit, but the magnitude was so small that it didn't really make a difference in our pnl at all
