import abc
import json
from typing import Optional

import pandas as pd
import requests

from jobhunter.daos.interfaces import AbstractJobWriter
import jobhunter.utils.mixins as mixins


class AbstractScraper(abc.ABC, metaclass=mixins.NotInstantiableMeta):
    @abc.abstractclassmethod
    def scrape(cls, writer: Optional[AbstractJobWriter] = None) -> pd.DataFrame:
        pass


class AbstractMetaWorkdayScraper(mixins.NotInstantiableMeta):
    def __new__(mcs, name, bases, namespace, **kwargs):
        if not name.upper().startswith('ABSTRACT'):
            assert isinstance(namespace.get('ROOT_URL'), str)
            assert isinstance(namespace.get('COMPANY_NAME'), str)
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class AbstractWorkdayScraper(AbstractScraper,
                             metaclass=AbstractMetaWorkdayScraper):
    SEARCH_ENDPOINT = 'fs/searchPagination/318c8bb6f553100021d223d9780d30be'

    @classmethod
    def scrape(cls, writer: Optional[AbstractJobWriter] = None) -> pd.DataFrame:
        # TODO: This should be mulithreaded
        jobs = pd.DataFrame([
            cls._get_job_info(f'{cls.ROOT_URL}/{endpoint}')
            for endpoint in cls._fetch_job_endpoints()
        ])

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
    def _fetch_job_endpoints(cls) -> list:
        offset = 0
        job_endpoints = []
        jobs = cls._get_search_results(offset)

        while jobs:
            offset += len(jobs)
            job_endpoints.extend([
                '/'.join(j['title']['commandLink'].split('/')[3:]) for j in jobs
            ])
            jobs = cls._get_search_results(offset)

        return job_endpoints

    @classmethod
    def _get_search_results(cls, offset: int) -> dict:
        url = f'{cls.ROOT_URL}/{cls.SEARCH_ENDPOINT}/{offset}'
        response = requests.get(url).json()
        containing_json = response['body']['children'][0]['children'][0]

        return containing_json.get('listItems', [])
