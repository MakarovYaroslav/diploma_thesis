from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from models.models import db, RedditComments, TwitterComments,\
    User, AnalysisResults
from sqlalchemy import func
from config import ProductionConfig
from flask_admin import Admin
from main.views import main_blueprint
from user.views import user_blueprint
from models.models_views import UserView, CommentView, ResultView

app = Flask(__name__)

app.config.from_object(ProductionConfig)

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
toolbar = DebugToolbarExtension(app)
db.init_app(app)

app.register_blueprint(main_blueprint)
app.register_blueprint(user_blueprint)


login_manager.login_view = "user.login"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500


def get_last_timestamp(table, username):
    with app.app_context():
        last_timestamp = db.session.query(func.max(table.timestamp))\
            .filter_by(user=username).first()[0]
    if last_timestamp is None:
        last_timestamp = 0.0
    return last_timestamp


admin = Admin(app, name='User Analysis', template_mode='bootstrap3')
admin.add_view(UserView(User, db.session, name='Users', endpoint="users"))
admin.add_view(CommentView(RedditComments, db.session,
                           name='Reddit Comments', endpoint="reddit"))
admin.add_view(CommentView(TwitterComments, db.session,
                           name='Twitter Comments', endpoint="twitter"))
admin.add_view(ResultView(AnalysisResults, db.session,
                          name='Analysis Results', endpoint="result"))


if __name__ == '__main__':
    app.run()
