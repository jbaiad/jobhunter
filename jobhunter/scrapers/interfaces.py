import abc
import json

import bs4
import pandas as pd
import requests


class AbstractScraper(abc.ABC):
    def __new__(cls, *args, **kwargs):
        raise TypeError('Scrapers cannot be instantiated!')

    @abc.abstractclassmethod
    def scrape(cls, writer: any) -> pd.DataFrame:
        pass


class AbstractMetaWorkdayScraper(abc.ABCMeta):
    def __new__(mcs, name, bases, namespace):
        if not name.upper().startswith('ABSTRACT'):
            assert isinstance(namespace.get('ROOT_URL'), str)
        return super().__new__(mcs, name, bases, namespace)


class AbstractWorkdayScraper(AbstractScraper,
                             metaclass=AbstractMetaWorkdayScraper):
    SEARCH_ENDPOINT = 'fs/searchPagination/318c8bb6f553100021d223d9780d30be'

    @classmethod
    def scrape(cls, writer: any = None) -> pd.DataFrame:
        return pd.DataFrame([
            cls._get_job_info(f'{cls.ROOT_URL}/{endpoint}')
            for endpoint in cls._fetch_job_endpoints()
        ])

    @classmethod
    def _get_job_info(cls, job_url: str) -> dict:
        response = requests.get(job_url, headers={'Accept': 'application/json'})
        info = response.json()['structuredDataAttributes']['data']
        info = json.loads(info) 

        info['date_posted'] = pd.Timestamp(info['datePosted'])
        info['employment_type'] = info['employmentType'].replace('_', ' ')
        info['location'] = info['jobLocation']['address']['addressLocality']
        info['url'] = job_url

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

        while len(jobs) > 0:
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

