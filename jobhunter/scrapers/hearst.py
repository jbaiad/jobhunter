import json
import threading
from typing import Optional
from urllib import request
import queue

import bs4
import pandas as pd

import jobhunter.daos.interfaces as daos_interfaces
import jobhunter.scrapers.interfaces as interfaces



class HearstScraper(interfaces.AbstractScraper):
    ROOT_URL = 'https://hearst.referrals.selectminds.com'
    JOBS_ENDPOINT = '/page/all-jobs-420'
    LOAD_JOBS_ENDPOINT = '/ajax/content/landingpage_job_results?JobSearch.id={search_id}&page_index={idx}&uid=0'
    JOB_QUEUE = queue.Queue()
    NUM_THREADS = 8


    @classmethod
    def scrape(cls, writer: Optional[daos_interfaces.AbstractJobWriter] = None) -> pd.DataFrame:
        # For some reason the requests library doesn't work here. Refer to: https://github.com/psf/requests/issues/5003
        req = request.Request(cls.ROOT_URL + cls.JOBS_ENDPOINT)
        resp = request.urlopen(req)
        soup = bs4.BeautifulSoup(resp.read(), 'html.parser')
        headers = {
            'tss-token': soup.find(id='tsstoken')['value'],
            'Cookie': ' '.join(val.split()[0] for name, val in resp.getheaders() if name == 'Set-Cookie'),
        }

        jobs = []
        threads = cls._start_threads(jobs)
        cls._populate_queue(soup.find(id='jSearchId')['value'], headers)
        cls._wait_for_threads_to_finish(threads)
        jobs = pd.DataFrame(jobs)

        if writer is not None:
            writer.write_jobs(jobs)
            writer.mark_inactive_jobs(jobs)

        return jobs

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
    def _populate_queue(cls, search_id, headers):
        page_index = 0
        while True:
            try:
                endpoint = cls.LOAD_JOBS_ENDPOINT.format(search_id=search_id, idx=page_index)
                req = request.Request(cls.ROOT_URL + endpoint, method='POST', headers=headers)
                resp = request.urlopen(req)
                content = json.loads(resp.read())
                soup = bs4.BeautifulSoup(content['Result'], 'html.parser')
                for item in soup.find_all(class_='job_link'):
                    cls.JOB_QUEUE.put(item['href'])
                page_index += 1
            except request.HTTPError:
                break
        
    @classmethod
    def _worker_loop(cls, jobs):
        while True:
            job_url = cls.JOB_QUEUE.get()
            if job_url is None:
                break
            else:
                req = request.Request(job_url)
                resp = request.urlopen(req)
                content = resp.read()
                soup = bs4.BeautifulSoup(content, 'html.parser')
                jobs.append({
                    'title': soup.find('h1', class_='title').text.strip(),
                    'location': soup.find('h4', class_='primary_location').span.next_sibling.strip(),
                    'description': str(soup.find('div', class_='job_description')),
                    'company': soup.find('dl', class_='field_company').dd.text.strip(),
                    'industry': soup.find('dl', class_='field_category').dd.text.strip(),
                    'date_posted': None,
                    'employment_type': None,
                    'url': job_url,
                    'is_active': True
                })
                cls.JOB_QUEUE.task_done()


__all__ = ['HearstScraper']
