#!/usr/bin/python

import json
import pandas as pd
import matplotlib.pyplot as plt

tweets_data_path = "tweets.txt"
tweets_data = []
tweets_file = open(tweets_data_path,"r")
for line in tweets_file:
    try:
        tweet = json.loads(line)
        tweets_data.append(tweet)
    except:
        continue
tweets_file.close()

tweets = pd.DataFrame()
tweets['created_at'] = [tweet['created_at'] for tweet in tweets_data]
