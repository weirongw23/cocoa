import base64
import random
import urllib.parse

import requests
from fastapi import APIRouter, Request

from cocoa.state import MusicState

router = APIRouter()


def build_response(message: str) -> dict:
    """Given a message, builds a dialogflow-compatible response."""
    return {"fulfillment_response": {"messages": [{"text": {"text": [message]}}]}}


def getAccessToken():
    authBytes = (MusicState.SPOTIFY_ID + ":" + MusicState.SPOTIFY_SECRET).encode(
        "ascii"
    )
    authHeader = {
        "Authorization": "Basic " + base64.b64encode(authBytes).decode("ascii")
    }
    payload = {
        "grant_type": "client_credentials",
    }
    resJson = requests.post(
        "https://accounts.spotify.com/api/token",
        headers=authHeader,
        data=payload,
    ).json()
    MusicState.SPOTIFY_ACCESS_TOKEN = resJson["access_token"]


def topByArtist(reqJson, authHeader):
    personName = reqJson["sessionInfo"]["parameters"]["person"]["name"]
    resJson = requests.get(
        "https://api.spotify.com/v1/search",
        headers=authHeader,
        params={"type": "artist", "q": personName},
    ).json()
    if len(resJson["artists"]["items"]) > 0:
        artistID = resJson["artists"]["items"][0]["id"]
        resJson = requests.get(
            "https://api.spotify.com/v1/artists/{}/top-tracks".format(artistID),
            headers=authHeader,
            params={"market": "US"},
        ).json()

        rec = resJson["tracks"][random.randint(0, len(resJson["tracks"]) - 1)]
        MusicState.currentRec = rec
        return build_response(
            "One of {}'s songs I recommend is {}.".format(
                personName.title(), rec["name"]
            )
        )


def discoverMusic(reqJson):
    """
    Updates default Params (with genres, etc)
    GETs Spotify data, and returns random recommend
    """
    getAccessToken()
    MusicState.params = {}
    authHeader = {"Authorization": "Bearer " + MusicState.SPOTIFY_ACCESS_TOKEN}
    if (
        "person" in reqJson["sessionInfo"]["parameters"]
        and reqJson["sessionInfo"]["parameters"]["person"] != "null"
    ):
        return topByArtist(reqJson, authHeader)
    if (
        "music_genre" in reqJson["sessionInfo"]["parameters"]
        and reqJson["sessionInfo"]["parameters"]["music_genre"] != "null"
    ):
        reqGenres = reqJson["sessionInfo"]["parameters"]["music_genre"]
        try:
            MusicState.params.update({"seed_genres": reqGenres})
        except:
            return build_response("Genre Error")
        resJson = requests.get(
            "https://api.spotify.com/v1/recommendations",
            headers=authHeader,
            params=MusicState.params,
        ).json()
    if len(resJson["tracks"]) > 0:
        rec = resJson["tracks"][0]
        MusicState.currentRec = rec
        return build_response(
            "I think you'd like {} by {}! You can listen to it here: {}".format(
                rec["name"], rec["artists"][0]["name"], rec["external_urls"]["spotify"]
            )
        )
    return build_response("Couldn't find any music under that genre, sorry.")


def similarMusic():
    """
    Updates default Params (with genres, etc)
    GETs Spotify data, and returns random similar
    """
    getAccessToken()
    authHeader = {"Authorization": "Bearer " + MusicState.SPOTIFY_ACCESS_TOKEN}
    if MusicState.currentRec is None:
        return build_response("There's no previous song to compare against!")

    similarParams = {"seed_tracks": MusicState.currentRec["id"]}
    resJson = requests.get(
        "https://api.spotify.com/v1/recommendations",
        headers=authHeader,
        params=similarParams,
    ).json()
    if len(resJson["tracks"]) > 0:
        rec = resJson["tracks"][0]
        return build_response(
            "One similar song is {} by {}! You can listen to it here: {}".format(
                rec["name"], rec["artists"][0]["name"], rec["external_urls"]["spotify"]
            )
        )
    return build_response("Couldn't find any music under that genre, sorry.")


@router.post("/musicrecommend")
async def recommend(r: Request):
    reqJson = await r.json()
    if "parameters" not in reqJson["sessionInfo"] or (
        "music_genre" in reqJson["sessionInfo"]["parameters"]
        and reqJson["sessionInfo"]["parameters"]["music_genre"] == "null"
        and "person" in reqJson["sessionInfo"]["parameters"]
        and reqJson["sessionInfo"]["parameters"]["person"] == "null"
    ):
        return build_response("Okay, what sort of song would you like?")
    return discoverMusic(reqJson)


@router.post("/musicsimilar")
async def similar(r: Request):
    reqJson = await r.json()
    return similarMusic()
