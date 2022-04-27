import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

driver = webdriver.Chrome(
    executable_path="/Users/justinbaytosh/Netflix/FinalProject/env/chromedriver")
driver.get(
    "https://store.steampowered.com/search/?sort_by=Reviews_DESC&maxprice=free&genre=Free+to+Play")
body = driver.find_element_by_tag_name("body")

total_games = 0
while total_games < 3779:
    body.send_keys(Keys.PAGE_DOWN)
    total_games = len(
        driver.find_elements_by_css_selector('a.search_result_row'))

page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")
results = soup.find(id="search_resultsRows")
game_elements = results.find_all(
    "a", class_="search_result_row")

games = []
for game_element in game_elements:
    title = game_element.find("span", class_="title").text
    release_date = game_element.find("div", class_="search_released").text
    link = game_element.get("href")
    games.append({"title": title, "release_date": release_date,
                  "price": 0, "link": link})

for game in games:
    URL = game['link']
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="responsive_page_template_content")

    reviews_summary_row = ''
    try:
        reviews_summary_row = results.find_all(
            "div", class_="user_reviews_summary_row")[-1] if results.find_all(
            "div", class_="user_reviews_summary_row") is not None else None
    except AttributeError:
        reviews_summary_row = None

    gameplay_elements = ''
    try:
        gameplay_elements = results.find(
            id="category_block").find_all("div", class_="label") if results.find(
            id="category_block") is not None else None
    except AttributeError:
        gameplay_elements = None

    genre_elements = ''
    try:
        genre_elements = results.find(id="genresAndManufacturer").find_all(
            "a") if results.find(id="genresAndManufacturer") is not None else None
    except AttributeError:
        genre_elements = None

    minrequirements_elements = ''
    try:
        minrequirements_elements = results.find(
            "div", class_="game_area_sys_req_leftCol").find_all('li') if results.find(
            "div", class_="game_area_sys_req_leftCol") is not None else None
    except AttributeError:
        minrequirements_elements = None

    overall_review = 'N/A'
    try:
        overall_review = reviews_summary_row.find(
            "span", class_="game_review_summary").text
    except AttributeError:
        overall_review = None

    percent_positive_reviews = 'N/A'
    try:
        percent_positive_reviews = results.find(
            "span", class_="nonresponsive_hidden").text.split('%')[0].strip().replace('- ', '')
    except AttributeError:
        percent_positive_reviews = None

    num_reviews = 'N/A'
    try:
        num_reviews = results.find_all(
            "span", class_="nonresponsive_hidden")[-1].text.strip().split('the ')[-1].split(' user')[0].replace(',', '')
    except AttributeError:
        num_reviews = None
    except IndexError:
        num_reviews = None

    tags = []
    if gameplay_elements:
        for gameplay_element in gameplay_elements:
            tags.append(gameplay_element.text.strip())

    genres = []
    if genre_elements:
        for genre_element in genre_elements:
            genres.append(genre_element.text.strip())
        del genres[-3:]

    minrequirements = []
    if minrequirements_elements:
        for minrequirements_element in minrequirements_elements:
            minrequirements.append(minrequirements_element.text.strip())

    game['overall_review'] = overall_review
    game['percent_positive_reviews'] = percent_positive_reviews
    game['num_reviews'] = num_reviews
    game['tags'] = tags
    game['genres'] = genres
    game['minrequirements'] = minrequirements

fieldnames = ["title", "release_date", "price", "link",
              'overall_review', 'percent_positive_reviews', 'num_reviews', 'tags', 'genres', 'minrequirements']
with open('data.csv', 'w') as outpath:
    csvwriter = csv.DictWriter(outpath, fieldnames=fieldnames)
    csvwriter.writeheader()
    csvwriter.writerows(games)
