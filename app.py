from __future__ import annotations

from datetime import date

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from fake_data import create_app

user_dict = create_app()
app = FastAPI()


@app.get("/")
def connexion(
    user_name: str, year: int, month: int, day: int, meal_id: int | None = None, aliments_df=pd.DataFrame) -> JSONResponse:
    # If the store is not in the dictionary
    if not (user_name in user_dict.keys()):
        return JSONResponse(status_code=404, content="User Not found")
    classe_mangeur = user_dict[user_name]

    # Check the value of meal_id
    if classe_mangeur == 'standard' and meal_id and (meal_id > 4 or meal_id < 1):
        return JSONResponse(
            status_code=404, content="Meal_id should be between 1 and 4"
        )
    if classe_mangeur == 'meat_lover' and meal_id and (meal_id > 4 or meal_id < 1):
        return JSONResponse(
            status_code=404, content="Meal_id should be between 1 and 4"
        )
    if classe_mangeur == 'vegan' and meal_id and (meal_id > 4 or meal_id < 1):
        return JSONResponse(
            status_code=404, content="Sensor_id should be between 1 and 4"
        )
    if classe_mangeur == 'vegetarian' and meal_id and (meal_id > 4 or meal_id < 1):
        return JSONResponse(
            status_code=404, content="Sensor_id should be between 1 and 4"
        )
    if classe_mangeur == 'random' and meal_id and (meal_id != 1):
        return JSONResponse(
            status_code=404, content="Sensor_id should be 1"
        )
    if classe_mangeur == 'fasting' and meal_id and (meal_id > 2 or meal_id < 1):
        return JSONResponse(
            status_code=404, content="Sensor_id should be between 1 or 2"
        )

    # Check the year
    if year < 2024:
        return JSONResponse(status_code=404, content="No data before 2024")

    # Check the date
    try:
        date(year, month, day)
    except TypeError:
        return JSONResponse(status_code=404, content="Enter a valid date")

    # Check the date is in the past
    if date.today() < date(year, month, day):
        return JSONResponse(status_code=404, content="Choose a date in the past")

    # If no sensor choose return the visit for the whole store
    if meal_id is None:
        connexion_counts = user_dict[user_name].get_all_connexion(
            date(year, month, day), aliments_df, user_name
        )
    else:
        connexion_counts = user_dict[user_name].get_connexion(
            meal_id, date(year, month, day), aliments_df, user_name
        )

    if connexion_counts < 0:
        return JSONResponse(
            status_code=404, content="The store was closed try another date"
        )

    return JSONResponse(status_code=200, content=connexion_counts)