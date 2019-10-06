from datetime import datetime
import bs4
import flask_admin.contrib.sqla as sqla
import jinja2.utils

from jobhunter.daos.sql import common
from jobhunter.daos.sql import schemata


def job_get_detail_value(context, model, name):
    if name == 'description':
        soup = bs4.BeautifulSoup(model.description, 'html.parser')
        text_components = [bs4.BeautifulSoup(x, 'html.parser').text for x in soup.prettify().split('\n')]
        text_components = [text.strip() for text in text_components if text.strip()]
        return text_components 
    else:
        return super(sqla.ModelView, context).get_detail_value(context, model, name)



class ReadOnlyJobView(sqla.ModelView):
    details_template = 'details.html'
    column_list = ['title', 'company', 'location', 'employment_type', 'date_posted']
    column_searchable_list = ['title', 'company', 'location', 'employment_type', 'date_posted']
    column_filters = ['title', 'company', 'location', 'employment_type', 'date_posted']
    column_details_list = schemata.Job.__table__.columns
    can_create = False
    can_edit = False
    can_delete = False
    can_delete = False
    can_view_details = True
    get_detail_value = job_get_detail_value
    column_type_formatters = {datetime: lambda view, value: value.strftime('%Y-%m-%d')}
    column_type_formatters_detail = column_type_formatters
    column_details_list = ['title', 'company', 'employment_type', 'url', 'location', 'date_posted', 'description']

JobView = ReadOnlyJobView(schemata.Job, common.Session(), menu_class_name='Jobs')


__all__ = ['JobView']
