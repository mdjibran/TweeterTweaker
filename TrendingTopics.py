'''

Written by : Mohammed Jibran
Date : 21st Jan 2017
Name : StreamTweeter.py
Description : Below codes connects to Twitter via its API and get Straming Tweets to the provided topic

'''

# Get all the imports
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import tweepy
import json
import SettingsFile
import sys
import re


# Provide API values
consumer_key = SettingsFile.consumer_key
consumer_secret = SettingsFile.consumer_secret
access_token = SettingsFile.access_token
access_token_secret = SettingsFile.access_token_secret

# Connect to API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Listener that prints received tweets to console
class StdOutListener(StreamListener):
# This function is executed if data/tweet is received
    def on_data(self, data):
        sentiment = 0
        location = None
        keyWrd = "UNKNOWN"
        lon = None
        lat = None
        dict_data = json.loads(data)

        with open('Topics.txt', 'r') as f:
            lst = f.readlines()

        lst = [element.replace("\n", "") for element in lst]

        try:
            try:
                text = str(dict_data["text"]).encode('ascii', 'ignore')
            except:
                text = str(dict_data["text"]).encode('unicode_escape')

            text = re.sub('[^\w\d\s]+', ' ', text)

            if text is not None:
                for word in text.split():
                    if word.lower() in lst:
                        keyWrd = str(word).upper()
                if keyWrd == "UNKNOWN":
                    textData = re.sub('[^\w\d\s]+', ' ', data)
                    textData = textData.replace("\n","")
                    for word in textData.split():
                        if word.lower() in lst:
                            keyWrd = str(word).upper()
                if keyWrd == "UNKNOWN":
                    print ""
                text = str(text)
            twText = re.sub('[^\w\d\s]+', ' ', text)
            twText = twText.replace("\n", "")
            text = TextBlob(text)
            text = float(text.sentiment.polarity)

            if text > 0:
                sentiment = 1  # Positive Tweet
            elif text < 0:
                sentiment = -1  # Negative Tweet
            else:
                sentiment = 0 # Neutral Tweet

            source = str(dict_data["source"])
            source = source.partition('>')[-1].rpartition('<')[0]
            source = source.replace('Twitter','').replace('for','').replace(' ','').replace(';','/')

            if dict_data['coordinates']:
                lon = float(dict_data['coordinates']['coordinates'][0])
                lat = float(dict_data['coordinates']['coordinates'][1])
            elif 'place' in dict_data.keys() and dict_data['place']:
                lon = float(dict_data['place']['bounding_box']['coordinates'][0][0][0])
                lat = float(dict_data['place']['bounding_box']['coordinates'][0][0][1])
            elif 'retweeted_status' in dict_data.keys() and 'place' in dict_data['retweeted_status'].keys() and \
                    dict_data['retweeted_status']['place']:
                lon = float(dict_data['retweeted_status']['place']['bounding_box']['coordinates'][0][0][0])
                lat = float(dict_data['retweeted_status']['place']['bounding_box']['coordinates'][0][0][1])
            elif 'quoted_status' in dict_data.keys() and 'place' in dict_data['quoted_status'].keys() and \
                    dict_data['quoted_status']['place']:
                lon = float(dict_data['quoted_status']['place']['bounding_box']['coordinates'][0][0][0])
                lat = float(dict_data['quoted_status']['place']['bounding_box']['coordinates'][0][0][1])

            cdate = str(dict_data["created_at"])
            cdate = cdate.replace(';','/')

            location = None
            location = str(dict_data["user"]["location"])
            location = location.replace(';','/')
            tweet = str(keyWrd)+"|"+str(sentiment)+"|"+source+"|"+cdate+"|"+str(lon)+"|"+str(lat)+"|"+location+"|"+str(twText)+"\n"
            print "\n"+tweet
            with open("tweet.csv","a") as filew:
                filew.write(tweet)

        except Exception as e:
            print ""
        return True

    def on_error(self, status):
        print ""


if __name__ == '__main__':
    with open('Topics.txt', 'r') as f:
        lst = f.readlines()
    for item in lst :
        lst = [element.replace("\n","") for element in lst]
    #print lst

    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(track=lst)
    #stream.filter(locations="Canada")
