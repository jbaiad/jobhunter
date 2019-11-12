from jobhunter.scrapers.interfaces import AbstractWorkdayScraper


class MeredithScraper(AbstractWorkdayScraper):
    COMPANY_NAME = 'Meredith'
    ROOT_URL = r'https://meredith.wd5.myworkdayjobs.com/en-US/EXT'

__all__ = ['MeredithScraper']
