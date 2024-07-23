# COCOA
> This is the backend for our COCOA bot.

## Product Features
- [Product Demo](https://www.youtube.com/watch?v=7q5QhEqZHBw&ab_channel=RobertKang)
- [Product Walkthrough](https://docs.google.com/presentation/d/1NwLBlXiXcbnBE8y7UPCaglUemoXy7SG_ZJJBgGriaLM/edit?usp=sharing)

## Tech Stack
- **Web:** Python Backend (FastAPI, Pydantic), Next.js and Tailwind CSS Frontend
- **NLP and Entity Recognition:** Dialogflow
- **APIs:** Spotify, TMDB, Yelp
- **CI/CD:** Heroku

## Architecture Design
**Cocoa's Conversational AI Architecture**
![Cocoa's Conversational AI Architecture](https://github.com/weirongw23/cocoa/blob/main/cocoa-architecture.png)

**System Architecture**
![System Architecture](https://github.com/weirongw23/cocoa/blob/main/sys-architecture.png)

**Backend Services**
![Backend Services](https://github.com/weirongw23/cocoa/blob/main/backend-services.png)

## Installation Instructions

To install this project, first install [poetry](https://python-poetry.org/docs/) on your machine.
Afterwards, enter the project folder and run `poetry install`. You should then be able to run the 
backend with `poetry run cocoa`.

## Contribution Instructions
Before you commit, in order to maintain code quality, it is **required** that you adhere to the style
guidelines. Luckily, this is very easy to do– just run the following two commands before you upload:
```bash
poetry run isort --profile=black cocoa
poetry run black cocoa
```

## Deployment
Running on heroku @ https://convai.herokuapp.com/. Auto deploys are enabled!
