# Copulas

Copulas are a way of estimating the multivariate distribution of independently modelled univariate distributions. They are the way of modelling the joint distribution of a set of random variables.


Going through an example might be useful. Imagine we have $1000 in a bond ETF and $1000 dollars in a NASDAQ ETF. What is the chance that they both drop by 5% on the same day?

We could approach this question using a multivariate bayesian approach, model a hidden factor that affects both the prices of the bond ETF and the Nasdaq ETF, estimate the most likely parameters, sample from the posterior and record the proportion of times that we see a greater than 10% drop in each of the ETFs. That can be a lot of work especially if we have already independently modelled the underlying assets.

First let's work out the distributions of each asset independently. We'll be using the normal distribution as that is conceptually the easiest to work with although the copula approach works any underlying distributions.

\[
  X \sim \mathcal{N}(\mu,\,\sigma^{2})\,.
\] 


``` py title="Get the paramters for AAPL and MSFT returns distribution"
import yfinance as yf

tickers = yf.Tickers('msft aapl')
df = tickers.history(period="max").dropna()
aapl_returns = df['Close']['AAPL'].pct_change().dropna()
msft_returns = df['Close']['MSFT'].pct_change().dropna()

print("AAPL return distribution")
print(aapl_returns.describe())
# AAPL return distribution
# count    9257.000000
# mean        0.001191
# std         0.027520
# min        -0.518692
# 25%        -0.012319
# 50%         0.000219
# 75%         0.014386
# max         0.332281

print("MSFT return distribution")
print(msft_returns.describe())
# MSFT return distribution
# count    9257.000000
# mean        0.001130
# std         0.021343
# min        -0.301159
# 25%        -0.009212
# 50%         0.000353
# 75%         0.011335
# max         0.195652
```

``` py title="make CDF for AAPL and MSFT returns" 
from scipy.stats import norm

def msft_return_probability(returns:float) -> float:
    """CDF of MSFT returns"""
    mean = 0.00113
    std = 0.021343
    zscore = (returns - mean)/std
    return norm.cdf(zscore)

def aapl_return_probability(returns:float) -> float:
    """CDF of AAPL returns"""
    mean = 0.00111
    std = 0.027520
    zscore = (returns - mean)/std
    return norm.cdf(zscore)

```



