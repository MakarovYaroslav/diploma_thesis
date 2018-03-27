from flask_admin.contrib import sqla
from werkzeug.exceptions import HTTPException
from flask_login import current_user
from flask import Response


class ModelView(sqla.ModelView):
    can_view_details = True

    def is_accessible(self):
        forbidden_status_code = 403
        if not current_user.admin:
            raise HTTPException('', Response(
                "Only for admins",
                forbidden_status_code,
                {'WWW-Authenticate': 'Basic realm="Admin rights required"'}
            ))
        return True


class UserView(ModelView):
    column_searchable_list = ['nickname', 'email']
    column_filters = ['admin']
    column_default_sort = 'email'


class CommentView(ModelView):
    column_searchable_list = ['user']
    column_default_sort = 'user'
    column_labels = dict(result='Result id')


class ResultView(ModelView):
    column_searchable_list = ['id']
    column_default_sort = 'id'
    column_labels = dict(pos='Positive', neg='Negative')