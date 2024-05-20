# linear utility
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

This repository contains research and algorithms for our team, Linear Utility, in IMC Prosperity 2024. We placed 2nd globally, with an overall score of 3,501,647 seashells, and took home $10,000 in prize money. 

## contributors ✨

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

Instead of relying heavily on open-source tools for visualization and backtesting, which many successful teams did, we decided instead to build our tools in-house. This, overall, was a good decision–while it didn't pay off as much as we hoped (more on this later), we were able to tailor our tools heavily for our own needs. We built two main tools for use throughout the competition: a backtester and a visualization dashboard. In our backtester, we were able to simulate trades taking our limit orders, allowing us to approximate PNL from market-making, which was a feature that the dominant open-source backtester notably lacked. Our visualization dashboard allowed us to observe price trends, investigate individual trades, and visualize the orderbook, which helped immensely in most rounds. 


## round 1️⃣

In round 1, we had access to two symbols to trade: amethysts and starfruit. For amethysts, the 

## round 2️⃣


## round 3️⃣


## round 4️⃣


## round 5️⃣



