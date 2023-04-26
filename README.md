<h1 align="center">
    <sub>
        <img src="https://github.com/daniel-boctor/norbertsgambit.net/blob/main/norbertsgambit/NG/static/NG/norberts-gambit.png" height="38" width="38">
    </sub>
    <a href="https://norbertsgambit.net">Norbert's Gambit Calculator</a>
</h1>

Norbert's Gambit is a technique used by many Canadian investors that allows the exchange of CAD / USD at rates that would otherwise be unobtainable to retail investors. This tool serves the purpose of being a one stop shop for investors to gauge ex-ante and ex-post trading expenses, as well as providing ready-to-file tax information for taxable investors.

***

* [Features](#features)
* [Tax Engine](#tax-engine)
* [Feature Requests](#feature-requests)

## Features
* __Bid / ask spreads:__ This tool accounts for the live bid / ask spread on both DLR.TO and DLR.U.TO. Most existing tools don't account for this, and only pull a single quoted price. Not only is it important to know the exact prices at which you will trade for the sake of accuracy, but also because it is likely that potential ECN fees will be codependent on whether you choose to transact at the bid or ask.

* __FX rates:__ Most tools only pull the current FX rate, and use it to calculate trading costs throughout the entire pair of trades. I have implemented the ability to specify an FX rate on both the date of purchase and the date of sale. The benefits of this are twofold. First, inbetween the purchase and sale date, the investor may experience a meaningful amount of drift in currency prices. If this is not accounted for, the trading costs will not be accurate. Second, the integrity of the data of past trades will not be skewed based off the interest rate drift from the time the trades occured to the time the calculation is being ran.

* __Implicit costs:__ Most tools will only account for explicit trading costs, defined as the sum of the ECN fees and commissions. In addition to explicit costs, this tool also accounts for implicit trading costs. These consist of both the bid / ask spreads that could be either payed or earned based on the investors liquidity preferences, and the profit / loss realized from FX rate drift while the trades are settling and the shares are journaling.

## Tax Engine
* Tax information can be generated on the trade, portfolio, year, or global level, and contains everything that is required on a Canadian tax return.
* All figures are quoted in CAD, and conforms to standards outlined by the Canada Revenue Agency. For all trades, the FX rate effective on the date of transaction will be used, as opposed to the date of settlement, to align tax figures with the underlying economic realities experienced by the investor. For further information on how capital gains / losses are treated under Canadian tax code, please refer to [T4037(E)](https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/t4037/capital-gains.html).

## Feature Requests
* Since we first launched in January 2022, a wide variety of feature requests from community members have contributed to the success of the site. Some of these requests have include the ability to change the pair of interlisted securities being used for the trade, as well as the options to specify a brokers FX spread / dealers FX rate for direct cost comparison between methods.
* If you would like to request any type of additional functionality, I would be happy to implement it. Feel free to [reach out](mailto:daniel.boctor@ontariotechu.net)!

***

As of January 2023, [norbertsgambit.danielboctor.com](https://norbertsgambit.danielboctor.com) has been permanantly moved to [norbertsgambit.net](https://norbertsgambit.net)