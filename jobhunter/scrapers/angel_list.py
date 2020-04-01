import abc
import threading
from typing import Optional
import queue

import pandas as pd
import requests

from jobhunter.scrapers.interfaces import AbstractScraper
from jobhunter.daos.interfaces import AbstractJobWriter


class AbstractAngelListScraper(AbstractScraper):
    JOB_QUEUE = queue.Queue()
    NUM_THREADS = 8
    BASE = "https://www.angel.co/company"

    @classmethod
    def scrape(cls, writer: Optional[AbstractJobWriter] = None) -> pd.DataFrame:
        jobs = []
        threads = cls._start_threads(jobs)
        cls._populate_job_queue()
        cls._wait_for_threads_to_finish(threads)
        jobs = pd.DataFrame(jobs).drop_duplicates('url', keep='first')

        if writer is not None:
            new_jobs, updated_jobs = writer.write_jobs(jobs)
            deleted_jobs = writer.mark_inactive_jobs(jobs)
            return new_jobs, updated_jobs, deleted_jobs
        else:
            return jobs

    @classmethod
    def _get_job_info(cls, job_url: str) -> dict:
        response = requests.get(job_url, headers={'Accept': 'application/json'})
        info = response.json()['structuredDataAttributes']['data']
        info = json.loads(info)

        info['date_posted'] = pd.Timestamp(info['datePosted'])
        info['employment_type'] = info['employmentType'].replace('_', ' ')
        info['location'] = info['jobLocation']['address']['addressLocality']
        info['company'] = cls.COMPANY_NAME
        info['url'] = job_url
        info['is_active'] = True

        del info['@context']
        del info['@type']
        del info['hiringOrganization']
        del info['identifier']
        del info['datePosted']
        del info['employmentType']
        del info['jobLocation']

        return info

    @classmethod
    def _wait_for_threads_to_finish(cls, threads):
        cls.JOB_QUEUE.join()
        for _ in range(cls.NUM_THREADS):
            cls.JOB_QUEUE.put(None)
        for t in threads:
            t.join()

    @classmethod
    def _start_threads(cls, jobs):
        threads = []
        for _ in range(cls.NUM_THREADS):
            t = threading.Thread(target=cls._worker_loop, args=[jobs])
            threads.append(t)
            t.start()

        return threads

    @classmethod
    def _worker_loop(cls, jobs):
        while True:
            job_url = cls.JOB_QUEUE.get()
            if job_url is None:
                break
            else:
                # TODO: I'm pretty sure this list appending is NOT thread-safe
                jobs.append(cls._get_job_info(job_url))
                cls.JOB_QUEUE.task_done()


    @classmethod
    def _populate_job_queue(cls) -> list:
        offset = 0
        jobs = cls._get_search_results(offset)

        while jobs:
            for j in jobs:
                endpoint = '/'.join(j['title']['commandLink'].split('/')[3:])
                cls.JOB_QUEUE.put(f'{cls.ROOT_URL}/{endpoint}')

            offset += len(jobs)
            jobs = cls._get_search_results(offset)

    @classmethod
    def _get_search_results(cls, offset: int) -> dict:
        url = f'{cls.BASE}/{cls.COMPANY}/jobs?role={cls.ROLE}'
        response = requests.get(url).json()
        containing_json = response['body']['children'][0]['children'][0]

        return containing_json.get('listItems', [])
