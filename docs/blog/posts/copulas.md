---
date: 2023-01-16
categories:
  - Math
---


# Copulas

Copulas are a way of estimating the multivariate distribution of independently modelled univariate distributions. They are a useful way of modelling the joint distribution of a set of random variables.

<!-- more -->

!!! warning

    Gaussian copulas were used widely in risk modelling during the GFC, the joint probability estimates will only be as good as your marginal probability modelling and appropriateness of the copula.


Going through an example might be useful. Imagine we have $1000 in AAPL stock and $1000 in MSFT stock. What is the chance that they both drop by 5% on the same day?

We could approach this question using a multivariate bayesian approach, model a hidden factor that affects both the prices of MSFT and AAPL, estimate the most likely parameters, sample from the posterior and record the proportion of times that we see a greater than 5% drop in each of the share prices. That can be a lot of work especially if we have already independently modelled the underlying assets.

## Build marginal distributions for the process you want to model

First let's work out the distributions of each asset independently. We'll be using the normal distribution as that is conceptually the easiest to work through, although the copula approach works for any underlying distributions. Assuming the returns follow a normal distribution (not fat tailed enough, I know) then we will have to estimate the mean and standard deviation from the sample.

\[
  x \sim \mathcal{n}(\mu,\,\sigma^{2})\,.
\] 


``` py title="Get the paramters for AAPL and MSFT returns distribution"
import yfinance as yf

tickers = yf.Tickers('msft aapl')
df = tickers.history(period="5y")
aapl_returns = df['Close']['AAPL'].pct_change().dropna()
msft_returns = df['Close']['MSFT'].pct_change().dropna()

print("AAPL return distribution")
print(aapl_returns.describe())
# AAPL return distribution
count    1258.000000
mean        0.001252
std         0.020985
min        -0.128647
25%        -0.008779
50%         0.001140
75%         0.012366
max         0.119808

print("MSFT return distribution")
print(msft_returns.describe())
count    1258.000000
mean        0.001149
std         0.019466
min        -0.147390
25%        -0.007827
50%         0.001289
75%         0.010938
max         0.142169
```

``` py title="make CDF for AAPL and MSFT returns" 
from scipy.stats import norm

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

```

## Pick a copula to calculate the joint distribution

We now have our underlying marginal distributions for each set of assets. Now we have to somehow combine them to form a joint distribution. The easiest way would be to assume that they are independent of each other. We could write an independent copula like this:

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
    When we read this function for the inputs correlated_copula(0.8,0.3) we should say "What is the chance of at least the 80th percentile of returns and at least the 30th percentile of returns?" If they are completely correlated then when one distribution returns the 80th percentile then the other distribution must also return at least the 80th percentile.
    ``` py 
        correlated_copula(0.8,0.3) == correlated_copula(0.8,0.8) 
    ```


Which gives us a much more realistic 3% chance, this is problematic in that we cannot prove that they are completely correlated and likely overestimates the risk. Going by this metric we could reduce our risk by dropping AAPL entirely and putting all our money in MSFT, this is the opposite of the mantra that "Diversification is the only free lunch.”

Let's make the assumption that they are inversely correlated, which gives us the following copula:

``` py
def inversely_correlated_copula(u,v):
    return max(u+v-1,0)
```

Accordingly if AAPL were truly uncorrelated with MSFT then there would be no days in which they both lose money and the joint probability of a 5% loss on both assets would be 0.

An alternative copula that we can use is the Gumbel copula which takes into account the correlation of the underlying marginal distributions. You can see the code below.

``` py
import numpy as np
def gumbel_copula(u, v, alpha):
    u = np.asarray(u)
    v = np.asarray(v)
    # compute copula
    copula = np.exp(-(((-np.log(u))**alpha + (-np.log(v))**alpha))**(1/alpha))
    return copula
```

For the Gumbel copula, when alpha is equal to one then the copula behaves the same as the independent copula. When alpha approaches infinity it behaves like the inversely correlated copula. So you can guess that alpha is related to the correlation of the series u and v.

To calculate alpha we first calculate the Kendall tau value of the two series. Kendall's tau can be described as a type of rank correlation coefficient. When making the calculation we use the probability values and not the values of the underlying returns i.e.

``` py
from scipy.stats import kendalltau

def calculate_alpha(u,v):
    u=np.array(u)
    v=np.array(v)
    tau = kendalltau(u,v).correlation
    return 1/(1-tau)
```


##Apply the copula to find the joint probability of two events
Let's create the probability series from the returns series and calculate our alpha value for MSFT and AAPL:

``` py title="calculate the joint probabilites for different copula"
alpha = calculate_alpha(aapl_returns.apply(lambda x: aapl_return_probability(x)),
                        msft_returns.apply(lambda x: msft_return_probability(x)))
                        
print(alpha) 
#2.2015...  


print(aapl_return_probability(-0.05)*msft_return_probability(-0.05))
# 0.0002..

print(gumbel_copula(aapl_return_probability(-0.05),msft_return_probability(-0.05))
# 0.0032
```


Even with our poor modeling of the marginal distributions the Gumbel copula is able to give us a much better estimation of the probability that both companies would drop 5% in a single day. Looking at the history over the last 5 years there have been 7 out of 1258 trading days in which both companies dropped 5% (0.0056 by proportion).


## Graphing the result

=== "independent copula graph"

    ``` py
    X,Y = np.mgrid[0:0.5:0.05, 0:0.5:0.05]
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X, Y, independent_copula(X,Y), c= 'red')
    plt.savefig("independent_copula.png")
    ```
    ![Independent Copula](/images/independent_copula.png){align=right }
 

=== "gumbel copula graph"
    ``` py
    X,Y = np.mgrid[0:0.5:0.05, 0:0.5:0.05]
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X, Y, gumbel_copula(X,Y,alpha), c= 'red')
    plt.savefig("gumbel_copula.png")
    ```
    ![Gumbel Copula](/images/gumbel_copula.png){align=right }

The graph is steeper for the Gumbel copula, which means the joint probability is higher for two unlikely but correlated events.



## Wrap up

Copula's are used in risk management for their flexibility in combining a wide range of probability models into a joint probability. Even with a simple marginal probability model the combined copula was reasonably accurate in estimating the joint distribution for correlated assets. You could use copulas for predicting the network load on two related software services or for calculating the risk of correlated assets that are modelled differently.

Below I have included a chart comparing the probability estimates for the Gumbel and Independent copulas for when `#!python u=v`. Once again the Gumbel copula estimates a higher probability of two correlated but low probability events.


<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.0/echarts.min.js"></script>

<div id="chart" style="width: 600px;height:400px;"></div>
<script type="text/javascript">
  // Initialize the echarts instance based on the prepared dom
  var myChart = echarts.init(document.getElementById('chart'));

  // Specify the configuration items and data for the chart

option = {
  title:{
    text: 'Gumbel and Independent copula',
    subtext: 'y=Copula(x,x)'
    
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} {b},{c} '
  },
  xAxis: {
    data: [0.   , 0.025, 0.05 , 0.075, 0.1  , 0.125, 0.15 , 0.175, 0.2  ,
       0.225, 0.25 , 0.275, 0.3  , 0.325, 0.35 , 0.375, 0.4  , 0.425,
       0.45 , 0.475],
    name:''
  },
  yAxis: {name: ''},
  series: [
    {
      data: [0.      , 0.000625, 0.0025  , 0.005625, 0.01    , 0.015625,
       0.0225  , 0.030625, 0.04    , 0.050625, 0.0625  , 0.075625,
       0.09    , 0.105625, 0.1225  , 0.140625, 0.16    , 0.180625,
       0.2025  , 0.225625],
      type: 'line',
      stack: 'x',
      areaStyle: {},
      name:'Independent'
    },
    {
      data: [0.        , 0.0065148 , 0.01677541, 0.02917153, 0.04319615,
       0.0585712 , 0.07511579, 0.09270087, 0.11122874, 0.13062234,
       0.150819  , 0.17176657, 0.19342082, 0.21574365, 0.23870185,
       0.26226616, 0.28641054, 0.31111165, 0.33634844, 0.36210178],
      type: 'line',
      stack: 'x',
      areaStyle: {},
      name:'Gumbel'
    }
  ]
};

  myChart.setOption(option);
</script>


