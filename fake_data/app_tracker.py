from typing import Tuple, Any

import pandas as pd
import numpy as np
from datetime import date, datetime

import openpyxl


try:
    from data_engineering.sensor_api.fake_data.sensor import create_user_instance
except ImportError:
    from .sensor import create_user_instance

import sys
import os

# Ajoutez le répertoire parent de 'data_engineering' au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

class AppTracker:
    def __init__(self, user_data: list) -> None:
        """
        Initialize the AppTracker with user data
        """
        self.users = [create_user_instance(user) for user in user_data]

    def simulate_day(self, business_date: date) -> None:
        """
        Simulate the connections and food consumption for each user for a day
        """
        food_processed = "sensor_api/data/food_processed.XLSX"
        aliments_df = pd.read_excel(food_processed)

        # Ensure reproducibility of measurements
        np.random.seed(seed=business_date.toordinal())
        # Find out which day the business_date corresponds to: Monday = 0, Sunday = 6
        # week_day = business_date.weekday()
        for user in self.users:
            user.get_daily_activity(business_date, aliments_df)

    """
    def get_user_activity(self, user_id: int, business_date: date, aliments_df) -> dict:

        Get the activity log for a specific user on a specific date



        # Ensure reproducibility of measurements

        user = next((u for u in self.users if u.user_id == user_id), None)
        if user:
            return user.get_daily_activity(business_date, aliments_df)
        return {}
    """

    def get_connexion(self, meal_id: int, business_date: date, user_id=int) -> dict:
        """Return the traffic for one sensor at a date"""
        food_processed = "food_processed.XLSX"
        aliments_df = pd.read_excel(food_processed)
        user = next((u for u in self.users if u.user_id == user_id), None)
        connexion_day = dict()
        connexion = None if user is None else user.get_daily_activity(user_id, business_date, aliments_df)

        print(f"User: {user}")
        print(f"Connexion: {connexion}")

        # Convertir business_date en objet date si c'est une chaîne
        if isinstance(business_date, str):
            business_date = datetime.strptime(business_date, '%Y-%m-%d').date()

        if connexion:
            for i in range(len(connexion['meal_id'])):
                heure_repas_date = datetime.strptime(connexion['heure_repas'][i], '%Y-%m-%d %H:%M:%S').date()
                #print(
                #    f"Checking entry {i}: meal_id={connexion['meal_id'][i]}, "
                #    f"heure_repas_date={heure_repas_date} de type {type(heure_repas_date)}, "
                #    f"user_id={connexion['user_id'][i]}, business date = {business_date} de type {type(business_date)}")

                condition_meal_id = (connexion['meal_id'][i] == meal_id)
                condition_date = (heure_repas_date == business_date)
                condition_user_id = (connexion['user_id'][i] == user_id)

                #print(f"Condition meal_id: {condition_meal_id}")
                #print(f"Condition date: {condition_date}")
                #print(f"Condition user_id: {condition_user_id}")

                if condition_meal_id and condition_date and condition_user_id:
                    for key in connexion.keys():
                        if key not in connexion_day:
                            connexion_day[key] = []
                        connexion_day[key].append(connexion[key][i])

        #print(f"Filtered connexion_day: {connexion_day}")

        return connexion_day

    def get_all_connexion(self, user_id: int, business_date: date, aliments_df=pd.DataFrame) -> dict:
        """Return the traffic for all sensors of the store at a date"""
        food_processed = "food_processed.XLSX"
        aliments_df = pd.read_excel(food_processed)
        user = next((u for u in self.users if u.user_id == user_id), None)
        connexion_day = None if user is None else user.simulate_daily_activity(business_date, aliments_df)
        return connexion_day
