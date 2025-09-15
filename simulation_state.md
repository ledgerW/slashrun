Absolutely — you seed a scenario at t₀ with real (or realistic) data, then advance the world one turn at a time by applying update rules to each slice of state. Below is (1) a pragmatic mapping from state fields → trustworthy data sources → typical update functions, (2) a compact way to fold social-media influence into the loop, and (3) concrete Python scaffolding: a Pydantic global state plus reducer functions you can drop into a LangGraph pipeline.

---

# 1) What to load at t₀ and how to update each turn

### Core accounting scaffolding (so your books close)

* **National Accounts & sector frames:** Use the 2008 **System of National Accounts (SNA 2008)** to structure output/income/financial accounts and supply–use tables. ([UN Stats][1], [IMF eLibrary][2])
* **External accounts:** Use the IMF’s **BPM6** for current account, capital/financial account, IIP, reserve assets; it gives you the identity CA + KA + FA + ΔRes + Errors/Omissions = 0. ([IMF][3])

> **Turn update:** after shocks and policy, close the BOP by letting **ΔReserves** or **Errors/Omissions** absorb residuals (configurable). ([IMF][3])

### Macro (country level)

* **GDP, CPI/Inflation, Unemployment, Debt, Fiscal balance, Reserves:** World Bank **WDI**, ILO **ILOSTAT**, IMF **IFS/Data Portal** for broader coverage. ([DataBank][4], [World Bank Open Data][5], [ILOSTAT][6], [IMF][7], [IMF Data][8])
* **Updates:**

  * **Inflation**: New-Keynesian Phillips-curve step with expected inflation + output gap (lightweight NKPC). ([Federal Reserve Bank of Richmond][9])
  * **Policy rate**: **Taylor rule** variant $iₜ = r* + πₜ + φ_π(πₜ−π*) + φ_y·gapₜ$. ([Federal Reserve][10], [Federal Reserve Bank of Atlanta][11])
  * **Debt dynamics**: IMF formula $\Delta d ≈ \frac{i−g}{1+g}·d_{t−1} − pbₜ + SFA$ (primary balance pb, stock-flow adj SFA, nominal i & g). ([IMF][12])

### Trade, production linkages & prices

* **Trade flows & tariffs/NTMs:** **UN Comtrade**, **WTO Tariff & Trade Data/WITS**, **UNCTAD TRAINS** for applied/bound tariffs & NTMs. ([UN Comtrade][13], [ttd.wto.org][14], [World Trade Organization][15], [World Integrated Trade Solution][16], [trainsonline.unctad.org][17])
* **Input–Output linkages:** **OECD ICIO**, **WIOD**, **Eora MRIO** give you A (technical coefficients) for Leontief updates. ([OECD][18], [University of Groningen][19], [worldmrio.com][20])
* **Commodity prices:** **World Bank Pink Sheet**, **IMF Primary Commodity Prices** (energy/agri/metals). ([The World Bank][21], [IMF][22])

> **Turn update:** sector outputs $x$ from final demand $y$: $x = (I−A)^{-1} y$ (Leontief); propagate shocks to sectors/countries; re-price trade with tariff/NTM changes. ([estore.carecinstitute.org][23])

### FX, external pricing & flows

* **Exchange rates/yields:** IMF IFS/FRED for series (choose your provider). ([IMF][7], [FRED][24])
* **Updates:** **UIP**-style drift: $\Delta s ≈ (i_{dom}−i_{base}) + \rho$ (risk premium), with optional reversion. ([Federal Reserve][25])

### Energy, food, logistics

* **Energy balances:** **IEA World Energy Balances**, **Energy Institute Statistical Review** for production/consumption/inventories. ([IEA][26], [Energy Institute][27])
* **Global food price:** **FAO Food Price Index**; can add FAOSTAT CPI-Food. ([FAOHome][28], [files-faostat.fao.org][29])

> **Turn update:** inventory dynamics $I_{t+1}=I_t+Prod−Cons+Imports−Exports$, prices move via stock-to-use or Pink-Sheet exogenous path with pass-through. ([The World Bank][21])

### Finance & contagion

* **Cross-border bank exposures:** **BIS Consolidated Banking Statistics** (by nationality/counterparty). ([Bank for International Settlements][30], [BIS Data Portal][31])
* **Systemic propagation:** simple **leverage-targeting fire-sale** and/or **Eisenberg–Noe clearing** step for interbank networks. ([IDEAS/RePEc][32], [ms.mcmaster.ca][33])
* **Liquidity constraints:** optional Basel III **LCR** checks for banks. ([Bank for International Settlements][34])

### Security & geopolitics

* **Military expenditure & arms transfers:** **SIPRI**. Personnel via World Bank (sourced to **IISS Military Balance**). ([SIPRI][35], [DataBank][36])
* **Conflict events:** **UCDP GED** (public, geo-coded). ([UCDP][37])
* **Sanctions:** **Global Sanctions Data Base (GSDB) R4**. ([globalsanctionsdatabase.com][38], [EconStor][39])
* **Alliances/contiguity/distances:** **COW Formal Alliances**, **CEPII GeoDist/Gravity**. ([correlatesofwar.org][40], [cepii.fr][41])

---

# 2) Bringing social media & info flows into the model

**Signals you can ingest**

* **GDELT** (events + **tone** from news/TV; 15-min cadence) → protest/riot counts, sentiment by theme/geo. ([gdeltproject.org][42], [data.gdeltproject.org][43])
* **Google Trends** (topic salience by country/region; API in alpha as of July 2025) → normalized interest on narratives (e.g., “inflation”, “mobilization”). ([Google for Developers][44], [Google Help][45])

**How to use it (two-layer approach)**

1. **Opinion dynamics layer** for public/elite beliefs per country:

   * Run a **DeGroot/Friedkin–Johnsen** step: $o_{t+1}=W o_t + (I−W)b$ with stubbornness $b$. Tune $W$ from alliance/trade/social ties. Output is a vector of topic beliefs + an aggregate **policy pressure** index. ([PMC][46], [www2.cs.siu.edu][47])
2. **Event cascade layer** for protests/violence:

   * Use a **Hawkes** process intensity $\lambda_{t+1}= \omega\lambda_t+ \alpha\cdot \text{social\_pressure}_t + \beta \cdot \text{price\_shock}$ to drive probabilities of protest/riot events that then feed back into risk premia, supply disruptions, etc. ([arXiv][48])

**Transmission to the real economy**

* **Risk premium channel:** higher policy-pressure raises sovereign spread and FX risk premium (feeds UIP & debt dynamics). ([Federal Reserve][25], [IMF][12])
* **Policy constraint channel:** high pressure reduces feasible fiscal adjustment or raises odds of populist fiscal/price controls.
* **Supply disruption channel:** protest/conflict intensities hit IO supply and trade flows (via bilateral gravity + distance frictions). ([cepii.fr][49])

---

# 3) Concrete code: Pydantic global state + LangGraph-style reducers

> Lightweight, testable scaffolding you can extend. Keep parameters in a separate config so you can calibrate per scenario.

```python
# world_state.py
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import math

# ---------- State Slices ----------

class Macro(BaseModel):
    gdp: float                      # nominal GDP (LCU)
    potential_gdp: float            # nominal (LCU) for simplicity
    inflation: float                # YoY, in decimal (0.04 = 4%)
    unemployment: float             # rate, 0..1
    output_gap: float               # (gdp - potential)/potential
    primary_balance: float          # % of GDP (positive = surplus)
    debt_gdp: float                 # gross public debt / GDP
    neutral_rate: float             # r* (nominal)
    policy_rate: float              # i_t (nominal)
    inflation_target: float = 0.02  # π*
    sfa: float = 0.0                # stock-flow adjustment (% GDP)

class External(BaseModel):
    fx_rate: float                  # price of 1 base currency (e.g., USD) in local currency
    reserves_usd: float             # USD bn
    current_account_gdp: float      # % of GDP
    net_errors_omissions_gdp: float = 0.0

class Finance(BaseModel):
    sovereign_yield: float          # nominal yield
    credit_spread: float            # vs base (decimal)
    bank_tier1_ratio: float         # simple system average
    leverage_target: float = 10.0

class Trade(BaseModel):
    exports_gdp: float              # % of GDP
    imports_gdp: float              # % of GDP
    tariff_mfn_avg: float           # %
    ntm_index: float                # 0..1 (synthetic)
    terms_of_trade: float = 1.0     # relative price index

class EnergyFood(BaseModel):
    energy_stock_to_use: float      # ratio
    food_price_index: float         # level (e.g., FAO)
    energy_price_index: float       # level (e.g., Pink Sheet energy)

class Security(BaseModel):
    milex_gdp: float                # % of GDP
    personnel: int                  # active personnel
    conflict_intensity: float       # 0..1 (from UCDP/Hawkes)

class Sentiment(BaseModel):
    gdelt_tone: float               # -10..10 (normalized)
    trends_salience: float          # 0..100 normalized (z-scored upstream)
    policy_pressure: float          # 0..1 (DeGroot/FJ output)
    approval: float                 # 0..1

class CountryState(BaseModel):
    name: str
    macro: Macro
    external: External
    finance: Finance
    trade: Trade
    energy: EnergyFood
    security: Security
    sentiment: Sentiment

# Cross-country graphs/matrices stored sparsely for simplicity
Matrix = Dict[str, Dict[str, float]]

class GlobalState(BaseModel):
    t: int
    base_ccy: str = "USD"
    countries: Dict[str, CountryState] = Field(default_factory=dict)
    trade_matrix: Matrix = Field(default_factory=dict)          # value shares i->j
    interbank_matrix: Matrix = Field(default_factory=dict)      # exposure i->j (USD bn)
    alliance_graph: Matrix = Field(default_factory=dict)        # weights 0..1
    sanctions: Matrix = Field(default_factory=dict)             # sanction intensity i->j 0..1
    io_coefficients: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # A row-sums <1
    commodity_prices: Dict[str, float] = Field(default_factory=dict)            # e.g., 'oil': 85.0

# ---------- Reducers (pure-ish functions) ----------

def taylor_rule(m: Macro, phi_pi: float = 0.5, phi_y: float = 0.5) -> float:
    """Fed-style Taylor rule (Atlanta Fed / Board variants)."""
    # i_t = r* + π + φπ(π-π*) + φy*gap
    return m.neutral_rate + m.inflation + phi_pi*(m.inflation - m.inflation_target) + phi_y*m.output_gap

def update_policy_rate(country: CountryState) -> None:
    target = taylor_rule(country.macro)
    # Simple partial adjustment
    country.macro.policy_rate = 0.5*country.macro.policy_rate + 0.5*target

def update_output_gap(country: CountryState, demand_shock_pct: float = 0.0) -> None:
    # Leontief/IO would move sectoral demand; here just nudge the gap.
    gap = (country.macro.gdp*(1.0 + demand_shock_pct) - country.macro.potential_gdp) / max(country.macro.potential_gdp, 1e-9)
    # partial toward new gap
    country.macro.output_gap = 0.7*country.macro.output_gap + 0.3*gap

def update_inflation(country: CountryState, kappa: float = 0.1, beta: float = 0.6) -> None:
    # NKPC-ish: π_{t+1} = β E_t[π] + κ * gap  (use last π as proxy for expectations)
    pi_next = beta*country.macro.inflation + kappa*country.macro.output_gap
    country.macro.inflation = max(-0.05, min(0.5, pi_next))  # clip

def update_debt(country: CountryState) -> None:
    # IMF debt dynamics (approx, %GDP): Δd ≈ ((i - g)/(1+g)) * d - pb + sfa
    i = country.macro.policy_rate
    g_nom = country.macro.inflation + 0.02 + country.macro.output_gap*0.5  # toy nominal growth proxy
    d = country.macro.debt_gdp
    pb = country.macro.primary_balance
    dd = ((i - g_nom)/(1.0 + g_nom))*d - pb + country.macro.sfa
    country.macro.debt_gdp = max(0.0, d + dd)

def settle_bop(country: CountryState) -> None:
    # Close CA + KA + FA + ΔRes + EO = 0 (toy: use CA only & move reserves)
    ca = country.external.current_account_gdp
    gdp_usd = max(country.macro.gdp / max(country.external.fx_rate, 1e-9), 1e-6)  # very rough
    delta_res = -ca * gdp_usd  # move reserves opposite CA
    country.external.reserves_usd = max(0.0, country.external.reserves_usd + delta_res)

def update_fx(dom: CountryState, base: CountryState, rho: float = 0.0) -> None:
    # UIP-ish drift: Δlog s ≈ (i_dom - i_base) + ρ
    diff = dom.macro.policy_rate - base.macro.policy_rate + rho
    dom.external.fx_rate *= math.exp(diff)  # log step

def fire_sale_step(state: GlobalState, price_impact: float = 0.05) -> None:
    # Ultra-simple: if system Tier1 falls, mark down assets and widen spreads
    avg_tier1 = sum(c.finance.bank_tier1_ratio for c in state.countries.values())/max(len(state.countries),1)
    if avg_tier1 < 0.10:
        for c in state.countries.values():
            c.finance.credit_spread += 0.01
            c.finance.sovereign_yield = c.macro.policy_rate + c.finance.credit_spread

def interbank_loss_step(state: GlobalState, default_threshold: float = 0.06) -> None:
    # If a sovereign yield spikes, hit banks with exposures to that country’s banks (toy)
    stressed = {k for k,v in state.countries.items() if v.finance.sovereign_yield - v.macro.policy_rate > default_threshold}
    if not stressed:
        return
    for i in state.interbank_matrix:
        loss = sum(state.interbank_matrix[i].get(j,0.0)*0.1 for j in stressed)  # 10% LGD toy
        if i in state.countries:
            c = state.countries[i]
            c.finance.bank_tier1_ratio = max(0.0, c.finance.bank_tier1_ratio - loss*1e-3)

def social_belief_step(state: GlobalState, alpha_tone=0.02, alpha_trend=0.01, decay=0.9) -> None:
    # DeGroot-style averaging over alliance_graph to update policy_pressure
    # First, compute a raw signal per country
    raw = {}
    for k,c in state.countries.items():
        signal = alpha_tone*c.sentiment.gdelt_tone + alpha_trend*(c.sentiment.trends_salience/100.0 - 0.5)
        raw[k] = max(0.0, min(1.0, decay*c.sentiment.policy_pressure + signal))
    # Then diffuse over alliances (row-normalized)
    new_pp = {}
    for i in state.countries:
        nbrs = state.alliance_graph.get(i, {})
        if nbrs:
            s = sum(nbrs.values())
            spill = sum((nbrs[j]/s)*raw.get(j, raw[i]) for j in nbrs)
            new_pp[i] = 0.5*raw[i] + 0.5*spill
        else:
            new_pp[i] = raw[i]
    for k in state.countries:
        state.countries[k].sentiment.policy_pressure = new_pp[k]

def unrest_hazard_step(state: GlobalState, a=0.5, b=0.8, c=0.6, decay=0.8) -> None:
    # λ_{t+1}=decay*λ_t + a*policy_pressure + b*max(π-π*,0) + c*unemp_gap
    for ctry in state.countries.values():
        lam_prev = ctry.security.conflict_intensity
        pi_gap = max(0.0, ctry.macro.inflation - ctry.macro.inflation_target)
        u_gap = max(0.0, ctry.macro.unemployment - 0.05)
        lam = decay*lam_prev + a*ctry.sentiment.policy_pressure + b*pi_gap + c*u_gap
        ctry.security.conflict_intensity = max(0.0, min(1.0, lam))

def energy_food_step(ctry: CountryState) -> None:
    # Inventory-price feedback (very coarse): higher stock-to-use -> lower prices next turn
    su = ctry.energy.energy_stock_to_use
    ctry.energy.energy_price_index *= (1.0 - 0.05*(su-1.0))
    # Food prices respond to inflation & shocks modestly
    ctry.energy.food_price_index *= (1.0 + 0.3*ctry.macro.inflation)

# ---------- World-level turn reducer ----------

def reduce_world(state: GlobalState, base_ccy_country: str) -> GlobalState:
    base = state.countries[base_ccy_country]
    # 1) Social layer first (affects risk premia)
    social_belief_step(state)
    unrest_hazard_step(state)

    # 2) Country macro/price updates
    for code, c in state.countries.items():
        update_output_gap(c)
        update_inflation(c)
        update_policy_rate(c)
        c.finance.sovereign_yield = c.macro.policy_rate + c.finance.credit_spread
        energy_food_step(c)
        update_debt(c)
        settle_bop(c)

    # 3) FX drift vs base
    for code, c in state.countries.items():
        if code != base_ccy_country:
            rho = 0.01 * c.sentiment.policy_pressure  # social risk premium
            update_fx(c, base, rho=rho)

    # 4) Financial network stress propagation
    fire_sale_step(state)
    interbank_loss_step(state)

    # Advance time
    state.t += 1
    return state
```


---

## Notes on sourcing & calibration

* **Data frames:**

  * **Macro & prices:** WDI/ILOSTAT/IFS/FRED. ([DataBank][4], [ILOSTAT][6], [IMF][7], [FRED][24])
  * **Trade/tariffs/NTMs:** Comtrade + WTO/WITS + UNCTAD TRAINS. ([UN Comtrade][13], [ttd.wto.org][14], [World Integrated Trade Solution][16], [trainsonline.unctad.org][17])
  * **IO tables:** OECD ICIO / WIOD / Eora. ([OECD][50], [University of Groningen][19], [worldmrio.com][20])
  * **Energy/food:** IEA + Energy Institute + FAO FFPI + Pink Sheet. ([IEA][26], [Energy Institute][27], [FAOHome][28], [The World Bank][21])
  * **Finance:** BIS CBS for cross-border exposure; Basel III LCR doc for simple liquidity checks. ([BIS Data Portal][31], [Bank for International Settlements][34])
  * **Geopolitics:** SIPRI (milex/arms), UCDP (events), GSDB (sanctions), COW Alliances, CEPII distances. ([SIPRI][35], [UCDP][37], [globalsanctionsdatabase.com][38], [correlatesofwar.org][40], [cepii.fr][41])
  * **Info layer:** GDELT (events/tone) + Google Trends (salience). ([gdeltproject.org][42], [data.gdeltproject.org][43], [Google for Developers][44])

* **Equation choices:**

  * Taylor rule and NKPC sources: **Federal Reserve** explainer + research references. ([Federal Reserve][10], [Federal Reserve Bank of Atlanta][11], [Federal Reserve Bank of Richmond][9])
  * Debt dynamics: **IMF TNM** (2010, 2021 updates). ([IMF][12])
  * UIP drift: Fed research on UIP. ([Federal Reserve][25])
  * Fire-sale & interbank: Greenwood–Landier–Thesmar (fire sales) and **Eisenberg–Noe** clearing. ([IDEAS/RePEc][32], [ms.mcmaster.ca][33])

---

## Quick “how to use”

1. **Seed t₀** with: WDI/IFS macro; ICIO/WIOD/Eora A-matrix; Comtrade bilateral trade; WTO/WITS tariffs; BIS interbank; SIPRI/UCDP/GSDB/COW; IEA/Energy-Institute/FAO/Pink-Sheet; GDELT/Trends. ([DataBank][4], [IMF][7], [OECD][18], [University of Groningen][19], [worldmrio.com][20], [UN Comtrade][13], [ttd.wto.org][14], [World Integrated Trade Solution][16], [BIS Data Portal][31], [SIPRI][35], [UCDP][37], [globalsanctionsdatabase.com][38], [correlatesofwar.org][40], [cepii.fr][49], [IEA][26], [Energy Institute][27], [FAOHome][28], [The World Bank][21], [gdeltproject.org][42], [Google for Developers][44])
2. **Run a turn** by calling `reduce_world(state, base_ccy_country="USA")`.
3. **Scenario knobs:** sanction intensity (sanctions\[i]\[j]), tariff shocks, policy overrides (override `policy_rate`), narrative shocks (boost `trends_salience`/`gdelt_tone`), energy supply disruptions, bank capital hits, etc.

If you want, I can tailor the state slices and reducers to your exact scope (e.g., more granular sectors, explicit Leontief inverse per region/industry, or a proper Eisenberg–Noe solver), but the scaffold above will let you spin a useful, explainable turn-based world right away.

[1]: https://unstats.un.org/unsd/nationalaccount/sna2008.asp?utm_source=chatgpt.com "System of National Accounts (2008 SNA) - UN Statistics Division"
[2]: https://www.elibrary.imf.org/display/book/9789211615227/9789211615227.xml?utm_source=chatgpt.com "System of National Accounts 2008"
[3]: https://www.imf.org/external/pubs/ft/bop/2007/pdf/bpm6.pdf?utm_source=chatgpt.com "Balance of Payments and International Investment Position ..."
[4]: https://databank.worldbank.org/source/world-development-indicators?utm_source=chatgpt.com "World Development Indicators | DataBank"
[5]: https://data.worldbank.org/indicator?utm_source=chatgpt.com "Indicators"
[6]: https://ilostat.ilo.org/data/snapshots/unemployment-rate/?utm_source=chatgpt.com "Unemployment rate - ILOSTAT"
[7]: https://www.imf.org/en/Data?utm_source=chatgpt.com "IMF Data"
[8]: https://data.imf.org/en/news/accessing%20international%20financial%20statistics?utm_source=chatgpt.com "Accessing International Financial Statistics (IFS)"
[9]: https://www.richmondfed.org/-/media/richmondfedorg/publications/research/economic_quarterly/2008/fall/pdf/hornstein.pdf?utm_source=chatgpt.com "Introduction to the New Keynesian Phillips Curve"
[10]: https://www.federalreserve.gov/monetarypolicy/policy-rules-and-how-policymakers-use-them.htm?utm_source=chatgpt.com "Policy Rules and How Policymakers Use Them"
[11]: https://www.atlantafed.org/cqer/research/taylor-rule?utm_source=chatgpt.com "Taylor Rule Utility"
[12]: https://www.imf.org/external/pubs/ft/tnm/2010/tnm1002.pdf?utm_source=chatgpt.com "[PDF] A Practical Guide to Public Debt Dynamics, Fiscal Sustainability, and ..."
[13]: https://comtrade.un.org/?utm_source=chatgpt.com "UN Comtrade Database - the United Nations"
[14]: https://ttd.wto.org/en?utm_source=chatgpt.com "WTO Tariff & Trade Data - World Trade Organization"
[15]: https://www.wto.org/english/tratop_e/tariffs_e/database_explanation_e.htm?utm_source=chatgpt.com "Tariff download facility - Brief explanation and user guide"
[16]: https://wits.worldbank.org/witsapiintro.aspx?lang=en&utm_source=chatgpt.com "WITS API"
[17]: https://trainsonline.unctad.org/?utm_source=chatgpt.com "UNCTAD Trains"
[18]: https://www.oecd.org/en/data/datasets/inter-country-input-output-tables.html?utm_source=chatgpt.com "Inter-Country Input-Output tables | OECD"
[19]: https://www.rug.nl/ggdc/valuechain/wiod/wiod-2016-release?lang=en&utm_source=chatgpt.com "WIOD 2016 Release"
[20]: https://worldmrio.com/documentation/?utm_source=chatgpt.com "Eora Documentation"
[21]: https://thedocs.worldbank.org/en/doc/18675f1d1639c7a34d463f59263ba0a2-0050012025/related/CMO-Pink-Sheet-August-2025.pdf?utm_source=chatgpt.com "CMO-Pink-Sheet-August-2025.pdf"
[22]: https://www.imf.org/en/Research/commodity-prices?utm_source=chatgpt.com "IMF Primary Commodity Prices"
[23]: https://estore.carecinstitute.org/wp-content/uploads/2020/04/Day-01_Session-02_Leontief-Output-Model_Presentation.pdf?utm_source=chatgpt.com "Leontief Output Model - carec"
[24]: https://fred.stlouisfed.org/docs/api/fred/?utm_source=chatgpt.com "St. Louis Fed Web Services: FRED® API"
[25]: https://www.federalreserve.gov/pubs/ifdp/2003/752/revision/ifdp752r.pdf?utm_source=chatgpt.com "Uncovered Interest Parity: It Works, But Not For Long"
[26]: https://www.iea.org/data-and-statistics/data-product/world-energy-balances?utm_source=chatgpt.com "World Energy Balances - Data product"
[27]: https://www.energyinst.org/statistical-review?utm_source=chatgpt.com "Home | Statistical Review of World Energy"
[28]: https://www.fao.org/worldfoodsituation/foodpricesindex/en/?utm_source=chatgpt.com "FAO Food Price Index"
[29]: https://files-faostat.fao.org/production/CP/CP_e.pdf?utm_source=chatgpt.com "Food and General Consumer Price Indices Methodology"
[30]: https://www.bis.org/statistics/consstats.htm?utm_source=chatgpt.com "Consolidated banking statistics - overview | BIS Data Portal"
[31]: https://data.bis.org/topics/CBS/tables-and-dashboards?utm_source=chatgpt.com "Consolidated banking statistics - tables & dashboards"
[32]: https://ideas.repec.org/a/eee/jfinec/v115y2015i3p471-485.html?utm_source=chatgpt.com "Vulnerable banks"
[33]: https://ms.mcmaster.ca/tom/Research%20Papers/EiseNoe01.pdf?utm_source=chatgpt.com "Systemic Risk in Financial Systems"
[34]: https://www.bis.org/publ/bcbs238.pdf?utm_source=chatgpt.com "Basel III: The Liquidity Coverage Ratio and liquidity risk ..."
[35]: https://www.sipri.org/databases/milex/sources-and-methods?utm_source=chatgpt.com "Sources and methods"
[36]: https://databank.worldbank.org/metadataglossary/world-development-indicators/series/MS.MIL.TOTL.P1?utm_source=chatgpt.com "Armed forces personnel, total"
[37]: https://ucdp.uu.se/downloads/?utm_source=chatgpt.com "UCDP Dataset Download Center"
[38]: https://globalsanctionsdatabase.com/?utm_source=chatgpt.com "Global Sanctions Database (GSDB)"
[39]: https://www.econstor.eu/handle/10419/301174?utm_source=chatgpt.com "The Global Sanctions Data Base - Release 4: The heterogeneous effects ..."
[40]: https://correlatesofwar.org/data-sets/formal-alliances/?utm_source=chatgpt.com "Formal Alliances (v4.1) - Correlates of War"
[41]: https://www.cepii.fr/distance/noticedist_en.pdf?utm_source=chatgpt.com "[PDF] Notes on CEPII's distances measures"
[42]: https://www.gdeltproject.org/?utm_source=chatgpt.com "The GDELT Project"
[43]: https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf?utm_source=chatgpt.com "the gdelt global knowledge graph (gkg) data format ..."
[44]: https://developers.google.com/search/docs/monitor-debug/trends-start?utm_source=chatgpt.com "Get started with Google Trends | Google Search Central"
[45]: https://support.google.com/trends/answer/4365533?hl=en&utm_source=chatgpt.com "FAQ about Google Trends data"
[46]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9352787/?utm_source=chatgpt.com "A framework to analyze opinion formation models - PMC"
[47]: https://www2.cs.siu.edu/~hexmoor/classes/CS539-F10/Friedkin.pdf?utm_source=chatgpt.com "Social Influence Networks and Opinion Change"
[48]: https://arxiv.org/pdf/1708.06401?utm_source=chatgpt.com "1A Tutorial on Hawkes Processes for Events in Social Media"
[49]: https://www.cepii.fr/DATA_DOWNLOAD/gravity/doc/Gravity_documentation.pdf?utm_source=chatgpt.com "[PDF] The CEPII Gravity Database"
[50]: https://www.oecd.org/content/dam/oecd/en/publications/reports/2023/11/development-of-the-oecd-inter-country-input-output-database-2023_3fa45b4c/5a5d0665-en.pdf?utm_source=chatgpt.com "[PDF] Development of the OECD Inter Country Input-Output Database ..."
