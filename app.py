from __future__ import annotations

from datetime import date

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from fake_data import create_app

user_dict = create_app()
app = FastAPI()


@app.get("/")
def connexion(
    user_name: str, year: int, month: int, day: int, user_id: int | None = None
) -> JSONResponse:
    # If the store is not in the dictionary
    if not (user_name in user_dict.keys()):
        return JSONResponse(status_code=404, content="User Not found")

    # Check the value of sensor_id
    if user_id and (user_id > len(user_dict) or user_id < 0):
        return JSONResponse(
            status_code=404, content="Sensor_id should be between 0 and 7"
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
    if user_id is None:
        connexion_counts = user_dict[user_name].get_all_traffic(date(year, month, day))
    else:
        connexion_counts = user_dict[user_name].get_sensor_traffic(
            user_id, date(year, month, day)
        )

    if connexion_counts < 0:
        return JSONResponse(
            status_code=404, content="The store was closed try another date"
        )

    return JSONResponse(status_code=200, content=connexion_counts)