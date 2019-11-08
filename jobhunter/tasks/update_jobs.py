import datetime as dt
import logging

import airflow
from airflow import exceptions
from airflow import utils
from airflow.operators import python_operator

from jobhunter import scrapers
import jobhunter.daos.sql as daos


LOGGER = logging.getLogger()
DEFAULT_ARGS = {
    'owner': 'jobhunter',
    'depends_on_past': False,
    'email': ['josh@joshbaiad.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=2),
    'start_date': utils.timezone.datetime(2019, 10, 27, 22)
}


def automated_scraping_job(scraper, writer):
    new_jobs, updated_jobs, deleted_jobs = scraper.scrape(writer)
    if new_jobs.empty and updated_jobs.empty and deleted_jobs.empty:
        raise exceptions.AirflowSkipException

    if not new_jobs.empty:
        LOGGER.info('Found %d new jobs', len(new_jobs))

    if not updated_jobs.empty:
        LOGGER.info('Updated %d jobs', len(updated_jobs))

    if not deleted_jobs.empty:
        LOGGER.info('Deleted %d jobs', len(deleted_jobs))


with airflow.DAG('job_scrapers', default_args=DEFAULT_ARGS, schedule_interval=dt.timedelta(minutes=10)) as scraper_dag:
    python_operator.PythonOperator(
        task_id='conde_nast', 
        python_callable=lambda: automated_scraping_job(scrapers.CondeNastScraper, daos.JobWriter)
    )
    python_operator.PythonOperator(
        task_id='guardian', 
        python_callable=lambda: automated_scraping_job(scrapers.GuardianScraper, daos.JobWriter)
    )
    python_operator.PythonOperator(
        task_id='nyt',
        python_callable=lambda: automated_scraping_job(scrapers.NewYorkTimesScraper, daos.JobWriter)
    )
    python_operator.PythonOperator(
        task_id='hearst',
        python_callable=lambda: automated_scraping_job(scrapers.HearstScraper, daos.JobWriter)
    )
    python_operator.PythonOperator(
        task_id='meredith',
        python_callable=lambda: automated_scraping_job(scrapers.MeredithScraper, daos.JobWriter)
    )
