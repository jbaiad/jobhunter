import abc

import pandas as pd
import selenium.webdriver as selenium_web_drivers
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import selenium.webdriver.support.expected_conditions as selenium_conditions
from selenium.webdriver.support.ui import WebDriverWait

import jobhunter.utils.selenium as selenium_utils


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
            assert isinstance(namespace.get('DRIVER'), WebDriver)
        return super().__new__(mcs, name, bases, namespace)


class AbstractWorkdayScraper(AbstractScraper,
                             metaclass=AbstractMetaWorkdayScraper):
    @classmethod
    def _load_job_listings(cls):
        cls.DRIVER.get(cls.ROOT_URL)
        pause_driver = WebDriverWait(cls.DRIVER, 10)
        page_ready = selenium_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[aria-label="Search Results"]')
        )
        pause_driver.until(page_ready)
        selenium_utils.load_page_with_infinite_scroll(cls.DRIVER, 1.5)

        return cls.DRIVER.find_elements_by_class_name('WNYF.WLYF')

    @classmethod
    def _fetch_job_url(cls, job_listing):
        button = job_listing.find_element_by_css_selector('div[role="link"]')
        action_chain = selenium_web_drivers.ActionChains(cls.DRIVER)
        action_chain.context_click(button).perform()
        copy_url_button = cls.DRIVER.find_element_by_css_selector(
            'div[title="Copy URL"]'
        )

        return copy_url_button.get_attribute('data-clipboard-text')

    @classmethod
    def _fetch_job_info(cls, job_url):
        cls.DRIVER.get(job_url)
        pause_driver = WebDriverWait(cls.DRIVER, 10)
        page_ready = selenium_conditions.presence_of_element_located(
            (By.CLASS_NAME, 'WIOO')
        )
        pause_driver.until(page_ready)

        job_info_elements = [
            x.text for x in cls.DRIVER.find_elements_by_class_name('WMMO')
        ]
        job_info = {
            'title': job_info_elements[0],
            'location': '; '.join(sorted(job_info_elements[1:-6])),
            'description': job_info_elements[-6],
            'posted': job_info_elements[-5],
            'type': job_info_elements[-4],
            'url': job_url,
        }

        return job_info 

    @classmethod
    def scrape(cls, writer: any = None) -> pd.DataFrame:
        job_listings = cls._load_job_listings()
        job_urls = [cls._fetch_job_url(listing) for listing in job_listings]
        jobs = pd.DataFrame([cls._fetch_job_info(url) for url in job_urls])

        cls.DRIVER.quit()

        return jobs
