---
title: "Forecasting Asia With One Number Is How Spreadsheets Develop Main Character Syndrome"
description: "Alpha without perfect forecasts gets very real when the market is China, Asia, policy risk, FX risk, and supply-chain chess."
categories:
  - quantitative-finance
tags:
  - alpha
  - emerging-markets
  - frontier-markets
  - forecasting
  - portfolio-construction
math: true
mermaid: true
---
Useful alpha research does not always require a precise forecast of each asset’s future return.

That becomes painfully obvious when the investment universe is China or broader Asia.

Nobody has one clean forecast for China property, U.S.-China export controls, Taiwan risk, yen volatility, India growth, Korean semiconductor exposure, or Southeast Asian supply-chain migration.

And if someone does, congratulations to their spreadsheet for achieving geopolitical enlightenment.

The better research question is not:

> “What exactly will China GDP, exports, earnings, or policy look like next year?”

The better question is:

> “Which assets are mispriced relative to the distribution of possible outcomes?”

That distinction matters.

Because Asia is not one trade.

China tech is not Japan reform.

Japan reform is not India infrastructure.

India infrastructure is not Southeast Asia supply-chain relocation.

Southeast Asia supply-chain relocation is not Korean memory-cycle exposure.

The region is a portfolio of very different risks pretending to be one geographic label.

## The forecast is not the decision

A precise forecast sounds useful.

A better decision is useful.

Those are not the same thing.

You may never know the exact future path of China’s property market. But you can still ask whether a Chinese bank, insurer, consumer name, internet platform, or industrial exporter is being priced for too much distress or not enough.

China’s property sector remains a clear example. A Reuters poll in August said China home prices were expected to fall **3.4% in 2026**, while property investment and sales declines were expected to deepen, showing the sector had not fully stabilized.

That does not automatically mean:

> “Avoid China.”

It means:

> “Raise the hurdle rate.”

A China investment can still be attractive if valuation, balance sheet quality, policy support, liquidity, and downside compensation are strong enough.

That is not clairvoyance.

That is underwriting.

## Scenario-weighted alpha beats fake precision

A cleaner way to think about China and Asia research is scenario-weighted expected return:

$$
\mathbb{E}[R_i] = \sum_{s=1}^{S} p_s R_{i,s}
$$

Where:

- `i` = asset, sector, country, or trade
- `s` = scenario
- `p_s` = probability of scenario `s`
- `R_{i,s}` = return of investment `i` under scenario `s`

Then make it more realistic:

$$
\begin{aligned}
\mathbb{E}[R_i^{\mathrm{net}}] ={}& \sum_{s=1}^{S} p_s R_{i,s} \\
&- C_i^{\mathrm{trade}} - C_i^{\mathrm{hedge}} \\
&- C_i^{\mathrm{liquidity}} - C_i^{\mathrm{policy}}
\end{aligned}
$$

Where:

- `C_i^{trade}` = transaction costs
- `C_i^{hedge}` = hedging costs
- `C_i^{liquidity}` = liquidity or capacity costs
- `C_i^{policy}` = geopolitical or policy-risk penalty

A useful research workflow is a sequence of decisions, not a single point forecast. This conceptual map shows the handoff from information to an implementable choice; it is not historical performance data.

```mermaid
flowchart LR
  A["Market information"] --> B["Scenario-weighted outcomes"]
  B --> C["Relative opportunity"]
  C --> D["Adjust for FX, costs, liquidity, policy, and tail risk"]
  D --> E["Rank, size, hedge, or pass"]
```

That last term is where a lot of real-world investing lives.

It is also where many backtests go to die quietly and then reappear later as a paid newsletter.

## China is not cheap just because it is down

Valuation alone is not a thesis.

A cheap asset can be mispriced.

It can also be cheap because the market read the footnotes.

For China-related assets, **Is it cheap?** is only the starting question. The better question is: **Is it cheap after adjusting for policy risk, FX risk, liquidity risk, and tail risk?**

A simple scoring framework could look like:

$$
\mathrm{Score}_i =
\operatorname{zscore}(V_i)
+ \operatorname{zscore}(E_i)
+ \operatorname{zscore}(Q_i)
+ \operatorname{zscore}(M_i)
- \operatorname{zscore}(L_i)
- \operatorname{zscore}(F_i)
- \operatorname{zscore}(P_i)
$$

Here, `V` is valuation, `E` earnings revisions, `Q` quality, `M` momentum, `L` leverage, `F` FX volatility, and `P` policy risk.

This does not pretend to forecast the future precisely.

It asks whether the opportunity is attractive after adjusting for the risks that actually matter.

That is the entire point.

A good signal does not need to say:

> “This stock will return 18.4% over the next 12 months.”

It can say:

> “Relative to the region, this asset has better valuation support, cleaner balance-sheet quality, improving revisions, and lower policy-adjusted downside.”

That is often enough to improve the decision.

## Asia is a relative-value problem

One mistake is treating Asia as a single macro bet.

It is not.

Recent commentary around Asia has highlighted the region’s diversity: Japan corporate reform, India demographic and infrastructure growth, China innovation, and Southeast Asia’s role in supply-chain diversification all represent different exposures.

That matters because relative opportunity may be more important than absolute forecasting.

The research question becomes:

> “Which Asian exposure gives the best compensated risk?”

Not:

> “Which country has the best headline story?”

A simple relative return framework:

$$
\mathrm{RAR}_i =
\frac{\mathbb{E}[R_i^{\mathrm{net}}]}{\sigma_i + \lambda T_i}
$$

Where:

- `RAR_i` = risk-adjusted return score
- `R_i^{net}` = net return
- `sigma_i` = volatility
- `T_i` = scenario downside
- `lambda` = penalty for tail risk

This is not perfect.

But it is much better than pretending a single macro narrative captures the whole region.

## Add the currency layer, because USD investors live in USD

Asia investing also forces investors to respect FX.

A local-market return and a U.S.-dollar return are not the same thing:

$$
1 + R_{\mathrm{USD}} = (1 + R_{\mathrm{Local}})(1 + R_{\mathrm{FX}})
$$

Approximation:

$$
R_{\mathrm{USD}} \approx R_{\mathrm{Local}} + R_{\mathrm{FX}}
$$

So if a Japan equity trade returns 10% locally but the yen weakens 8% against the dollar, the U.S.-dollar investor did not experience the same trade.

They experienced a good equity thesis partially eaten by currency.

Very rude of math.

This is why “good company, bad currency” can still become a disappointing portfolio result.

And why hedging is not some academic footnote.

It is part of the trade.

## The China trade is also a deflation trade

One underappreciated way to think about China is as a global deflationary vendor.

That sounds dramatic.

It is also basically the business model.

China has spent decades building enormous manufacturing scale, deep supply chains, export capacity, and cost advantages. The result is that the rest of the world gets cheaper goods, cheaper inputs, cheaper equipment, cheaper clean-tech components, cheaper electronics, and cheaper manufacturing capacity.

Consumers like that.

Companies like that.

Politicians like complaining about it while their economies quietly rely on it.

This is the uncomfortable part of the China investment debate.

China can pressure global goods prices lower while simultaneously making the world dependent on the exact supply chain it claims to want to diversify away from.

That is not just a macro story.

It is a portfolio-construction problem.

China’s scale can be deflationary for global goods markets, but it can also compress margins for manufacturers outside China. If Chinese firms can produce at lower cost and accept thinner margins, competitors elsewhere either lower prices, lose share, lobby for tariffs, or pretend “reshoring” will be easy until the invoice arrives.

This is the dynamic investors need to underwrite:

> China can be cheap enough to be useful, large enough to be unavoidable, and politically difficult enough to require a discount.

That is a weird asset.

Useful, risky, deflationary, systemically embedded, and very annoying to model.

Reuters recently reported that China posted a record trade surplus of nearly **$1.2 trillion in 2025**, while European policymakers have been pressuring China over its export surge and trade imbalance. Reuters also reported that some G20 trade ministers signed a U.S.-led statement criticizing structural excess factory capacity, while China rejected the overcapacity argument as protectionist framing.

So the question is not simply:

> “Is China investable?”

The better question is:

> “Where is China’s deflationary manufacturing machine helping margins, where is it destroying margins, and where is the market underpricing the dependency?”

That can be modeled as an exposure:

$$
\begin{aligned}
D_i ={}& w_1 I_i + w_2 X_i \\
  &- w_3 C_i - w_4 T_i - w_5 S_i
\end{aligned}
$$

Where:

- `I_i` = benefit from cheap Chinese inputs
- `X_i` = exposure to Chinese end demand
- `C_i` = margin pressure from Chinese competitors
- `T_i` = risk of trade barriers or policy intervention
- `S_i` = fragility from China-linked supply-chain dependence

This makes the China question more useful.

A company that depends on cheap Chinese inputs may benefit from China’s deflationary export machine.

A company competing directly against Chinese overcapacity may get its margins manufactured down to the floor.

Same country.

Different exposure.

Very different investment result.

This is also why “decoupling” is easier to say than to execute.

If the world is hooked on cheap Chinese manufacturing, breaking that dependency may be strategically attractive but economically inflationary. You can move supply chains, but you cannot always move cost structure, labor availability, supplier density, infrastructure, and manufacturing know-how at the same price.

The result is a tradeoff:

$$
\mathrm{Resilience} \uparrow
\qquad \Rightarrow \qquad
\mathrm{CostEfficiency} \downarrow
$$

At least in the short run.

That is the hard part.

China’s deflationary pressure is useful until it becomes dependency.

Dependency is efficient until it becomes geopolitical risk.

Geopolitical risk is manageable until the supply chain you optimized for cost becomes the supply chain you need to rebuild under stress.

That is not a clean point forecast.

That is a distribution of outcomes.

And that is exactly why China/Asia investing should be framed as decision research, not spreadsheet prophecy.

## Policy risk is not a vibe

Policy risk is often discussed vaguely.

It should not be.

In China and Asia research, policy risk can be a first-order variable.

U.S.-China technology controls are one example. Reuters recently reported that a contractor linked to Super Micro pleaded guilty in a scheme to illegally export servers containing advanced Nvidia AI chips to China; prosecutors had charged several people with conspiring to divert about **$2.5 billion** of U.S. AI technology to China without required licenses.

That kind of event is not just legal noise.

It affects supply chains, semiconductor exposure, cloud infrastructure, AI compute access, compliance costs, and investor perception.

So the model should not treat policy risk as a paragraph at the end.

It should enter the underwriting.

For example:

$$
\begin{aligned}
P_i ={}& w_1 E_i + w_2 S_i + w_3 U_i \\
  &+ w_4 C_i + w_5 X_i
\end{aligned}
$$

Then the expected return can be adjusted:

$$
\mathbb{E}[R_i^{\mathrm{policy\text{-}adj}}]
= \mathbb{E}[R_i] - \theta P_i
$$

Where:

- `E_i` = export-control exposure
- `S_i` = sanctions exposure
- `U_i` = regulatory uncertainty
- `C_i` = capital-control risk
- `X_i` = supply-chain sensitivity
- `theta` = penalty per unit of policy risk

Again, not perfect.

But better than pretending geopolitics is impossible to model, then accidentally taking a giant geopolitics position.

## Conditional alpha matters

A factor is rarely useful in every environment.

A value signal in China during policy easing, improving credit impulse, and lower geopolitical tension is not the same as a value signal during property stress, capital outflow pressure, and weak household confidence.

Same factor.

Different regime.

Different payoff.

A conditional alpha model could look like:

$$
\begin{aligned}
\alpha_{i,t} ={}& \beta_V V_{i,t} + \beta_M M_{i,t} \\
                &+ \beta_Q Q_{i,t} + \beta_L L_t \\
                &+ \beta_F F_t + \beta_P P_t + \epsilon_{i,t}
\end{aligned}
$$

Here, `V`, `M`, and `Q` are value, momentum, and quality; `L`, `F`, and `P` are liquidity regime, FX regime, and policy risk.

But the more useful version includes interactions:

$$
\begin{aligned}
\alpha_{i,t} ={}& \beta_1 V_{i,t} \\
&+ \beta_2 (V_{i,t} \times L_t) \\
&+ \beta_3 (V_{i,t} \times P_t) \\
&+ \beta_4 M_{i,t} + \beta_5 Q_{i,t} + \epsilon_{i,t}
\end{aligned}
$$

Because the signal does not live in a vacuum.

It lives in a regime.

A cheap China stock with improving revisions and policy support is not the same trade as a cheap China stock with deteriorating earnings, weak liquidity, and rising policy risk.

Both screen as “cheap.”

Only one might deserve capital.

## A practical example: China tech vs. Southeast Asia supply chains

Suppose the broad theme is:

> “Asia benefits from AI, manufacturing relocation, and global supply-chain rebalancing.”

That sounds nice.

It is also not specific enough to trade.

A China AI infrastructure investment may offer innovation exposure and scale, but it may carry export-control risk, geopolitical discounting, and policy uncertainty.

A Southeast Asia supply-chain investment may offer China+1 exposure, but it may also depend on infrastructure, energy costs, labor capacity, foreign direct investment, and whether relocated production actually earns attractive margins.

So the decision is not:

> “Asia bullish or bearish?”

The decision is:

> “Which exposure gives the best risk-adjusted participation in the theme?”

That can be framed as:

$$
\begin{aligned}
H_i ={}& a_1 G_i + a_2 M_i + a_3 S_i \\
  &- a_4 F_i - a_5 P_i - a_6 V_i
\end{aligned}
$$

Here, `G` is growth exposure, `M` margin upside, `S` supply-chain benefit, `F` FX risk, `P` policy risk, and `V` valuation risk.

Now the research is doing something useful.

It is not asking for a perfect forecast.

It is asking which trade improves after adjusting for the risks that actually determine realized returns.

## The point

The best China/Asia research probably does not start with:

> “Here is the exact future.”

It starts with:

> “Here is the distribution of possible futures, and here is the decision that improves under that distribution.”

That is the entire idea behind alpha without perfect forecasts.

The goal is not to predict every macro variable with fake precision.

The goal is to map information to better decisions.

Especially in markets where the real edge may come from understanding:

- which risks are priced  
- which risks are ignored  
- which risks are over-discounted  
- which risks can be hedged  
- which risks should simply be avoided  

That is less exciting than pretending one model can forecast China, Asia, policy, currencies, and supply chains in one clean number.

But it is much closer to how real investment decisions work.

Alpha does not require clairvoyance.

It requires better decision-making under uncertainty.

Which is less magical.

And usually more profitable.
