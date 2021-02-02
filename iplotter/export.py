import time
from selenium import webdriver
import os


class VirtualBrowser(object):
    """Helper class for converting html charts to png."""

    def __init__(self, driver=None):
        super(VirtualBrowser, self).__init__()

        if driver is None:
            _chrome_options = webdriver.ChromeOptions()
            _chrome_options.add_argument('--headless')
            _chrome_options.add_argument('--hide-scrollbars')
            _chrome_driver = webdriver.Chrome(options=_chrome_options)
            self.driver = _chrome_driver
        else:
            self.driver = driver

    def __enter__(self):
        return self

    def save_as_png(self, filename, width=960, height=480, render_time=1):
        """Open saved html file in an virtual browser and save a screen shot to PNG format."""
        self.driver.set_window_size(width, height)
        self.driver.get('file://{path}/{filename}'.format(
            path=os.getcwd(), filename=filename + ".html"))
        time.sleep(render_time)
        self.driver.save_screenshot(filename + ".png")

    def __exit__(self, type, value, traceback):
        self.driver.quit()
        return True

    def quit(self):
        """Shutdown virtual browser when finished."""
        self.driver.quit()
        return True
