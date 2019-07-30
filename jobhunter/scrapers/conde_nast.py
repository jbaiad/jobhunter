import selenium.webdriver as selenium_web_drivers

from jobhunter.scrapers.interfaces import AbstractWorkdayScraper


class CondeNastScraper(AbstractWorkdayScraper):
    _DRIVER_OPTIONS = selenium_web_drivers.ChromeOptions()
    _DRIVER_OPTIONS.add_argument('--headless')
    DRIVER = selenium_web_drivers.Chrome(chrome_options=_DRIVER_OPTIONS)
    ROOT_URL = r'https://condenast.wd5.myworkdayjobs.com/CondeCareers'
