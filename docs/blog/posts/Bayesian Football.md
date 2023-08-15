---
date: 2023-08-15
categories:
  - Math
  - Python
  - Bayesian
---

# Bayesian Football Predictions

With the English Premier League starting up again, I've spent a lot of time thinking about football. Three years ago I wrote a Bayesian model to predict premiear league scorelines (you can still find my notebook on github) using Pymc3. Pymc3 and its computational engine, Theano, have stalled compared to the alternatives so it's time for an rewrite in numpyro and - since we only have one week of matches - a small tweak so that the computations converge quicker.

<!-- more -->

## Information contained in scorelines

There are two tricks to be aware of with predicitng winners in events. The first trick to be aware of is that what we measure is not necessarily what we want to know. Competitions are tricky, the better team won't always win. What we obesrve is a scoreline which is a reflection of the latent skill of each team relative to each other. The most accurate models will include a latent skill component, much like Elo for chess.

The second trick is that we should model the scores and not the result. A team that constantly wins 5-0 is very different to a team that consistently wins 2-1. A scoreline inherently contains more information than learning team A beat B. So if we want to use the most information available to us we should model the scoreline instead of the win/loss result. The same is true for modelling changes in price of stock data, the delta has more information than the sign of the delta. 

## Getting the data

First, we ingest the scorelines for each game so far and normalise the data so that each row contains one game result.

``` py title="Pulling data from wikipedia tables"
    season_df =pd.read_html("https://en.wikipedia.org/wiki/2023%E2%80%9324_Premier_League")[5]
    season_df.index = season_df.columns[1:]
    del(season_df['Home \ Away'])
```

``` py title="Normalising the data"
    #create dataframe where each row corresponds to one game
    season_df.index = season_df.columns
    rows = []
    for i in season_df.index:
        for c in season_df.columns:
            if i == c: continue
            score = season_df[c][i]
            if str(score) in ['nan', 'a']: continue
            score = [int(row) for row in str(score).split('–')]
            rows.append([i, c, score[0], score[1]])
    df = pd.DataFrame(rows, columns = ['home', 'away', 'home_score', 'away_score'])
```

```py title="Create index for each team"
    teams = season_df.columns
    teams = pd.DataFrame(teams, columns=['team'])
    teams['i'] = teams.index
    df = pd.merge(df, teams, left_on='home', right_on='team', how='left')
    df = df.rename(columns = {'i': 'i_home'})
    df = pd.merge(df, teams, left_on='away', right_on='team', how='left')
    df = df.rename(columns = {'i': 'i_away'})
    del(df['team_x'])
    del(df['team_y'])
```

```py title="Turn observations into lists"
    observed_home_goals = df.home_score.values
    observed_away_goals = df.away_score.values
    home_team = df.i_home.values
    away_team = df.i_away.values
    num_teams = len(df.i_home.unique())
```

## The Model

We now have all the data in the format we need, we can create the model and pass in our lists of observations.


``` py title="Using latent home advantage, attack and defense skill to predict scorelines"

import numpy as np
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist

def model(observed_home_goals, observed_away_goals, num_teams, home_team, away_team):
    def home_theta(intercept, home_advantage, atts, defs):
        return jnp.exp(intercept + home_advantage + atts[home_team] + defs[away_team])

    def away_theta(intercept, atts, defs):
        return jnp.exp(intercept + atts[away_team] + defs[home_team])

    tau_att = numpyro.sample('tau_att', dist.Gamma(concentration=0.1, rate=0.1))
    tau_def = numpyro.sample('tau_def', dist.Gamma(concentration=0.1, rate=0.1))
    tau_home = numpyro.sample('tau_home', dist.Gamma(concentration=0.1, rate=0.1))

    intercept = numpyro.sample('intercept', dist.Normal(0, 0.1))

    atts = numpyro.sample('atts', dist.Normal(0, tau_att).expand([num_teams]).to_event(1))
    defs = numpyro.sample('defs', dist.Normal(0, tau_def).expand([num_teams]).to_event(1))
    home_advantage = numpyro.sample('home_advantage', dist.Normal(0, tau_home))

    home_theta = home_theta(intercept, home_advantage, atts, defs)
    away_theta = away_theta(intercept, atts, defs)

    numpyro.sample('home_goals', dist.Poisson(home_theta), obs=observed_home_goals)
    numpyro.sample('away_goals', dist.Poisson(away_theta), obs=observed_away_goals)
```

Ignoring the technicalities of bayesian sampling and the sampling distributions lets run through the generative model.

\[
goals_{home} \sim \text{Poisson} (e^{\text{intercept} + \text{home} + \text{atts}[i] + \text{defs}[j]})
\] 


- Poisson distribution since each goal is a discrete event that has an equal chance of happening over each period of time.
- Exponential distribution since scorelines must be positive buy they can also cover large ranges (we've seen several 9-0 scorelines in the Premier League)
- Intercept corresponds to how many points the game is expected to have, think of the difference between football and basketball. 
- Teams generally play better at home and this is explicitly modelled in the `home` parameter. 
- Each team has its own inherent level of attacking and defending ability the number of goals is proportionate to how much better the attacking ability is compared to the oppositions defence.


## The training loop and usage

```py title="training loop"

rng_key = random.PRNGKey(0)
# Run inference
kernel = numpyro.infer.NUTS(model)
mcmc = numpyro.infer.MCMC(kernel, num_samples=1500, num_warmup=1000)
mcmc.run(rng_key, observed_home_goals, observed_away_goals, num_teams, home_team, away_team)

# Get samples
trace = mcmc.get_samples()


```


```py title="usage"
class Season:
    
    def __init__(self, season_dataframe, trace):
        """
        Args:
            season_dataframe: Pandas dataframe, row names are home team, column names are away team, cell is H–A score
            trace: Dictionary containing values for ["defs","atts","home", "intercept"]
        """
        self.data = season_dataframe
        
        self.trace = trace
        self.teams = pd.DataFrame(season_df.columns, columns=['team'])
        self.teams['i'] = self.teams.index


    def simulate_game(self, home, away, seed=False):
        """
        Args:
            home: 3 letter name of team e.g. "ARS"
            away: 3 letter name of team e.g. "ARS"
            seed: Integer, maximum possible value is len(self.trace)
        
        Returns:
            list: [int(home_team_goals), int(away_team_goals)]
        """
        if not seed:
            seed =  np.random.randint(len(self.trace))

        home_index = self.team_index(home)
        away_index = self.team_index(away)
        
        home_attack, away_attack = self.trace["atts"][seed][home_index], self.trace["atts"][seed][away_index]
        home_defence, away_defence = self.trace["defs"][seed][home_index], self.trace["defs"][seed][away_index]
        
        home_advantage = self.trace["home_advantage"][seed]
        intercept = self.trace["intercept"][seed]

        home_goals = np.random.poisson(np.exp(intercept + home_advantage  + home_attack + away_defence))
        away_goals = np.random.poisson(np.exp(intercept + away_attack + home_defence))
        return home_goals, away_goals

current_season = Season(season_df,trace)
current_season.simulate_game("MCI","TOT")

```

It's not much use unless you have an IDE to play around and tweak with the inputs. I'll be productionizing it soon and opening up an API endpoint, details in a later blog post.
