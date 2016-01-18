# hn-playlist
Script that create Youtube playlist containing popular videos shared on hackernews.

## prerequisites
To run this script you will need to add the file client_secrets.json from Cloud Console: https://cloud.google.com/console to the script console.

Please ensure that you have enabled the YouTube Data API for your project.

For more information about using OAuth2 to access the YouTube Data API, see:
  https://developers.google.com/youtube/v3/guides/authentication

For more information about the client_secrets.json file format, see:
  https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

In addition you will need:

* ```pip install feedparser```
* ```pip install --upgrade httplib2```
* ```pip install --upgrade google-api-python-client```

## usage
```
hn_playlist.py [-h] [--minimal_score MINIMAL_SCORE]
                      [--status {public,private}]

optional arguments:
  -h, --help            show this help message and exit
  --minimal_score MINIMAL_SCORE
                        the minimal score of youtube link to be included on
                        the playlist (default: 30)
  --status {public,private}
                        the sharing status of the created playlist (default:
                        private)
```

## more information
* The title of the playlist will be: *Haker News Playlist (more than {MINIMAL_SCORE} points)*.
* If there is a playlist with the same name on the channel it will be deleted before re-generation.
* The script will print to stdout the name of the hacker news story with the link and the date it was added.
* If the video can't be added to playlist (i.e. it was removed) error message will be printed to stdout/
* On the end of the script, browser will be opened on the playlist url.
 
## credits
The Hacker News data was obtained from https://edavis.github.io/hnrss/
