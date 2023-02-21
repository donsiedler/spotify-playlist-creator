import os
import re
import spotipy
import requests
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

from pprint import pprint

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

date_pattern = "^\d{4}-\d{2}-\d{2}$"
date_valid = None

while not date_valid:

    date = input("Which year do you want to travel to? Type the date in this format: YYYY-MM-DD: ")

    # Validate date
    if re.match(date_pattern, date):
        date_valid = True
    else:
        print("Sorry, that didn't work. Make sure to use the correct date format!")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}/")
response.raise_for_status()
website = response.text

soup = BeautifulSoup(website, "html.parser")
items = soup.select("li .o-chart-results-list__item h3")

song_titles = [item.getText(strip=True) for item in items]
print(song_titles)

scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope,
))

user_id = sp.current_user().get("id")

year = date.split("-")[0]

for song in song_titles:
    track_search = sp.search(
        q=f"track: {song} year: {year}",
        type="track",
        limit=1,
        market="PL",
    )
    print(track_search["tracks"]["items"][0]["uri"])

