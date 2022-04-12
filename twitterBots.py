import tweepy as tp
import config
import time
import os
#import boto3


# twitter API credentials
consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
access_token = config.access_token
access_secret = config.access_secret
bearer_token = config.bearer_token


def create_url():
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    user_fields = "user.fields=created_at,description"
    # You can replace the ID given with the Tweet ID you wish to lookup Retweeting users for
    # You can find an ID by using the Tweet lookup endpoint
    id = "1418215506524348417"

    # tweet_fields =
    expansions_fields = "expansions.fields =referenced_tweets.id"
    # You can adjust ids to include a single Tweets.
    # Or you can add to up to 100 comma-separated IDs
    url = "https://api.twitter.com/2/tweets/{}/retweeted_by".format(id)
    return url, user_fields


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RetweetedByPython"
    return r


def printTweet(tweet):
    # can use name = displayname or screenName = @
    print(f" {tweet.user.screen_name}: {tweet.text}")


# login to twitter account api
auth = tp.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tp.API(auth)

# compare favorite count or
# need to determine if main tweet has been RATIO'd
# more replies or RTs than Likes
def isRatio(tweet):
    ratio = 0
    likes = tweet.favorite_count
    rts = tweet.retweet_count
    printTweet(tweet)

    if tweet.in_reply_to_status_id:
        orgID = tweet.in_reply_to_status_id_str
        orgTweet = api.get_status(orgID)
        print("replied to:")
        printTweet(orgTweet)
        orgLikes = orgTweet.favorite_count
        orgRts = orgTweet.retweet_count
    out = ""
    if orgLikes < likes:
        ratio += 1
        print("Enjoy this Ratio")
    if orgRts < rts:
        print("Retweet Mafia. Ratio Confirmed")
        ratio += 1
    if ratio < 1:
        print("Ratio DeConfirmed")
        print(f"{orgTweet.user.screen_name} WASN'T ratio'd by {tweet.user.screen_name}")
        out = f"{orgTweet.user.screen_name} WASN'T ratio'd by {tweet.user.screen_name} GG"
    else:
        print(f"{orgTweet.user.screen_name} WAS ratio'd by {tweet.user.screen_name} GG")
        out = f"{orgTweet.user.screen_name} WAS ratio'd by {tweet.user.screen_name} GG"
    return out


def printThread(thread):
    i = 0
    pass


def buildThread(tweet, thread):
    isQuote = tweet.is_quote_status
    last = tweet.id_str
    while isQuote:
        name = tweet.user.screen_name
        text = tweet.text
        thread.append(name)
        thread.append(text)
        printTweet(tweet)
        isQuote = tweet.is_quote_status
        if isQuote:
            last = tweet
            quoteID = tweet.quoted_status_id
            tweet = api.get_status(quoteID)
            firstQt = last.entities['urls'][0]['expanded_url']
    print(firstQt)
    api.update_status("@ Here's the first one by :" +last.user.name + " " + firstQt)


def retrieve_id(file):
    f_read = open(file, "r")
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def store_id(id, file):
    f_write = open(file, "w")
    f_write.write(str(id))
    f_write.close()

def ratioChecker(file):
    lastSeenID = retrieve_id(file)
    status = "nothing happened"
    mentions = api.mentions_timeline(lastSeenID, tweet_mode="extended", include_entities="true")
    for mention in mentions:
        if True:  # in mention.full_text:
            lastSeenID = mention.id
            #store_id(lastSeenID, file)
            ##api.update_status('@' + mention.user.screen_name + " test type beat ", mention.id)
            print("replied to @" + mention.user.screen_name)
            # check that they replied to something:
            # if "verify" in mention.full_text:
            if mention.in_reply_to_status_id is None:
                pass
            else:
                print(mention.in_reply_to_status_id_str)
                ##tweetLink = api.get_status(mention.in_reply_to_status_id_str)
                ##print(tweetLink)
                ## print(tweetLink.entities['urls'][0]['expanded_url'])
                convertTweet = api.get_status(mention.in_reply_to_status_id_str)
                status = isRatio(convertTweet)
                api.update_status('@' + mention.user.screen_name + " " + status, mention.id)

'''S3 Stuff 
def retrieve_id_s3(file):
    s3 = boto3.resource('s3')
    bucket_name = "elasticbeanstalk-us-east-1-974044218632"
    obj = s3.Object(bucket_name, file)
    body = obj.get()['Body'].read().strip()
    print(body)
    return body

def store_id_s3(lastSeenID):
    bucket_name = "elasticbeanstalk-us-east-1-974044218632"
    file_name = "id.txt"
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=file_name, Body=lastSeenID)

def ratioCheckerS3(file):
    lastSeenID = retrieve_id_s3(file)
    status = "nothing happened"
    mentions = api.mentions_timeline(lastSeenID, tweet_mode="extended", include_entities="true")
    for mention in mentions:
        if True:  # in mention.full_text:
            lastSeenID = mention.id
            store_id_s3(lastSeenID)
            print("checking for @" + mention.user.screen_name)
            # check that they replied to something:
            # if "verify" in mention.full_text:
            if mention.in_reply_to_status_id is None:
                pass
            else:

                ##tweetLink = api.get_status(mention.in_reply_to_status_id_str)
                ##print(tweetLink)
                ## print(tweetLink.entities['urls'][0]['expanded_url'])
                convertTweet = api.get_status(mention.in_reply_to_status_id_str)
                status = isRatio(convertTweet)
                api.update_status('@' + mention.user.screen_name + " " + status, mention.id)
                print("replied to  @" + mention.user.screen_name)
'''

def printThread(thread):
    print("Unraveling Nested Quotes...")
    for i in range(len(thread),2):
        print(f" {thread[i]}: {thread[i+1]}")






print("1st QT test")
tweet = api.get_status("1420587361386352643")
thread = []
buildThread(tweet, thread)
printThread(thread)

print("Nested Test!")
tweet = api.get_status("1381380508848951297")
thread = []
buildThread(tweet, thread)
printThread(thread)
tweet = api.get_status("1377614778991050769")
thread = []
buildThread(tweet, thread)
printThread(thread)

print("ratio test")


tweet = api.get_status("1420366444743831556")
#isRatio(tweet)

'''
def main(event, context):
    file = "id.txt"
    ratioChecker(file)
'''
