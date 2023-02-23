import os
import re
import spotipy
import requests
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

date_pattern = "^[1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]$"
date_valid = None

while not date_valid:

    date = input("Which year do you want to travel to? Type the date in this format: YYYY-MM-DD: ")

    # Validate date
    if re.match(date_pattern, date):
        date_list = date.split("-")
        year = int(date_list[0])
        month = int(date_list[1])
        day = int(date_list[2])

        if year >= 1958 and month in range(1, 13) and day in range(1, 32):
            date_valid = True
        else:
            print("Sorry, that didn't work. Make sure to input the date correctly!\n"
                  "(should work from 1958-08-04 onwards)")
    else:
        print("Sorry, that didn't work. Make sure to use the correct date format!")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}/")
response.raise_for_status()
website = response.text

soup = BeautifulSoup(website, "html.parser")
song_items = soup.select("li.o-chart-results-list__item h3")
artist_items = soup.select("span.c-label.a-no-trucate.a-font-primary-s")

song_titles = [song_item.getText(strip=True) for song_item in song_items]
artist_names = [artist_item.getText(strip=True) for artist_item in artist_items]

tracks = (list(zip(artist_names, song_titles)))

scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope,
))

year = date.split("-")[0]

track_URIs = []

# Search for track URIs
for artist, song in tracks:
    track_search = sp.search(
        q=f"artist: {artist} track: {song} year: {year}",
        type="track",
        limit=1,
        market="PL",
    )
    URI = track_search["tracks"]["items"][0]["uri"]
    track_URIs.append(URI)
    print(URI)

print(track_URIs)

# Create Spotify playlist
user_id = sp.current_user().get("id")
playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{date} Billboard 100",
    public=False,
    description="Musical Time Machine")

print(playlist)
playlist_id = playlist["id"]

# Add songs to the playlist
sp.playlist_add_items(playlist_id=playlist_id, items=track_URIs)

print(playlist)