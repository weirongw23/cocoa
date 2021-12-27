import random
import urllib.parse

import requests
from fastapi import APIRouter, Request

from cocoa.state import MovieState

router = APIRouter()


def build_response(message: str) -> dict:
    """Given a message, builds a dialogflow-compatible response."""
    return {"fulfillment_response": {"messages": [{"text": {"text": [message]}}]}}


def discoverRec(reqJson):
    """
    Updates default Params (with genres, etc)
    GETs TMDB_API_ROOT data, and returns random recommend
    """
    if (
        "genre" in reqJson["sessionInfo"]["parameters"]
        and reqJson["sessionInfo"]["parameters"]["genre"] != "null"
    ):
        reqGenres = reqJson["sessionInfo"]["parameters"]["genre"]
        try:
            MovieState.params.update(
                {
                    "with_genres": [
                        MovieState.TMDB_GENRE_IDS[reqGenre] for reqGenre in reqGenres
                    ]
                }
            )
        except:
            return build_response("Genre Error")
    if (
        "person" in reqJson["sessionInfo"]["parameters"]
        and reqJson["sessionInfo"]["parameters"]["person"] != "null"
    ):
        people = reqJson["sessionInfo"]["parameters"]["person"]
        peopleIDs = []
        for person in people:
            resJson = requests.get(
                "http://api.tmdb.org/3/search/person?api_key={}&query={}".format(
                    MovieState.TMDB_SECRET, urllib.parse.quote(person["name"])
                )
            ).json()
            if resJson["results"]:
                peopleIDs.append(resJson["results"][0]["id"])
        MovieState.params.update({"with_cast": peopleIDs})

    results = requests.get(MovieState.TMDB_API_ROOT, params=MovieState.params).json()[
        "results"
    ]
    MovieState.currentRec = results[random.randint(0, len(results) - 1)]

    return build_response(
        "I think you'd like {}! It has a popularity of {}, and rating of {}/10".format(
            MovieState.currentRec["title"],
            MovieState.currentRec["popularity"],
            MovieState.currentRec["vote_average"],
        ),
    )


def similarRec():
    if MovieState.currentRec is None:
        return build_response("There's no previous movie to compare against!")

    similarURL = "https://api.themoviedb.org/3/movie/{}/similar".format(
        MovieState.currentRec["id"]
    )
    MovieState.currentRec = requests.get(
        similarURL,
        params={"api_key": MovieState.TMDB_SECRET, "language": "en-US", "page": 1},
    ).json()["results"][random.randint(0, 3)]

    return build_response(
        "One similar movie is {}! It has a popularity of {}, and rating of {}/10".format(
            MovieState.currentRec["title"],
            MovieState.currentRec["popularity"],
            MovieState.currentRec["vote_average"],
        ),
    )


@router.post("/recommend")
async def recommend(r: Request):
    reqJson = await r.json()
    if "parameters" not in reqJson["sessionInfo"] or (
        "genre" in reqJson["sessionInfo"]["parameters"]
        and reqJson["sessionInfo"]["parameters"]["genre"] == "null"
        and "person" in reqJson["sessionInfo"]["parameters"]
        and reqJson["sessionInfo"]["parameters"]["person"] == "null"
    ):
        return build_response("Okay, what sort of movie would you like?")
    return discoverRec(reqJson)


@router.post("/similar")
async def similar(r: Request):
    return similarRec()


@router.post("/overview")
async def overview(r: Request):
    if MovieState.currentRec is None:
        return build_response("No movie recommendation made yet!")

    return build_response(
        "Here's the overview on {}: {}".format(
            MovieState.currentRec["title"],
            MovieState.currentRec["overview"],
        )
    )


@router.post("/reset")
async def reset(r: Request):
    MovieState.params = MovieState.MOVIE_DEFAULT_PARAMS
