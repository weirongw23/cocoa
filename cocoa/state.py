"""

Encodes globals and static vars for the backend

"""

import uuid
from typing import Optional


class DialogFlowState:
    AGENT = "projects/cocoa-332118/locations/us-central1/agents/ae320936-d399-4004-98f8-9700f2310260"
    LANGUAGE_CODE = "en-us"
    session_id: uuid.UUID = uuid.uuid4()


class MovieState:
    ### STATIC VARS ###
    TMDB_SECRET = "24ff06c312e37d3cb6073bad3655ca12"
    TMDB_API_ROOT = "https://api.themoviedb.org/3/discover/movie"
    MOVIE_DEFAULT_PARAMS = {
        "api_key": TMDB_SECRET,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "page": 1,
    }
    TMDB_GENRE_IDS = {
        "Action": 28,
        "Adventure": 12,
        "Animation": 16,
        "Comedy": 35,
        "Crime": 80,
        "Documentary": 99,
        "Drama": 18,
        "Family": 10751,
        "Fantasy": 14,
        "History": 36,
        "Horror": 27,
        "Music": 10402,
        "Mystery": 9648,
        "Romance": 10749,
        "Science Fiction": 878,
        "TV Movie": 10770,
        "Thriller": 53,
        "War": 10752,
        "Western": 37,
    }

    ### GLOBALS ###
    params: dict = MOVIE_DEFAULT_PARAMS
    currentRec: Optional[dict] = None


class RestaurantState:
    ### STATIC VARS ###
    YELP_API_ROOT = "https://api.yelp.com/v3/businesses"
    YELP_API_HEADERS = {
        "Authorization": "Bearer Vsz2KzC1R6YWWr_IkAjaWCXcb7t-9sgaIKN1ALmf6rVvFZf-Aicmfh_TUc4zdzxL-_7kFxkPxqQM4AFjT22WthWNJYVCwUZH-iLTLP7nc1StEfgydb2so4EiJF2RYXYx",
        "content-type": "application/json",
    }

    ### GLOBALS ###
    lastRec: Optional[dict] = None


class MusicState:
    ### STATIC VARS ###
    SPOTIFY_ID = "f9af5a52e1ac48348d448970f7f777b8"
    SPOTIFY_SECRET = "ad23164238ec4ed6a3a6be3308948272"

    ### GLOBALS ###
    SPOTIFY_ACCESS_TOKEN = None
    params = {}
    currentRec: Optional[dict] = None
