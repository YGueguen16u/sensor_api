import sys
import os


# Ajouter le répertoire racine du projet au sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
print(f"Adding {project_root} to sys.path")
sys.path.append(project_root)

print(f"sys.path: {sys.path}")

# Vérifiez le contenu du répertoire pour s'assurer que les modules sont là
for root, dirs, files in os.walk(os.path.abspath(os.path.dirname(__file__))):
    print(root, dirs, files)

from data_engineering.sensor_api.fake_data.app_tracker import AppTracker

from datetime import date
import pandas as pd


def create_users_from_excel(file_path: str) -> list:
    """
    Create user instances from an Excel file
    """
    user_data = pd.read_excel(file_path)
    users = []
    
    for _, row in user_data.iterrows():
        users.append({
            'nom': row['l_name'],
            'prenom': row['f_name'],
            'age': row['age'],
            'sexe': row['sexe'],
            'user_id': row['user_id'],
            'classe_mangeur': row['classe']
        })
    
    return users

def create_app() -> AppTracker:
    """
    Create an instance of AppTracker with the given users
    """
    file_path = r"C:\Users\GUEGUEN\Desktop\WSApp\IM\data_engineering\sensor_api\data\user\user_table.XLSX"
    users = create_users_from_excel(file_path)
    app_tracker = AppTracker(users)
    return app_tracker

