#!/usr/bin/env python3.8

import spotipy
import json
from os import environ
from spotipy.oauth2 import SpotifyOAuth

ADD_TRACKS_PER_REQUEST_LIMIT = 100
REMOVE_TRACKS_PER_REQUEST_LIMIT = 100 # No idea if its the limit but i dont want to test it

SPOTIFY_PLAYLIST_SCOPE = 'playlist-modify-private'
SECRETS_CLIENT_ID = 'spotfiy-api-clientid'
SECRETS_SECRET_ID = 'spotfiy-api-secret'
REDIRECT_URI = 'http://example.com'
CACHE_PATH = 'cache_file'

child_playlists = []
output_playlist = ''

def parse_secrets():
    with open('secrets.json') as f:
        secrets = json.load(f)
        
        return secrets

def get_tracks_id(tracks_info):
    return list(map(lambda track: track['track']['id'], tracks_info['items']))


def get_tracks_id_from_playlist(spotify, playlist_id):
    playlist = spotify.user_playlist('spotify', playlist_id)

    tracks_info = playlist['tracks']
    tracks_id = get_tracks_id(tracks_info)

    while tracks_info['next']:
        tracks_info = spotify.next(tracks_info)
        tracks_id.extend(get_tracks_id(tracks_info))

    return tracks_id

def combine_two_lists_without_duplicates(list_1, list_2):
    set_1 = set(list_1)
    set_2 = set(list_2)

    list_2_items_not_in_list_1 = list(set_2 - set_1)
    combined_list = list_1 + list_2_items_not_in_list_1

    return combined_list

def get_all_tracks_from_playlists(spotify, playlists):
    all_tracks = []
    for playlist_id in playlists:
        tracks = get_tracks_id_from_playlist(spotify, playlist_id)

        all_tracks = combine_two_lists_without_duplicates(all_tracks, tracks)

    return all_tracks

def to_chunks(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def add_tracks(spotify, playlist, tracks_to_add):
    tracks_to_add_chunks = to_chunks(tracks_to_add, ADD_TRACKS_PER_REQUEST_LIMIT)

    for i, chunk in enumerate(tracks_to_add_chunks):
        spotify.user_playlist_add_tracks('spotify', playlist, chunk)
        print("Tracks Added Chunk %u/%u" %  (i, len(tracks_to_add_chunks)))

def remove_tracks(spotify, playlist, tracks_to_remove):
    tracks_to_remove = to_chunks(tracks_to_remove, REMOVE_TRACKS_PER_REQUEST_LIMIT)

    for i, chunk in enumerate(tracks_to_remove):
        spotify.user_playlist_remove_all_occurrences_of_tracks('spotify', playlist, chunk)
        print("Tracks Removed Chunk %u/%u" % (i, len(tracks_to_remove)))

def main():
    secrets = parse_secrets()
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SPOTIFY_PLAYLIST_SCOPE,
                        client_id=secrets[SECRETS_CLIENT_ID],
                        client_secret=secrets[SECRETS_SECRET_ID],
                        redirect_uri=REDIRECT_URI,
                        cache_path=CACHE_PATH))

    output_tracks = get_tracks_id_from_playlist(spotify, output_playlist)
    childs_tracks = get_all_tracks_from_playlists(spotify, child_playlists)

    tracks_to_add = list(set(childs_tracks) - set(output_tracks))
    tracks_to_remove = list(set(output_tracks) - set(childs_tracks))

    print("Adding %u tracks, Removing %u tracks" % (len(tracks_to_add), len(tracks_to_remove)))

    add_tracks(spotify, output_playlist, tracks_to_add)
    remove_tracks(spotify, output_playlist, tracks_to_remove)


if __name__ == '__main__':
    main()