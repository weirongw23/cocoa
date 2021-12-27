import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud.dialogflowcx_v3 import SessionsClient, types

from cocoa import movie, music, restaurant
from cocoa.state import DialogFlowState

app = FastAPI()

# Setup CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movie.router)
app.include_router(restaurant.router)
app.include_router(music.router)

# Dialogflow client setup:
session_path = f"{DialogFlowState.AGENT}/sessions/testing2"
session_client = SessionsClient.from_service_account_file(
    "google-creds.json",
    client_options={"api_endpoint": "us-central1-dialogflow.googleapis.com:443"},
)


@app.get("/getintent")
def getintent(intent: str) -> str:
    request = types.DetectIntentRequest(
        session=session_path,
        query_input=types.QueryInput(
            text=types.TextInput(text=intent),
            language_code=DialogFlowState.LANGUAGE_CODE,
        ),
    )
    response = session_client.detect_intent(request=request)
    print(response)
    return " ".join(
        " ".join(msg.text.text) for msg in response.query_result.response_messages
    )


def run():
    uvicorn.run("cocoa.server:app", host="localhost", port=8000, reload=True)
