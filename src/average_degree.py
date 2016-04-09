#!/usr/bin/python

import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def traverse_dict(dictionary,tags=None):
    """Recursively traverses tweet dictionary to retrieve hashtags
    """
    if tags is None:
        tags = []
    if isinstance(dictionary,list):
        if len(dictionary) > 0:
            if isinstance(dictionary[0],dict):
                traverse_dict(dictionary[0],tags)
    if isinstance(dictionary,dict):
        for key, value in dictionary.items():
            if key == 'hashtags':
                n_tags = len(dictionary[key])
                for i in xrange(n_tags):
                    tags.append(dictionary[key][i]['text'])
            else:
                traverse_dict(value,tags)
    return tags

if __name__ == '__main__':
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
    tweets['created_at'] = [datetime.strptime(tweet['created_at'], 
                    '%a %b %d %H:%M:%S +0000 %Y') for tweet in tweets_data]
    tweets['hashtags'] = [traverse_dict(tweet) for tweet in tweets_data]
    MaxTime = max(tweets['created_at'])
    one_min_tweets = tweets[MaxTime - tweets['created_at'] < '0 days 00:00:60']
