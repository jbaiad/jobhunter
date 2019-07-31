from jobhunter.scrapers.interfaces import AbstractWorkdayScraper


class CondeNastScraper(AbstractWorkdayScraper):
    COMPANY_NAME = 'Condé Nast'
    ROOT_URL = r'https://condenast.wd5.myworkdayjobs.com/CondeCareers'

__all__ = ['CondeNastScraper']

