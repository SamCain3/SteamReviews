import requests
from bs4 import BeautifulSoup

URL = 'https://store.steampowered.com/app/1698960/Project_Kat__Paper_Lily_Prologue/'
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="responsive_page_template_content")

rating_details = results.find(
    "span", class_="nonresponsive_hidden").text.split('%')[0].replace(' - ', '')

print(rating_details)
