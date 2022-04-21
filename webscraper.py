import csv
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

tic = time.perf_counter()

driver = webdriver.Chrome(
    executable_path="/Users/justinbaytosh/Netflix/FinalProject/env/chromedriver")


driver.get(
    "https://store.steampowered.com/search/?sort_by=Reviews_DESC&maxprice=free&genre=Free+to+Play")
body = driver.find_element_by_tag_name("body")

total_games = 0
while total_games < 3778:
    body.send_keys(Keys.PAGE_DOWN)
    total_games = len(
        driver.find_elements_by_css_selector('a.search_result_row'))
    print(total_games)

page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")
results = soup.find(id="search_resultsRows")
game_elements = results.find_all(
    "a", class_="search_result_row")

games = []
for game_element in game_elements:
    title_element = game_element.find("span", class_="title")
    release_element = game_element.find("div", class_="search_released")

    title = title_element.text
    release_date = release_element.text
    link = game_element.get("href")

    games.append({"title": title, "release_date": release_date,
                  "price": 0, "link": link})

print(f'total games: {len(games)}')

for game in games:
    URL = game['link']
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="responsive_page_template_content")

    #
    #
    #

    reviews_summary_row = results.find(
        "div", class_="user_reviews_summary_row") if results.find(
        "div", class_="user_reviews_summary_row") is not None else None

    gameplay_elements = results.find(
        id="category_block").find_all("div", class_="label") if results.find(
        id="category_block") is not None else None

    genre_elements = results.find(id="genresAndManufacturer").find_all(
        "a") if results.find(id="genresAndManufacturer") is not None else None

    # change so only get min storage requirement, nothing else
    minrequirements_elements = results.find(
        "div", class_="game_area_sys_req_leftCol").find_all('li') if results.find(
        "div", class_="game_area_sys_req_leftCol") is not None else None

    #
    #
    #

    average_review = 'N/A'
    num_reviews = 'N/A'
    try:
        average_review = reviews_summary_row.find(
            "span", class_="game_review_summary").text
    except AttributeError:
        average_review = None

    try:
        num_reviews = reviews_summary_row.find(
            "span", class_="responsive_hidden").text.strip().replace(')', '').replace('(', '')
    except AttributeError:
        num_reviews = None

    tags = []
    if gameplay_elements:
        for gameplay_element in gameplay_elements:
            tags.append(gameplay_element.text)

    genres = []
    if genre_elements:
        for genre_element in genre_elements:
            genres.append(genre_element.text)
        del genres[-3:]

    minrequirements = []
    if minrequirements_elements:
        for minrequirements_element in minrequirements_elements:
            minrequirements.append(minrequirements_element.text)

    #
    #
    #

    game['average_review'] = average_review
    game['num_reviews'] = num_reviews
    game['tags'] = tags
    game['genres'] = genres
    game['minrequirements'] = minrequirements


fieldnames = ["title", "release_date", "price", "link",
              'average_review', 'num_reviews', 'tags', 'genres', 'minrequirements']
with open('steam_free_data_2.csv', 'w') as outpath:
    csvwriter = csv.DictWriter(outpath, fieldnames=fieldnames)
    csvwriter.writeheader()
    csvwriter.writerows(games)

toc = time.perf_counter()
print(f"Data scraped and processed in {toc - tic:0.4f} seconds")
