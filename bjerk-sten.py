#!~/Documents/Trading/Devel/tosenv/bin/python3
#import the Quant Lib
import QuantLib as ql

spot = 446.48
strike = 445
interest_rate = 0.055
volatility = 0.2622
expiry = ql.Date(7, 2, 2025)
premium = 13.025

# Let the today date whenwe want to value a instrument be
NYSEcal = ql.UnitedStates(ql.UnitedStates.NYSE)
today = ql.Date().todaysDate()

# we can set evaluationDate in QL as
ql.Settings.instance().evaluationDate = today

riskFreeTS = ql.YieldTermStructureHandle(ql.FlatForward(today, interest_rate, ql.Actual365Fixed()))
dividendTS = ql.YieldTermStructureHandle(ql.FlatForward(today, 0.0, ql.Actual365Fixed()))
volatilityH = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(today, NYSEcal, volatility, ql.Actual365Fixed()))
spotH = ql.QuoteHandle(ql.SimpleQuote(spot))
process = ql.BlackScholesMertonProcess(spotH, dividendTS, riskFreeTS, volatilityH)

engine = ql.BjerksundStenslandApproximationEngine(process)
prem = ql.VanillaOption(ql.PlainVanillaPayoff(ql.Option.Put, spot), ql.AmericanExercise(today, expiry))
prem.setPricingEngine(engine)

print(ql.Settings.instance().evaluationDate);
print(F"{spot} {strike} {interest_rate} {volatility} {expiry} {premium}")
print(f"Premium:     {prem.NPV():11.6f}")
print(f"Delta:       {prem.delta():11.6f}")
print(f"Implied Vol: {prem.impliedVolatility(premium, process):11.6f}")