import os
from PIL import ImageGrab, Image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def capture_html_to_image(url, output_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280x720")
    chrome_options.add_argument('--disable-ipc-flooding-protection')

    webdriver_path = '/Applications/chromedriver'
    driver = webdriver.Chrome(service=Service(webdriver_path), options=chrome_options)

    # print(url)
    driver.get(url)
    driver.save_screenshot(output_path)

    driver.quit()


if __name__ == '__main__':
    capture_html_to_image('file:///Users/lihao/Desktop/otree_with_LLM/iowa_gambling_task/test/fuck.html',
                          'output_image.png')
