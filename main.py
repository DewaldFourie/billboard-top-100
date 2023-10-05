from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def remove_values_from_list(the_list, val):
    return [value for value in the_list if value != val]


URL = "https://www.billboard.com/charts/hot-100/2000-08-12/"
SPOTIFY_CLIENT_ID = "entersecretid"
SPOTIFY_CLIENT_SECRET = "entersecretid"
URL_REDIRECT = "https://example.com/callback"

# -----------------------------------------SCRAPING BILLBOARD 100---------------------------------------------------

response = requests.get("https://www.billboard.com/charts/hot-100/2000-08-12/")
web_page = response.text

soup = BeautifulSoup(web_page, "html.parser")
songs = soup.find_all(name="h3", id="title-of-a-story", class_="u-letter-spacing-0021")

top_100_songs_names = soup.find_all(name="h3", class_="u-max-width-230@tablet-only", id="title-of-a-story")
top_100_songs_names = [song.text.strip() for song in top_100_songs_names]

top_100_songs_artist = soup.find_all(name="span", class_="u-letter-spacing-0021")
top_100_songs_artist = [artist.text.strip() for artist in top_100_songs_artist]

# ----------------------------------------SPOTIFY AUTHENTICATION-----------------------------------------------------

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private",
                                                    redirect_uri=URL_REDIRECT,
                                                    client_id=SPOTIFY_CLIENT_ID,
                                                    client_secret=SPOTIFY_CLIENT_SECRET,
                                                    show_dialog=True,
                                                    cache_path="token.txt"
                                                    )
                          )

user_id = spotify.current_user()["id"]

# ----------------------------------------SEARCHING SPOTIFY FOR SONGS BY TITLE---------------------------------------

date = input("What year do you want to travel to? Type the date in this format YYYY-MM-DD:\n")
song_names = top_100_songs_names

song_uris = []
year = date.split("-")[0]
for song in song_names:
    result = spotify.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# --------------------------------------------CREATING A NEW PLAYLIST ON SPOTIFY---------------------------------------


playlist = spotify.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

# -------------------------------------------ADDING SONGS FOUNT TO NEW PLAYLIST----------------------------------------

spotify.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
