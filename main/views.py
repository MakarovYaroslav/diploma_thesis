from flask import Blueprint, render_template, request,\
    redirect, url_for, make_response
from flask_login import login_required
from save_reddit_twitter_data import RedditUser, TwitterUser
from models.models import RedditComments, TwitterComments
from main_functions import get_config, save_user_data_to_db,\
    user_have_enough_comments_count
from build_graph import draw_graph, draw_count_graph, draw_pie_graph
import plotly.tools as tls
from user.user_decorators import check_confirmed

main_blueprint = Blueprint('main', __name__,)
config = get_config()
topics = config['topic_modeling']['categories']


@main_blueprint.route('/', methods=['POST', 'GET'])
@login_required
@check_confirmed
def home():
    if request.method == 'POST':
        from server import get_last_timestamp
        social_network = request.form['options']
        username = request.form.get('username')
        if not username:
            return render_template('main.html', topics=topics, user_error=True)
        checked_topics = [topic for topic in topics if topic in request.form]
        if social_network == 'reddit':
            if not RedditUser.user_is_exist(username):
                return render_template('main.html', topics=topics,
                                       user_error=True, network=social_network)
            last_timestamp = get_last_timestamp(RedditComments, username)
        elif social_network == 'twitter':
            if not TwitterUser.user_is_exist(username):
                return render_template('main.html', topics=topics,
                                       user_error=True, network='twitter')
            last_timestamp = get_last_timestamp(TwitterComments, username)
        save_user_data_to_db(social_network, username, last_timestamp)
        response = make_response(redirect(url_for(
            'main.show_results', network=social_network,
            user=username, checked_topics=checked_topics)))
        return response
    else:
        return render_template('main.html', topics=topics,
                               user_error=False, network='reddit')


@main_blueprint.route('/<network>/<user>/')
@main_blueprint.route('/<network>/<user>/<checked_topics>')
@login_required
def show_results(network, user, checked_topics=topics):
    if user_have_enough_comments_count(user, network):
        graph_url = draw_pie_graph(network, user, checked_topics)
        graph = tls.get_embed(graph_url)
        graph2_url = draw_graph(network, user, checked_topics)
        graph2 = tls.get_embed(graph2_url)
        graph3_url = draw_count_graph(network, user)
        graph3 = tls.get_embed(graph3_url)
        return render_template('images.html', network=network, user=user,
                               graph=graph, graph2=graph2, graph3=graph3)
    else:
        return render_template('images.html', network=network, user=user,
                               graph="User does not have enough comments!")
