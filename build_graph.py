import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
from models.models import RedditComments, TwitterComments
from sqlalchemy.orm import joinedload


def draw_graph(network, user, checked_topics):
    from server import app
    if network == 'reddit':
        with app.app_context():
            comments = RedditComments.query.filter_by(user=user)\
                .order_by(RedditComments.timestamp)\
                .options(joinedload(RedditComments.result)).all()
    elif network == 'twitter':
        with app.app_context():
            comments = TwitterComments.query.filter_by(user=user)\
                .order_by(TwitterComments.timestamp)\
                .options(joinedload(TwitterComments.result)).all()

    dates = [datetime.fromtimestamp(comment.timestamp) for comment in comments]
    ocean_attitude = [comment.result.pos * comment.result.politics
                      for comment in comments]
    program_attitude = [comment.result.pos * comment.result.program
                        for comment in comments]
    medicine_attitude = [comment.result.pos * comment.result.medicine
                         for comment in comments]

    ocean_visible = True if 'Politics' in checked_topics else 'legendonly'
    program_visible = True if 'Programming languages' \
                              in checked_topics else 'legendonly'
    medicine_visible = True if 'Medicine' in checked_topics else 'legendonly'
    politics_trace = go.Scatter(x=dates, y=ocean_attitude,
                                name='Politics', visible=ocean_visible)
    program_trace = go.Scatter(x=dates, y=program_attitude,
                               name='Programming languages',
                               visible=program_visible)
    medicine_trace = go.Scatter(x=dates, y=medicine_attitude,
                                name='Medicine', visible=medicine_visible)

    data = [politics_trace, program_trace, medicine_trace]
    layout = dict(
        title='Diagram of positive attitude to topics in '
              'time with time range slider and selectors',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label='1month', step='month',
                         stepmode='backward'),
                    dict(count=6, label='6months', step='month',
                         stepmode='backward'),
                    dict(count=1, label='YTD', step='year',
                         stepmode='todate'),
                    dict(count=1, label='1year', step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(),
            type='date'
        )
    )

    fig = dict(data=data, layout=layout)
    plot_url = py.plot(fig, filename='styling-names',
                       auto_open=False, showLink=False)
    return plot_url


def draw_count_graph(network, user):
    from server import app, db
    with app.app_context():
        if network == 'reddit':
            comments = pd.read_sql(
                RedditComments.query.filter_by(user=user)
                .options(joinedload(RedditComments.result)).statement,
                db.engine)
        elif network == 'twitter':
            comments = pd.read_sql(
                TwitterComments.query.filter_by(user=user)
                .options(joinedload(TwitterComments.result)).statement,
                db.engine)
    comments['timestamp'] = pd.to_datetime(comments['timestamp'], unit="s")
    max_date = comments['timestamp'].max()
    min_date = comments['timestamp'].min()
    date_delta = (max_date - min_date) / 10
    pos_comments = comments[comments['pos'] > comments['neg']]
    neg_comments = comments[comments['pos'] < comments['neg']]
    pos_count = pos_comments.groupby(
        pd.Grouper(key='timestamp', freq=date_delta))['pos'].count()
    neg_count = neg_comments.groupby(
        pd.Grouper(key='timestamp', freq=date_delta))['neg'].count()
    date_range = pd.date_range(start=min_date, end=max_date, freq=date_delta)

    trace1 = go.Bar(x=date_range, y=pos_count.values, name='POS comments',
                    marker=dict(color='#2ECC40', line=dict(color='#000000',
                                                           width=1.5),
                                )
                    )
    trace2 = go.Bar(x=date_range, y=neg_count.values, name='NEG comments',
                    marker=dict(color='#FF4136', line=dict(color='#000000',
                                                           width=1.5),
                                )
                    )

    data = [trace1, trace2]
    layout = go.Layout(
        title='Diagram of pos/neg message count in time',
        barmode='group'
    )

    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='grouped-bar',
                       auto_open=False, showLink=False)
    return plot_url


def calculate_pos_user_attitude(comments, topic):
    pos_attitude = 0.0
    for comment in comments:
        pos_attitude += comment.result.pos * getattr(comment.result, topic)
    neg_attitude = 0.0
    for comment in comments:
        neg_attitude += comment.result.neg * getattr(comment.result, topic)
    pos_user_attitude = (pos_attitude/(pos_attitude+neg_attitude))*100
    return pos_user_attitude


def draw_pie_graph(network, user, checked_topics):
    from server import app
    if network == 'reddit':
        with app.app_context():
            comments = RedditComments.query.filter_by(user=user)\
                .options(joinedload(RedditComments.result)).all()
    elif network == 'twitter':
        with app.app_context():
            comments = TwitterComments.query.filter_by(user=user)\
                .options(joinedload(TwitterComments.result)).all()
    politics_opacity = 1 if 'Politics' in checked_topics else 0.5
    program_opacity = 1 if 'Programming languages' in checked_topics else 0.5
    medicine_opacity = 1 if 'Medicine' in checked_topics else 0.5
    pos_politics_attitude = calculate_pos_user_attitude(comments, 'politics')
    pos_medicine_attitude = calculate_pos_user_attitude(comments, 'medicine')
    pos_program_attitude = calculate_pos_user_attitude(comments, 'program')
    pie_colors = ['#2ECC40', '#FF4136']
    pie_line = {'color': '#000000', 'width': 2}
    fig = {
        "data": [
            {
                "values": [pos_politics_attitude, 100-pos_politics_attitude],
                "labels": ["Positive", "Negative"],
                "domain": {"x": [0, .3]},
                "name": "Politics",
                "hoverinfo": "label+percent+name",
                "type": "pie",
                "hole": .4,
                "opacity": politics_opacity,
                "marker": {'colors': pie_colors, 'line': pie_line},
            },
            {
                "values": [pos_medicine_attitude, 100-pos_medicine_attitude],
                "labels": ["Positive", "Negative"],
                "domain": {"x": [.33, .63]},
                "name": "Medicine",
                "hoverinfo": "label+percent+name",
                "hole": .4,
                "type": "pie",
                "opacity": medicine_opacity,
                "marker": {'colors': pie_colors, 'line': pie_line},
            },
            {
                "values": [pos_program_attitude, 100 - pos_program_attitude],
                "labels": ["Positive", "Negative"],
                "domain": {"x": [.66, .96]},
                "name": "Programming languages",
                "hoverinfo": "label+percent+name",
                "hole": .4,
                "type": "pie",
                "opacity": program_opacity,
                "marker": {'colors': pie_colors, 'line': pie_line},
            }],
        "layout": {
            "title": "Pie chart of the user's attitude to the topics",
            "annotations": [
                {
                    "font": {"size": 20},
                    "showarrow": False,
                    "text": "Politics",
                    "x": 0.11,
                    "y": 1.05,
                },
                {
                    "font": {"size": 20},
                    "showarrow": False,
                    "text": "Medicine",
                    "x": 0.48,
                    "y": 1.05
                },
                {
                    "font": {"size": 20},
                    "showarrow": False,
                    "text": "Programming languages",
                    "x": 0.95,
                    "y": 1.05
                }
            ]
        }
    }
    plot_url = py.plot(fig, filename='donut', auto_open=False)
    return plot_url
