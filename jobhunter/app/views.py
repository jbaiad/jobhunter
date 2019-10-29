import flask_admin

import jobhunter.daos.sql.views as sql_views
import jobhunter.daos.sql.schemata as sql_schemata


class HiddenView(flask_admin.AdminIndexView):
    def is_visible(self):
        return False


JOB_VIEW = sql_views.JobView(sql_schemata.Job, name='Jobs', endpoint='jobs')
JOB_WATCH_VIEW = sql_views.JobWatchView(sql_schemata.Job, name='Watch List', endpoint='watchlist')
ADMIN_INDEX_VIEW = HiddenView(url='/', template='index.html')
