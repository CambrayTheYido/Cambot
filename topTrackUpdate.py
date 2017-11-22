#!/usr/bin/env python
import sys
from twython import Twython
import pylast
import spotipy
import spotipy.util as util
import config
import twitter_handles

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username
last_fm_password = config.lastfm_password_hash

# Spotify API
scope = config.spotify_scope
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

#Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

#LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username,
                               password_hash=pylast.md5(last_fm_password))
user = network.get_user(last_fm_username)

#Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=scope)

# Get the top track from the last 7 days
topTrack = user.get_top_tracks(period='7day', limit='1')

for x in topTrack:
    search = x[0]

if len(sys.argv) > 1:
    search_str = sys.argv[1]
else:
    search_str = str(search)

sp = spotipy.Spotify(auth=token)
result = sp.search(search, limit='1')
things = result['tracks']['items']
for track in things:
    url = track['external_urls']
    url = url.get('spotify')

    artist_name = str(track['artists'][0].get('name'))
    artist_name_with_at = twitter_handles.is_artist_in_dict(artist_name)

    if artist_name.lower() in search_str.lower():
        search_str = search_str.replace(artist_name, artist_name_with_at, 1)

# Check if the URL has already been tweeted lately, if not then tweet new link
files = open("topTrackURL.txt", "r")
for line in files:
    if line != url:
        file = open("topTrackURL.txt", "w")
        file.write(url)
        file.close
        tweetStr = "#TopTrackUpdate \n" + str(search) + "\n" + str(url)
        print(tweetStr)
        api.update_status(status=tweetStr)
