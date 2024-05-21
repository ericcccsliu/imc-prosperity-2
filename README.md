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

However, through looking at backtest logs in our dashapp, we discovered that many profitable trades were prevented by our position limits, as we were unable to long or short more than 20 amethysts (and starfruit) at any given moment. To fix this issue, we implemented a strategy to clear our position–our algorithm would do 0 ev trades, if available, just to get the position closer to 0, so that we'd be able to do more positive ev trades later on. This strategy bumped our pnl up by about 3%. 

### starfruit ⭐
For starfruit, we initially struggled to find a good fair price since its midprice is pretty noisy and would be fluctuating because of over/under aggressive orders. However, as we navigate through out dashapp we found out that at all times there seems to be a market making bot quoting relatively large sizes on both ends. Using the market making mid as a fair price turned out to be much less noisy and generated more pnl in backtests. We tested our algorithm on the website submission and with the pnl data given, we figured out that the website was also marking our pnl to the market making mid instead of the mid price. We were able to verify this by calculating internal pnl graph and it surprisingly matched the pnl graph given by website well. This boosted our confidence in using market making mid as fair price. Besides this, some research on the fair price showed that starfruit was slightly mean reverting, therefore we also implemented that in our fair calculation. The rest was very similar to amethysts where we took orders and quoted orders with a certain edge, and finally optimizing the parameters with a grid search.

After round 1, our team was ranked #3 overall.

## round 2️⃣


## round 3️⃣


## round 4️⃣


## round 5️⃣

