import datetime
from server import app, db
from models.models import User
import os


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(User(
            social_id=os.getenv('ADMIN_EMAIL'),
            email=os.getenv('ADMIN_EMAIL'),
            nickname="ADMIN",
            password=os.getenv('ADMIN_PASSWORD'),
            admin=True,
            confirmed=True,
            confirmed_on=datetime.datetime.now())
        )
        db.session.commit()
