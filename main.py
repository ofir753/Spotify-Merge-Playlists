#!/usr/bin/env python3.8

import spotipy
import json
from os import environ
from spotipy.oauth2 import SpotifyOAuth
from argparse import ArgumentParser, FileType
import datetime

ADD_TRACKS_PER_REQUEST_LIMIT = 100
REMOVE_TRACKS_PER_REQUEST_LIMIT = 100 # No idea if its the limit but i dont want to test it

SPOTIFY_PLAYLIST_SCOPE = 'playlist-modify-private playlist-modify-public'
SECRETS_CLIENT_ID = 'spotfiy-api-clientid'
SECRETS_SECRET_ID = 'spotfiy-api-secret'
SECRETS_REDIRECT_URI = 'spotfiy-api-riderct_uri'
CACHE_PATH = 'cache_file'

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

def merge_playlist_from_dict(spotify, playlist_dict):
    print("Merging %s" % (playlist_dict['name']))

    merge_playlist(spotify, playlist_dict['merged_playlist'], playlist_dict['child_playlists'])
    print("")

def strip_spotify_playlist_uri(spotify_uri):
    return spotify_uri.replace('spotify:playlist:', '')

def merge_playlist(spotify, output_playlist, child_playlists):
    output_tracks = get_tracks_id_from_playlist(spotify, output_playlist)
    childs_tracks = get_all_tracks_from_playlists(spotify, child_playlists)

    tracks_to_add = list(set(childs_tracks) - set(output_tracks))
    tracks_to_remove = list(set(output_tracks) - set(childs_tracks))

    tracks_to_add = list(filter(lambda track: track != None, tracks_to_add))
    tracks_to_remove = list(filter(lambda track: track != None, tracks_to_remove))

    print("Adding %u tracks, Removing %u tracks" % (len(tracks_to_add), len(tracks_to_remove)))

    add_tracks(spotify, output_playlist, tracks_to_add)
    remove_tracks(spotify, output_playlist, tracks_to_remove)

    description = "Last time updated: %s" % (datetime.datetime.now())
    spotify.user_playlist_change_details('spotify', strip_spotify_playlist_uri(output_playlist), description=description)

def connect_to_spotify(secrets_file_stream):
    secrets = json.load(secrets_file_stream)
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SPOTIFY_PLAYLIST_SCOPE,
                        client_id=secrets[SECRETS_CLIENT_ID],
                        client_secret=secrets[SECRETS_SECRET_ID],
                        redirect_uri=secrets[SECRETS_REDIRECT_URI],
                        cache_path=CACHE_PATH))

    return spotify


def main():
    parser = ArgumentParser(description="Merge Spotify Playlists")
    parser.add_argument('input_file', nargs='?', type=FileType('r'), default="input.json")
    parser.add_argument('secrets_file', nargs='?', type=FileType('r'), default="secrets.json")

    args = parser.parse_args()

    spotify = connect_to_spotify(args.secrets_file)

    playlists_to_merge = json.load(args.input_file)
    playlists_to_merge = playlists_to_merge['playlists']

    for playlist in playlists_to_merge:
        merge_playlist_from_dict(spotify, playlist)


if __name__ == '__main__':
    main()