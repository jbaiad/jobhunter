import time

from selenium.webdriver.remote.webdriver import WebDriver


def load_page_with_infinite_scroll(driver: WebDriver,
                                   time_between_scrolls: float = 1.0
                                   ) -> None:
    current_height = None
    new_height = get_window_height(driver)

    while current_height is None or current_height < new_height:
        current_height = new_height
        scroll_to_bottom(driver)
        time.sleep(time_between_scrolls)
        new_height = get_window_height(driver)


def scroll_to_bottom(driver: WebDriver) -> None:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')


def get_window_height(driver: WebDriver):
    return driver.execute_script('return document.body.scrollHeight;')
