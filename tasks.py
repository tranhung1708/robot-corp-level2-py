import os
from pathlib import Path
import time
from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium

selenium = Selenium()


@task
def resover_data_collected():
    selenium.open_available_browser(url="https://github.com/robocorp/template-python-browser/blob/master/tasks.py")
    time.sleep(5)
    selenium.close_browser()