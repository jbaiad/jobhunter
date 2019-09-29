from jobhunter.scrapers.interfaces import AbstractWorkdayScraper


class NewYorkTimesScraper(AbstractWorkdayScraper):
    COMPANY_NAME = 'The New York Times'
    ROOT_URL = r'https://nytimes.wd5.myworkdayjobs.com/NYT'

__all__ = ['NewYorkTimesScraper']
