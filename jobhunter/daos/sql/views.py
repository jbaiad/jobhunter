from datetime import datetime

import bs4
import flask
import flask_admin.contrib.sqla as sqla
import flask_login
from sqlalchemy import func

from jobhunter.daos.sql import common
from jobhunter.daos.sql import schemata


class SqlView(sqla.ModelView):
    session = common.Session()

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, self.session, *args, **kwargs)


class ReadOnlyView(sqla.ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True


class JobView(SqlView, ReadOnlyView):
    details_template = 'job_details.html'
    column_details_list = ['title', 'company', 'employment_type', 'url', 'location', 'date_posted', 'description']
    column_list = ['title', 'company', 'location', 'employment_type', 'date_posted']
    column_searchable_list = column_list
    column_filters = column_list
    column_type_formatters = {datetime: lambda view, value: value.strftime('%Y-%m-%d')}

    def get_detail_value(context, model, name):
        if name == 'description':
            soup = bs4.BeautifulSoup(model.description, 'html.parser')
            text_components = [bs4.BeautifulSoup(x, 'html.parser').text for x in soup.prettify().split('\n')]
            text_components = [text.strip() for text in text_components if text.strip()]
            return text_components
        else:
            return super().get_detail_value(context, model, name)


class JobWatchView(JobView):
    can_delete = True

    def get_query(self):
        return self.session.query(schemata.Job).join(schemata.JobWatch, schemata.Job.id == schemata.JobWatch.job_id)\
                           .filter(schemata.JobWatch.username == flask_login.current_user.username)

    def get_count_query(self):
        return self.session.query(func.count(schemata.JobWatch.job_id))\
                           .filter(schemata.JobWatch.username == flask_login.current_user.username)

    def delete_model(self, model: schemata.Job):
        try:
            self.on_model_delete(model)
            self.session.flush()
            self.session.query(schemata.JobWatch).filter(schemata.JobWatch.job_id == model.id).delete()
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flask.flash(f'Failed to delete record. {ex}')
            self.session.rollback()
            return False
        else:
            self.after_model_delete(model)

        return True

    def get_empty_list_message(self):
        return "You're not watching any jobs!"


__all__ = ['JobView', 'JobWatchView']
