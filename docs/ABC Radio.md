# ABC Radio

I wrote a [python library](https://abc-radio-wrapper.readthedocs.io/en/latest/index.html) for searching and parsing through the historical catalgoue of songs played on ABC (Australian Broadcasting Corporation) radio channels. This is especially timely since TripleJ will be releasing it's "Hottest 100" playlist for 2022 in a few days. 

I'll make a post later about some of the things I learned along the way but this post will mostly be about using the library and seeing what information we can extract from the data source.

TripleJ tends to have a good mix of quality and breadth in its music selection and is arguably the reason that the Australian music industry as a whole has punched above its weight for so long. Which is why i'll be looking at the TripleJ data in particular.

Let's calculate which song and which artist had the most airtime throughout 2022. 


``` sh title="install abc-radio-wrapper pypi package"
pip install abc-radio-wrapper
```

``` py
import pandas as pd
import abc_radio_wrapper

ABC = abc_radio_wrapper.ABCRadio()

startDate: datetime = datetime.fromisoformat("2022-01-01T00:00:00+00:00")
endDate: datetime = datetime.fromisoformat("2022-12-31T23:59:59+00:00")

radio_play_list = []
    
#search through 1 year period of triplej songs, set limit to 100 for faster results (default is 10)
for search_result in ABC.continuous_search(from_=startDate, to=endDate, station="triplej", limit=100):
    print(search_result.offset/search_result.total)
    for radio_play in search_result.radio_songs:        
        artist = [artist.name for artist in radio_play.song.artists][0]
        if len(artists) ==0: continue
        radio_play_list.append({"song":radio_play.song.title, "time":radio_play.played_time, "artist":artist})

df = pd.DataFrame(radio_play_list)

#get the top 20 artists by playtime
print(
    df.groupby('artist').count().sort_values('time', ascending=False)[0:20]
)
```

From here if you were to pick a particular time interval you could imagine integrating with the youtube or spotify API to create a playlist for a certain time period.


