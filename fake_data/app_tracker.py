from typing import Tuple, Any

import pandas as pd
import numpy as np
from datetime import date
#from data_engineering.sensor_api.fake_data.sensor import create_user_instance
from data_engineering.sensor_api.fake_data.sensor import create_user_instance
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
        food_processed = r"sensor_api\data\food_processed.XLSX"
        aliments_df = pd.read_excel(food_processed)

        # Ensure reproducibility of measurements
        np.random.seed(seed=business_date.toordinal())
        # Find out which day the business_date corresponds to: Monday = 0, Sunday = 6
        week_day = business_date.weekday()
        for user in self.users:
            user.simulate_daily_activity(business_date, aliments_df)

    """
    def get_user_activity(self, user_id: int, business_date: date, aliments_df) -> dict:

        Get the activity log for a specific user on a specific date



        # Ensure reproducibility of measurements

        user = next((u for u in self.users if u.user_id == user_id), None)
        if user:
            return user.get_daily_activity(business_date, aliments_df)
        return {}
    """
    def get_connexion(self, meal_id: int, business_date: date, aliments_df= pd.DataFrame, nom=str) -> tuple[Any, Any]:
        """Return the traffic for one sensor at a date"""
        user = next((u for u in self.users if u.nom == nom), None)
        if user:
            connexion_day = user.get_daily_activity(business_date, aliments_df)
        return connexion_day['date'], connexion_day[meal_id]

    def get_all_connexion(self, business_date: date, aliments_df=pd.DataFrame, nom=str) -> int:
        """Return the traffic for all sensors of the store at a date"""
        user = next((u for u in self.users if u.nom == nom), None)
        if user:
            connexion_day = user.get_daily_activity(business_date, aliments_df)
        return connexion_day
