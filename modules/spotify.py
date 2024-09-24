import os
import requests
from dotenv import load_dotenv

load_dotenv()

def authenticate_spotify():
    # Replace with your actual client_id and client_secret
    client_id = os.getenv("SPOTIFY_ID")
    client_secret = os.getenv("SPOTIFY_KEY")
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(
        auth_url,
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    auth_data = auth_response.json()
    return auth_data["access_token"]


def find_playlist(query):
    token = authenticate_spotify()
    headers = {"Authorization": f"Bearer {token}"}
    search_url = f"https://api.spotify.com/v1/search?q={query}&type=playlist&limit=1"
    response = requests.get(search_url, headers=headers)
    data = response.json()

    if "playlists" in data and data["playlists"]["items"]:
        playlist = data["playlists"]["items"][0]
        playlist_name = playlist["name"]
        playlist_url = playlist["external_urls"]["spotify"]
        return f"{playlist_name}: {playlist_url}"
    else:
        return {"error": "No playlist found for the query"}


if __name__ == "__main__":
    print(find_playlist("Beastars OST"))