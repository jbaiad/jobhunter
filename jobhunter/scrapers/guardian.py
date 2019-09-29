import bs4
import pandas as pd
import requests

from jobhunter.scrapers.interfaces import AbstractScraper


ROOT_URL = r'https://workforus.theguardian.com'
INDEX = r'/index.php/search-jobs-and-apply'


class GuardianScraper(AbstractScraper):
    @classmethod
    def scrape(cls, writer: any = None) -> pd.DataFrame:
        jobs = []
        next_url = ROOT_URL + INDEX

        while next_url is not None:
            response = requests.get(next_url)
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            listings = soup.tbody.find_all('td')[::2]

            for job in listings:
                job_url = ROOT_URL + job.a.get('href')
                response = requests.get(job_url)
                job_soup = bs4.BeautifulSoup(response.content, 'html.parser')

                info = job_soup.find('aside', 'site-content__aside')
                info = {
                    k.get_text(): v.get_text()
                    for k, v in zip(*[iter(info.find_all('p'))] * 2)
                }
                info['title'] = job.get_text()
                info['url'] = job_url
                del info['Job Number']

                jobs.append(info)

            next_url = soup.find('span', 'ccm-page-right').a
            if next_url is not None:
                next_url = ROOT_URL + next_url.get('href')

        return pd.DataFrame(jobs)\
                 .rename(columns={'Business Area': 'area',
                                  'Employment Type': 'type',
                                  'Location': 'location'})

__all__ = ['GuardianScraper']
