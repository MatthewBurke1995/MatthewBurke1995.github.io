---
date: 2023-01-28
categories:
  - Python
  - API
  - Typing
---

# ABC Radio

I wrote a [python library](https://abc-radio-wrapper.readthedocs.io/en/latest/index.html) for searching and parsing through the historical catalgoue of songs played on ABC (Australian Broadcasting Corporation) radio channels. This is especially timely since TripleJ will be releasing it's "Hottest 100" playlist for 2022 in a few days. 

<!-- more -->

I'm particularly interested in the TripleJ data due to it aligning with my music preferences. TripleJ tends to have a good mix of quality and breadth in its music selection and is arguably the reason that the Australian music industry as a whole has punched above its weight for so long. Which is why I'll be looking at the TripleJ data in particular.

Let's calculate which song and which artist had the most airtime throughout 2022. 

## Usage

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
        artists = [artist.name for artist in radio_play.song.artists]
        if len(artists) ==0: continue
        radio_play_list.append({"song":radio_play.song.title, "time":radio_play.played_time, "artist":artists[0]})

df = pd.DataFrame(radio_play_list)

#get the top 20 artists by playtime
print(
    df.groupby('artist').count().sort_values('time', ascending=False)[0:20]
)


                         song  time  artists
artist                                      
Art Vs Science            876   876      876
Spacey Jane               649   649      649
The Wombats               562   562      562
Ball Park Music           519   519      519
Vance Joy                 508   508      508
Flume                     485   485      485
Ocean Alley               468   468      468
beabadoobee               453   453      453
Wet Leg                   437   437      437
Maggie Rogers             431   431      431
G Flip                    426   426      426
Charli XCX                421   421      421
Kendrick Lamar            412   412      412
Eliza & The Delusionals   409   409      409
Foals                     407   407      407
Sycco                     406   406      406
Beddy Rays                395   395      395
merci, mercy              394   394      394
Lil Nas X                 389   389      389
Mura Masa                 382   382      382

```

So what could you use this data for? From here if you were to pick a particular time interval you could imagine integrating with the youtube or spotify API to create a playlist for a certain day or month. I think a similar method is already used to compile the hottest 100 playlists on youtube after each January, at least I'd hope people weren't adding each item by hand. You could also challenge my assumption that TripleJ has a wide variety of music. One method would be to calculate the Gini Impurity of the song catalouge where each artist is it's own category. You'd need to compare the results with other radio stations or other periods of time. 

And a convenience function for matching a song to a youtube video.

```py title="generate a youtube video from a song title"
import requests
import urllib.parse

def get_youtube_url(song_name: str, apikey: str) -> str:
    r= requests.get("https://youtube.googleapis.com/youtube/v3/search?q="+urllib.parse.quote_plus(song_name)+"&key="+apikey)
    video_id = r.json()['items'][0]['id']['videoId']
    return "https://www.youtube.com/watch?v="+video_id
```

