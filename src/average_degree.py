#!/usr/bin/python

import json
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import itertools as it
import numpy as np
import collections
from datetime import datetime


def traverse_dict(dictionary, tags=None):
    """Recursively traverses tweet dictionary to retrieve hashtags
    """
    if tags is None:
        tags = []
    if isinstance(dictionary, list):
        if len(dictionary) > 0:
            if isinstance(dictionary[0], dict):
                traverse_dict(dictionary[0], tags)
    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            if key == 'hashtags':
                n_tags = len(dictionary[key])
                for i in xrange(n_tags):
                    tags.append(dictionary[key][i]['text'])
            else:
                traverse_dict(value, tags)
    return tags


def tweet_parse(tweet_data):
    """Parse out created date and list of hashtags from tweet
    """
    tweet_date = datetime.strptime(
        tweet_data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    tweet_hashtags = traverse_dict(tweet_data)
    point = collections.namedtuple('TweetRecord', ['created_at', 'hashtags'])
    p = point(created_at=tweet_date, hashtags=tweet_hashtags)
    return p


def tweet_time_diff(queue, point):
    """Compute time difference between first tweet and most recent tweet
    """
    first_tweet_date = getattr(queue.first(), 'created_at')
    next_tweet_date = getattr(point, 'created_at')
    diff = next_tweet_date - first_tweet_date
    return diff


def add_hashtag_edges(graph, hashtags):
    graph.add_nodes_from(hashtags)
    for pair in it.combinations(hashtags, 2):
        graph.add_edge(*pair)
    return graph


def remove_hashtag_edge(graph, queue):
    hashtags = getattr(queue.first(), 'hashtags')
    for pair in it.combinations(hashtags, 2):
        graph.remove_edge(*pair)
    queue.dequeue()
    return graph, queue

# Goodrich et al, Data Structures and Algorithms in Python (Section 7.1.2)


class LinkedQueue:
    """FIFO queue implementation using a singly linked list for storage."""

    #-------------------------- nested Node class --------------------------
    class _Node:
        """Lightweight, nonpublic class for storing a singly linked node."""
        __slots__ = '_element', '_next'    # streamline memory usage

        def __init__(self, element, next):  # initialize node's fields
            self._element = element         # reference to user's element
            self._next = next               # reference to next node
    #------------------------------- queue methods ---------------------------

    def __init__(self):
        """Create an empty queue."""
        self._head = None
        self._tail = None
        self._size = 0                      # number of queue elements

    def __len__(self):
        """Return the number of elements in the queue."""
        return self._size

    def is_empty(self):
        """Return True if the queue is empty."""
        return self._size == 0

    def first(self):
        """Return (but do not remove) the element at the front of the queue."""
        if self.is_empty():
            raise Empty('Queue is empty')
        return self._head._element          # front aligned with head of list

    def dequeue(self):
        """Remove and return the first element of the queue (i.e., FIFO).
        Raise Empty exception if the queue is empty.
        """
        if self.is_empty():
            raise Empty('Queue is empty')
        answer = self._head._element
        self._head = self._head._next
        self._size -= 1
        if self.is_empty():                 # special case as queue is empty
            self._tail = None               # removed head had been the tail
        return answer

    def enqueue(self, e):
        """Add an element to the back of queue."""
        newest = self._Node(e, None)        # node will be new tail node
        if self.is_empty():
            self._head = newest             # special case: previously empty
        else:
            self._tail._next = newest
        self._tail = newest                 # update reference to tail node
        self._size += 1


def mean_degree(G):
    """Compute average degree of graph
    """
    return np.mean(G.degree().values())


def main():
    queue = LinkedQueue()
    graph = nx.Graph()
    tweets_data_path = "tweets.txt"
    avg_deg = []
    with open(tweets_data_path, "r") as tweets_file:
        for line in tweets_file:
            tweet = json.loads(line)
            if "limit" in tweet.keys():
                continue
            else:
                temp_point = tweet_parse(tweet)
                queue.enqueue(temp_point)

                tweet_date_diff = tweet_time_diff(queue, temp_point)

                next_tweet_hashtags = getattr(temp_point, 'hashtags')

                if tweet_date_diff.days < 0:
                    # next tweet is out of order
                    continue
                else:
                    graph = add_hashtag_edges(graph, next_tweet_hashtags)
                    if tweet_date_diff.seconds <= 60:
                        # next tweet is at most 60 seconds newer than first
                        # tweet
                        avg_deg.append(mean_degree(graph))
                    else:
                        # next tweet is more than 60 seconds newer than
                        # first tweet
                        graph, queue = remove_hashtag_edge(graph, queue)
                        avg_deg.append(mean_degree(graph))
    print avg_deg
if __name__ == '__main__':
    main()
