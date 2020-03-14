import os
import time
from pathlib import Path

import youtube_dl
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = 'https://vuemastery.com'
USERNAME = 'vypmycurzjcuwezzrz@awdrt.net'
PASSWORD = 'cHeVn4SfMoH6+s27sl8ezDHI+jY='


def login(driver):
    driver.get(f'{BASE_URL}')

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button.button.primary.-small'))
    ).click()

    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
    )
    email_field.click()
    email_field.send_keys(USERNAME)

    password_field = driver.find_element_by_css_selector('input[type="password"]')
    password_field.click()
    password_field.send_keys(PASSWORD)

    driver.find_element_by_css_selector('.form-actions > button[type="submit"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.navbar-secondary > button.button.primary.-small.appear'))
    )


def get_course_urls(driver):
    driver.get(f'{BASE_URL}/courses')
    time.sleep(5)
    courses = driver.find_elements_by_css_selector('span[mode="out-in"] > a.course-card')

    course_urls = [course.get_attribute('href') for course in courses]

    return course_urls


def crawl_course(driver, course_url):
    driver.get(course_url)
    time.sleep(5)
    lessons = driver.find_elements_by_css_selector('div.lessons-list-scroll > div.list-item')
    num_lessons = len(lessons)

    course_title = driver.find_element_by_css_selector('h2.title').text
    Path(course_title).mkdir(exist_ok=True)

    for i in range(num_lessons):
        driver.get(course_url)
        time.sleep(5)
        current_lesson = driver.find_elements_by_css_selector('div.lessons-list-scroll > div.list-item')[i]

        classes = current_lesson.get_attribute('class').split()
        if 'draft' in classes:
            continue
        
        if 'active' not in classes:
            current_lesson.click()
            time.sleep(5)

        download_lesson(driver, course_title)


def download_lesson(driver, course_title):
    lesson = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.lessons-list-scroll > div.list-item.active'))
    )
    video = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[itemprop="video"] > meta[itemprop="embedURL"]'))
    )
    url = video.get_attribute('content')

    lesson_title = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.list-item.active h4.list-item-title'))
    ).text.replace('/', '-')
    
    ydl_opts = {
        'outtmpl': f'{course_title}/{lesson_title}.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    driver = webdriver.Chrome()
    driver.set_window_size(1024, 600)
    driver.maximize_window()

    try:
        login(driver)
        for course_url in get_course_urls(driver):
            crawl_course(driver, course_url)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
