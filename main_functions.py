import socket
import pathos.multiprocessing as mp
import json


def get_config():
    with open("config.json", "r") as json_data_file:
        config = json.load(json_data_file)
    return config


def test_internet():
    try:
        socket.gethostbyaddr('www.yandex.ru')
    except socket.gaierror:
        return False
    return True


def user_have_enough_comments_count(user, network):
    from server import app
    from models.models import RedditComments, TwitterComments
    if network == 'reddit':
        with app.app_context():
            comments = RedditComments.query.filter_by(user=user).all()
    elif network == 'twitter':
        with app.app_context():
            comments = TwitterComments.query.filter_by(user=user).all()
    return True if len(comments) > 3 else False


def save_user_data_to_db(network, username, last_timestamp):
    from lda.theme import replace_posts_with_topics
    from save_reddit_twitter_data import RedditUser, TwitterUser
    if network == 'reddit':
        user = RedditUser(username)
    elif network == 'twitter':
        user = TwitterUser(username)
    user.get_user_data(last_timestamp)
    if len(user.data) == 0:
        print("PUSTO")
        return
    comments_and_posts = user.get_comments_and_posts()
    pool = mp.Pool(5)
    tone_dict = dict(zip(comments_and_posts, pool.map(user.get_tone_dict, comments_and_posts.values())))
    #tone_dict = user.get_tone_dict(comments_and_posts)
    topics_with_tone = replace_posts_with_topics(tone_dict)
    user.save_data_to_db(username, topics_with_tone, network)
    print("saved")
    return
