import yfinance as yf
from scipy.stats import norm
from scipy.stats import kendalltau


tickers = yf.Tickers('msft aapl')
df = tickers.history(period="5y")
aapl_returns = df['Close']['AAPL'].pct_change().dropna()
msft_returns = df['Close']['MSFT'].pct_change().dropna()

print("AAPL return distribution")
print(aapl_returns.describe())
print("MSFT return distribution")
print(msft_returns.describe())

def msft_return_probability(returns:float) -> float:
    """CDF of MSFT returns
    >>> round(msft_return_probability(-0.05),2)
    0.01
    """
    mean = 0.00115
    std = 0.01947
    zscore = (returns - mean)/std
    return norm.cdf(zscore)

def aapl_return_probability(returns:float) -> float:
    """CDF of AAPL returns
    >>> round(aapl_return_probability(-0.05),2)
    0.03
    """
    mean = 0.001252
    std = 0.020985
    zscore = (returns - mean)/std
    return norm.cdf(zscore)


def independent_copula(u, v):
    """Copula that assumes independence"""
    return u * v


import numpy as np
def gumbel_copula(u, v, alpha):
    """"""
    u = np.asarray(u)
    v = np.asarray(v)
    # compute copula
    copula = np.exp(-(((-np.log(u))**alpha + (-np.log(v))**alpha))**(1/alpha))
    return copula



def calculate_alpha(u,v):
    u=np.array(u)
    v=np.array(v)
    tau = kendalltau(u,v).correlation
    return 1/(1-tau)

