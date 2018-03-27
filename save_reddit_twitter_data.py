import requests
import sentiment.sentiment_mod as s
from lda.createuci import Text
import os
from models.models import RedditComments, TwitterComments, AnalysisResults
from datetime import datetime
import praw
import tweepy
import asyncio


class User:
    def __init__(self, user_id):
        self.user_id = user_id

    @staticmethod
    def save_data_to_db(username, user_data, network):
        from server import app, db
        if network == 'twitter':
            table = TwitterComments
        elif network == 'reddit':
            table = RedditComments
        with app.app_context():
            for topics, tone_with_time in user_data:
                medicine = politics = program = 0.0
                for topic, probability in topics:
                    if topic == 'Medicine':
                        medicine = probability
                    elif topic == 'Politics':
                        politics = probability
                    else:
                        program = probability
                pos = tone_with_time['pos']
                neg = tone_with_time['neg']
                timestamp = tone_with_time['timestamp']
                result = AnalysisResults(pos=pos, neg=neg, medicine=medicine, politics=politics, program=program)
                new_line = table(user=username, timestamp=timestamp, result=result)
                db.session.add(new_line)
            db.session.commit()

    @staticmethod
    def get_tone_dict(post_and_comment):
        confidence_dict = {}
        comment, timestamp = post_and_comment
        confidence_dict['timestamp'] = timestamp
        tone = s.sentiment(comment)
        tonality, probability = tone
        if tonality == 'pos':
            confidence_dict['pos'] = probability
            confidence_dict['neg'] = 1 - probability
        else:
            confidence_dict['neg'] = probability
            confidence_dict['pos'] = 1 - probability
        return confidence_dict


class RedditUser(User):
    def __init__(self, user_id):
        super().__init__(user_id)

    @staticmethod
    def user_is_exist(username):
        r = requests.get(
            'http://www.reddit.com/user/%s' % username, headers={'User-agent': 'request bot 0.1'})
        return True if r.status_code == 200 else False

    def get_user_data(self, last_timestamp):
        reddit = praw.Reddit(user_agent=os.getenv('REDDIT_USER_AGENT'),
                             client_id=os.getenv('REDDIT_CLIENT_ID'),
                             client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                             username=os.getenv('REDDIT_USERNAME'),
                             password=os.getenv('REDDIT_PASSWORD'))
        reddit_user = reddit.redditor(self.user_id)
        comments = reddit_user.comments.new(limit=None)
        new_comments = []
        for comment in comments:
            if comment.created <= last_timestamp:
                break
            if comment.is_root:
                new_comments.append(comment)
        print("Получено %d новых комментов" % len(new_comments))
        self.data = new_comments
        return

    def get_comments_and_posts(self):
        comments_and_posts = {}
        if self.data is not None:
            for record in self.data:
                clean_text = Text()
                post = clean_text.text_cleaning(record.link_title)
                comment = clean_text.text_cleaning(record.body)
                timestamp = record.created
                comments_and_posts[post] = (comment, timestamp)
        return comments_and_posts


class TwitterUser(User):
    def __init__(self, user_id):
        super().__init__(user_id)

    @staticmethod
    def user_is_exist(username):
        r = requests.get(
            'https://twitter.com/%s' % username, headers={'User-agent': 'request bot 0.1'})
        if r.status_code == 200:
            return True
        else:
            return False

    @asyncio.coroutine
    def check_tweet(self, tweet):
        loop = asyncio.get_event_loop()
        future1 = loop.run_in_executor(None, self.get_status_text, tweet.in_reply_to_status_id)
        status_text = yield from future1
        if not status_text:
            return
        else:
            return [status_text, tweet.created_at.timestamp(), tweet.text]

    def get_status_text(self, status_code):
        try:
            status_text = self.api.get_status(status_code).text
        except tweepy.error.TweepError:
            status_text = ''
        return status_text

    def get_user_data(self, last_timestamp):
        consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
        consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
        access_key = os.getenv('TWITTER_ACCESS_KEY')
        access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        self.api = api
        alltweets = []
        new_tweets = api.user_timeline(screen_name=self.user_id, count=200)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        while len(new_tweets) > 0:
            print(alltweets[-1].created_at, datetime.fromtimestamp(last_timestamp))
            if alltweets[-1].created_at <= datetime.fromtimestamp(last_timestamp):
                break
            new_tweets = api.user_timeline(screen_name=self.user_id, count=200, max_id=oldest)
            alltweets.extend(new_tweets)
            oldest = alltweets[-1].id - 1
        print("Получено %d новых комментов" % len(alltweets))
        tweets = [tweet for tweet in alltweets if tweet.created_at > datetime.fromtimestamp(last_timestamp)]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [asyncio.async(self.check_tweet(tweet)) for tweet in tweets]
        if tasks:
            done, _ = loop.run_until_complete(asyncio.wait(tasks))
            comments = [result.result() for result in done if result.result() is not None]
        else:
            comments = []
        loop.close()
        print("Из них подошли %d" % len(comments))
        self.data = comments
        return

    def get_comments_and_posts(self):
        comments_and_posts = {}
        if self.data is not None:
            for record_post, record_timestamp, record_comment in self.data:
                clean_text = Text()
                post = clean_text.text_cleaning(record_post)
                comment = clean_text.text_cleaning(record_comment)
                timestamp = record_timestamp
                comments_and_posts[post] = (comment, timestamp)
        return comments_and_posts
