# COCOA
> This is the backend for our COCOA bot.

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
