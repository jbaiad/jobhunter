import datetime as dt

import airflow
from airflow import utils
from airflow.operators import python_operator

from jobhunter import scrapers
import jobhunter.daos.sql as daos


DEFAULT_ARGS = {
    'owner': 'jobhunter',
    'depends_on_past': False,
    'email': ['josh@joshbaiad.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=2),
    'start_date': utils.timezone.datetime(2019, 10, 20, 22)
}

with airflow.DAG('job_scrapers', default_args=DEFAULT_ARGS, schedule_interval=dt.timedelta(minutes=10)) as scraper_dag:
    python_operator.PythonOperator(
        task_id='conde_nast', 
        python_callable=lambda: scrapers.CondeNastScraper.scrape(daos.JobWriter)
    )
    python_operator.PythonOperator(
        task_id='guardian', 
        python_callable=lambda: scrapers.GuardianScraper.scrape(daos.JobWriter)
    )
    python_operator.PythonOperator(
        task_id='nyt',
        python_callable=lambda: scrapers.NewYorkTimesScraper.scrape(daos.JobWriter)
    )
