#!/usr/bin/python

import httplib2
import os
import sys
import pprint
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import feedparser
import webbrowser
import argparse
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this script run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def build_youtube():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
            message=MISSING_CLIENT_SECRETS_MESSAGE,
            scope=YOUTUBE_READ_WRITE_SCOPE)
    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flags = argparser.parse_args()
        credentials = run_flow(flow, storage, flags)
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            http=credentials.authorize(httplib2.Http()))
    return youtube

def add_video_to_playlist(youtube,videoID,playlistID):
    add_video_request=youtube.playlistItems().insert(
        part="snippet",
        fields="snippet",
        body={
            'snippet': dict(
                playlistId=playlistID,
                resourceId=dict(
                   kind='youtube#video',
                   videoId=videoID
                )
                #'position': 0
            )
        }
    ).execute()


def look_for_playlist(youtube, title):
    playlists = youtube.playlists().list(part='snippet', mine=True).execute()
    for p in playlists['items']:
        if p['snippet']['title'] == title:
            return p['id']
    return None

def create_playlist(youtube, minimal_score, status="public"):
    title='Haker News Playlist (more than {} points)'.format(minimal_score)
    i = look_for_playlist(youtube, title)
    if i:
        print 'delete playlist', i
        youtube.playlists().delete(id=i).execute()
    playlists_insert_response = youtube.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
               title=title,
            ),
            status=dict(
                privacyStatus=status
            )
       )
    ).execute()
    return playlists_insert_response['id']


def extract_id(f):
    return f['link'].split('=')[1].split('&')[0].split('/')[0]


def main(args):
    minimal_score = args.minimal_score
    youtube = build_youtube()
    hn_playlist_id = create_playlist(youtube, minimal_score, args.status)
    feed_url = 'http://hnrss.org/newest?q=www.youtube.com&search_attrs=url&points={}'.format(minimal_score)
    feed = feedparser.parse(feed_url)
    for f in feed['entries']:
        try:
            add_video_to_playlist(youtube, extract_id(f), hn_playlist_id)
            print f['title'], '\t', f['published']
        except:
            print "*** error on ", f['title'], extract_id(f)
    
    playlist_url = 'https://www.youtube.com/playlist?list={}'.format(hn_playlist_id)
    webbrowser.open(playlist_url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--minimal_score', type=int, default=30, help='the minimal score of youtube link to be included on the playlist (default: %(default)s)')
    parser.add_argument('--status', choices=['public', 'private'], default='private', help='the sharing status of the created playlist (default: %(default)s)')
    main(parser.parse_args())
