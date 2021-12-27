from datetime import datetime, timedelta
from random import choice

import requests
from fastapi import APIRouter, Request

from cocoa.state import RestaurantState

router = APIRouter()


def build_response(message):
    return {"fulfillment_response": {"messages": [{"text": {"text": [message]}}]}}


def get_params(params):
    keys = ["price", "term", "radius", "open_now"]
    values = [
        params[key]["resolvedValue"] if key in params else None
        for key in ["price", "term", "radius", "opennow"]
    ]
    return dict(zip(keys, values))


def call_search_api(term=None, price=None, radius=None, open_now=None):
    params = {
        "location": "Ann Arbor",
    }
    if term is not None:
        params["term"] = term
    if price is not None:
        params["price"] = price
    try:
        params["radius"] = int(radius)
    except:
        pass
    try:
        params["open_now"] = bool(open_now)
    except:
        pass

    headers = {
        "Authorization": "Bearer Vsz2KzC1R6YWWr_IkAjaWCXcb7t-9sgaIKN1ALmf6rVvFZf-Aicmfh_TUc4zdzxL-_7kFxkPxqQM4AFjT22WthWNJYVCwUZH-iLTLP7nc1StEfgydb2so4EiJF2RYXYx",
        "content-type": "application/json",
    }

    return requests.get(
        f"{RestaurantState.YELP_API_ROOT}/search", params=params, headers=headers
    ).json()


def call_details_api():
    return requests.get(
        f"{RestaurantState.YELP_API_ROOT}/{RestaurantState.lastRec['id']}",
        headers=RestaurantState.YELP_API_HEADERS,
    ).json()


def call_reviews_api():
    return requests.get(
        f"{RestaurantState.YELP_API_ROOT}/{RestaurantState.lastRec['id']}/reviews",
        headers=RestaurantState.YELP_API_HEADERS,
    ).json()


def RatingIntentHandler():
    return build_response(
        f"{RestaurantState.lastRec['name']} has a rating of {RestaurantState.lastRec['rating']} stars out of 5.0!"
    )


def AddressIntentHandler():
    return build_response(
        f"{RestaurantState.lastRec['name']} is located at {RestaurantState.lastRec['location']['address1']}."
    )


def DistanceIntentHandler():
    return build_response(
        f"You're about {RestaurantState.lastRec['distance']} meters away from {RestaurantState.lastRec['name']}."
        + " Of course, due to privacy reasons, I don't know your exact location, but I'm guessing you're somewhere in Ann Arbor..."
    )


def CategoryIntentHandler():
    aliases = [
        str(category["alias"]) for category in RestaurantState.lastRec["categories"]
    ]
    return build_response(
        f"{RestaurantState.lastRec['name']} is known for {', '.join(aliases)}"
    )


def DeliveryPickupIntentHandler():
    if not RestaurantState.lastRec["transactions"]:
        return build_response(
            f"Unfortunately, {RestaurantState.lastRec['name']} does not support delivery, pickup, or reservations."
        )

    transactions = RestaurantState.lastRec["transactions"]
    return build_response(
        f"{RestaurantState.lastRec['name']} allows for {', '.join(transactions)}"
    )


def convtime(time):
    # Convert from HH:MM[:SS] in UTC to HH:MM AM/PM in EST:
    t = datetime.strptime(time[:4], "%H%M")
    # Subtract 5 hours to convert to EST:
    t -= timedelta(hours=5)
    # Convert to 12 hour time:
    return t.strftime("%I:%M %p")


def HoursIntentHandler():
    hours = call_details_api()["hours"][0]
    today = datetime.today().weekday()
    tomorrow = (datetime.today() + timedelta(days=1)).weekday()

    if hours["is_open_now"]:
        resp = "You're in luck! {} is currently open until {}".format(
            RestaurantState.lastRec["name"], convtime(hours["open"][today]["end"])
        )
    else:
        resp = (
            "Unfortunately, {} is closed... Tomorrow's hours will be {} to {}".format(
                RestaurantState.lastRec["name"],
                convtime(hours["open"][tomorrow]["start"]),
                convtime(hours["open"][tomorrow]["end"]),
            )
        )
    return build_response(resp)


def PhoneIntentHandler():
    return build_response(
        f"You can call them at {RestaurantState.lastRec['phone'][2:]}."
    )


def PriceIntentHandler():
    price = len(RestaurantState.lastRec["price"])
    priceRange = {
        1: "under $10. A good bargain.",
        2: "$11 to $30, so pretty mid-range.",
        3: "$31 to $60.",
        4: "over $61. Pretty pricy!",
    }[price]
    return build_response(
        f"According to yelp, the menu has a price level of {price} out of 4. So, the food is {priceRange}"
    )


def ReviewIntentHandler():
    review = call_reviews_api()["reviews"][0]
    return build_response(
        f"Here's a {review['rating']} star review from {review['user']['name']}: \"{review['text']}\"."
    )


@router.post("/webhook")
async def webhook(r: Request):
    req = await r.json()
    try:
        intentName = req["intentInfo"]["displayName"]
        params = req["intentInfo"].get("parameters") or {}
        if intentName == "food_RecommendIntent":
            resp_json = call_search_api(**get_params(params))
            assert resp_json["businesses"], "no businesses found"
            RestaurantState.lastRec = choice(resp_json["businesses"])
            return build_response(
                f"Hmm, I recommend you try out {RestaurantState.lastRec['name']}"
            )
        elif RestaurantState.lastRec is None:
            return build_response(
                "I don't remember which restaurant you were asking about."
            )
        elif intentName == "food_filter_RatingIntent":
            return RatingIntentHandler()
        elif intentName == "food_filter_AddressIntent":
            return AddressIntentHandler()
        elif intentName == "food_filter_CategoryIntent":
            return CategoryIntentHandler()
        elif intentName == "food_filter_DeliveryPickupIntent":
            return DeliveryPickupIntentHandler()
        elif intentName == "food_filter_DistanceIntent":
            return DistanceIntentHandler()
        elif intentName == "food_filter_HoursIntent":
            return HoursIntentHandler()
        elif intentName == "food_filter_PhoneIntent":
            return PhoneIntentHandler()
        elif intentName == "food_filter_PriceIntent":
            return PriceIntentHandler()
        elif intentName == "food_filter_ReviewIntent":
            return ReviewIntentHandler()
        raise Exception(f"Error: Unrecognized intent {intentName}")
    except Exception as e:
        print(f"Exception found: {e}")
        return build_response("Sorry, we could not understand your query.")
