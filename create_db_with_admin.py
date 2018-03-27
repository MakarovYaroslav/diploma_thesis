import datetime
from server import app, db
from models.models import User


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(User(
            social_id="ad@min.com",
            email="ad@min.com",
            nickname="ADMIN",
            password="admin",
            admin=True,
            confirmed=True,
            confirmed_on=datetime.datetime.now())
        )
        db.session.commit()
