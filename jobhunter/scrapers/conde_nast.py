from jobhunter.scrapers.interfaces import AbstractWorkdayScraper


class CondeNastScraper(AbstractWorkdayScraper):
    ROOT_URL = r'https://condenast.wd5.myworkdayjobs.com/CondeCareers'
