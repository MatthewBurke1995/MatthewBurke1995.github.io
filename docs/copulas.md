# Copulas

Copulas are a way of estimating the multivariate distribution of independently modelled univariate distributions. They are a useful way of modelling the joint distribution of a set of random variables.

Going through an example might be useful. Imagine we have $1000 in a bond ETF and $1000 dollars in a NASDAQ ETF. What is the chance that they both drop by 5% on the same day?

We could approach this question using a multivariate bayesian approach, model a hidden factor that affects both the prices of the bond ETF and the Nasdaq ETF, estimate the most likely parameters, sample from the posterior and record the proportion of times that we see a greater than 10% drop in each of the ETFs. That can be a lot of work especially if we have already independently modelled the underlying assets.

First let's work out the distributions of each asset independently. We'll be using the normal distribution as that is conceptually the easiest to work through, although the copula approach works for any underlying distributions.

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
    """CDF of MSFT returns
    >>> round(msft_return_probability(-0.05),2)
    0.01
    """
    mean = 0.00113
    std = 0.021343
    zscore = (returns - mean)/std
    return norm.cdf(zscore)

def aapl_return_probability(returns:float) -> float:
    """CDF of AAPL returns
    >>> round(aapl_return_probability(-0.05),2)
    0.03
    """
    mean = 0.00111
    std = 0.027520
    zscore = (returns - mean)/std
    return norm.cdf(zscore)

```

We now have our undelying univariate probably functions for each set of assets. Now we have to somehow combine them. The easiest way would be to assume that they are independent of each other. We could write an independent copula like this:

``` py
def independent_copula(u, v):
    return u * v
```

Using this copula the chance of them both going down at least 5% would be 0.01 * 0.03 or 3/10000. 

If they were perfectly correlated then the chance of them both going down at least 5% would be a much higher number, something like:

``` py
def correlated_copula(u,v):
    return max(u,v)
```
!!! note
    When we read this function for the inputs correlated_copula(0.8,0.3) we should say "What is the chance of at least the 80th percentile of returns and at least the 30th percentile of returns?" If they are completely correlated then when one distribution returns the 80th percentile then the other distribution must also return the 80th percentile, therefore: 
    ``` py 
        correlated_copula(0.8,0.3) == correlated_copula(0.8,0.8) 
    ```


Which gives us a much more realistic 3% chance, this is problematic in that we cannot prove that they are completely correlated and likely overestimates the risk. Going by this metric we could reduce our risk by dropping AAPL entirely and putting all our money in MSFT, this is the opposite of the mantra that "Diversification is the only free lunch.”

Let's take the assumption that they are inversely correlated.

``` py
def uncorrelated_copula(u,v):
    return max(u+v-1,0)
```

This gives us a value of 0, if AAPL were truly uncorrelated with MSFT then there would be no days in which they both lose money.


``` py
import numpy as np
def gumbel_copula(u, v, alpha):
    u = np.asarray(u)
    v = np.asarray(v)
    # compute copula
    copula = np.exp(-(((-np.log(u))**alpha + (-np.log(v))**alpha))**(1/alpha))
    return copula
```

