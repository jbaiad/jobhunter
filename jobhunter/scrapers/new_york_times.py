from jobhunter.scrapers.interfaces import AbstractWorkdayScraper


class NewYorkTimesScraper(AbstractWorkdayScraper):
    ROOT_URL = r'https://nytimes.wd5.myworkdayjobs.com/NYT'

__all__ = ['NewYorkTimesScraper']

