import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import random
import openpyxl
import os

# Path to the directory containing this script
current_dir = os.path.abspath(os.path.dirname(__file__))

# Base User class
class User:
    """
    Class User
    """

    def __init__(self,
                 nom: str,
                 prenom: str,
                 age: int,
                 sexe: str,
                 user_id: int,
                 classe_mangeur: str,
                 type_food: str,
                 ) -> None:
        """
        Initialize a user with their attributes
        """
        self.nom = nom
        self.prenom = prenom
        self.age = age
        self.sexe = sexe
        self.user_id = user_id
        self.classe_mangeur = classe_mangeur
        self.facteur_calories = 1.2 if sexe == 'homme' else 1.0
        self.heures_repas = {}
        self.intervalles_calories = {}
        self.type_food_file = type_food  # Replace with actual path
        self.probabilites_df = pd.read_excel(self.type_food_file)
        self.aliments_consomme = []

    def __repr__(self):
        return (f"User(nom={self.nom}, prenom={self.prenom}, age={self.age}, sexe={self.sexe}, "
                f"user_id={self.user_id}, classe_mangeur={self.classe_mangeur})")

    def generer_heures_connexion(self, business_date=date):
        """
        Generate connection times for each meal with random variation.

        For each meal defined in `self.heures_repas`, this method generates a connection time
        with random variation around the scheduled time. If the eater class is 'random',
        the variation can range from -60 to +300 minutes. Otherwise, variation is limited to -60 to +60 minutes.

        Returns:
            list of tuple: A list of tuples where each tuple contains the meal number and the varied connection time.
                        Example: [(1, datetime), (2, datetime), ...]
        """
        random.seed(business_date.toordinal() + self.user_id)  # Seed based on date and user_id for reproducibility
        heures_de_connexion = []
        for repas, heure in self.heures_repas.items():
            heure_reelle = datetime.combine(business_date, datetime.strptime(heure, '%H:%M').time())
            if self.classe_mangeur == 'random':
                variation = timedelta(minutes=random.randint(-60, 300))
            else:
                variation = timedelta(minutes=random.randint(-60, 60))
            heure_variee = heure_reelle + variation
            heures_de_connexion.append((repas, heure_variee))
        return heures_de_connexion

    def choisir_types_aliments(self, repas):
        """
        Choose food types to consume for a given meal based on probabilities.

        Uses meal-specific columns for means and standard deviations to generate
        probabilities and randomly select food types based on these probabilities.

        Args:
            repas (int): The meal number (1 for breakfast, 2 for lunch, etc.)

        Returns:
            np.ndarray: An array of chosen food types.
        """
        repas_col_avg = f'Meal_{repas}_avg'
        repas_col_std = f'Meal_{repas}_std'

        types = self.probabilites_df['Types']
        moyennes = self.probabilites_df[repas_col_avg]
        std_devs = self.probabilites_df[repas_col_std]

        probabilites = np.random.normal(moyennes, std_devs)
        probabilites = np.clip(probabilites, 0, None)  # Ensure probabilities are not negative

        total_probabilite = np.sum(probabilites)
        if total_probabilite > 0:
            probabilites = probabilites / total_probabilite  # Normalize so probabilities sum to 1

        types_choisis = np.random.choice(types, size=len(types), p=probabilites)
        return types_choisis

    def determiner_quantite(self, type_aliment):
        """
        Determine the quantity of a food item based on its type and the eater class.

        Returns:
            int: The quantity of food.
        """
        # 5% chance that the quantity is zero
        if random.random() < 0.04:
            return 0
        elif random.random() > 0.9999:
            return random.randint(100, 1000)

        quantite = 1  # Default quantity

        if self.classe_mangeur == 'meat_lover':
            if type_aliment in ['Viande', 'Poisson', 'Oeuf'] and random.random() < 0.30:
                quantite = random.randint(2, 5)
        elif self.classe_mangeur in ['vegan', 'vegetarian']:
            if type_aliment in ['Légumes', 'Fruit', 'Légumineuse'] and random.random() < 0.30:
                quantite = random.randint(2, 5)
        elif self.classe_mangeur == 'standard':
            if type_aliment in ['viande', 'poisson', 'oeuf', 'Légumes', 'Fruit',
                                'Légumineuse'] and random.random() < 0.30:
                quantite = random.randint(2, 5)
        elif self.classe_mangeur == 'random':
            if random.random() < 0.30:
                quantite = random.randint(2, 5)

        return quantite

    def selectionner_aliments(self, aliments_df, types_choisis, repas, min_calories, max_calories):
        """
        Select foods to consume based on chosen types and caloric constraints.

        Foods are randomly chosen from the selected types until the minimum calorie
        requirement is met. If total calories exceed the maximum allowed,
        foods are removed based on their probability.

        Args:
            aliments_df (pd.DataFrame): DataFrame containing food information.
            types_choisis (np.ndarray): Food types chosen for the meal.
            repas (int): Meal number (1 for breakfast, 2 for lunch, etc.)
            min_calories (float): Minimum calories to consume for this meal.
            max_calories (float): Maximum calories to consume for this meal.

        Returns:
            list of dict: A list of dictionaries representing selected foods.
        """
        min_calories *= self.facteur_calories
        max_calories *= self.facteur_calories
        total_calories = 0
        aliments_selectionnes = []

        exceed_max_calories = random.random() < 0.2  # 20% chance to exceed max_calories

        for type_aliment in types_choisis:
            aliments_du_type = aliments_df[aliments_df['Type'] == type_aliment]
            aliment_choisi = aliments_du_type.sample(n=1).iloc[0].to_dict()
            aliment_choisi['Repas'] = repas

            # Determine the quantity of the food
            quantite = self.determiner_quantite(type_aliment)
            aliment_choisi['Quantite'] = quantite
            if quantite >= 10:
                exceed_max_calories = 1
            total_calories += aliment_choisi['Valeur calorique'] * quantite
            aliments_selectionnes.append(aliment_choisi)

            if total_calories >= min_calories and (exceed_max_calories or total_calories <= max_calories):
                break

        # If the total exceeds max_calories and exceed_max_calories is False, remove foods with the lowest probabilities
        if not exceed_max_calories and total_calories > max_calories:
            while total_calories > max_calories:
                aliments_selectionnes.sort(key=lambda x: self.probabilite_aliment(x['Type'], x['Repas']))
                aliment_a_retirer = aliments_selectionnes.pop(0)
                total_calories -= aliment_a_retirer['Valeur calorique'] * aliment_a_retirer['Quantite']

        return aliments_selectionnes

    def probabilite_aliment(self, type_aliment, repas):
        """
        Get the average probability of a food type for a specific meal.

        Args:
            type_aliment (str): The food type to get the probability for.
            repas (int): Meal number (1 for breakfast, 2 for lunch, etc.)

        Returns:
            float: The average probability of the food for the given meal.
        """
        repas_col_avg = f'Meal_{repas}_avg'
        moyenne = self.probabilites_df[self.probabilites_df['Types'] == type_aliment][repas_col_avg].values[0]
        return moyenne

    def simulate_daily_activity(self, user_id, business_date: date, aliments_df: pd.DataFrame):
        """
        Simulate daily eating activities of the user for a given date.

        Generates connection times, chooses food types for each meal and selects
        consumed foods based on probabilities and caloric constraints.

        Args:
            business_date: The current date
            user_id: user id
            aliments_df (pd.DataFrame): DataFrame containing food information.
        """
        np.random.seed(seed=business_date.toordinal() + user_id)  # Seed for reproducibility
        random.seed(business_date.toordinal() + user_id)  # Also set the random seed

        heures_de_connexion = self.generer_heures_connexion(business_date)
        self.aliments_consomme = []
        aliments_logs = []

        for repas, heure in heures_de_connexion:
            types_choisis = self.choisir_types_aliments(repas)
            aliments_selectionnes = self.selectionner_aliments(
                aliments_df,
                types_choisis,
                repas,
                self.intervalles_calories[repas][0],
                self.intervalles_calories[repas][1]
            )
            self.aliments_consomme.extend(aliments_selectionnes)

            for aliment in aliments_selectionnes:
                quantity = aliment.get('Quantite', 1)
                aliments_logs.append({
                    'user_id': user_id,
                    'meal_id': repas,
                    'heure_repas': heure.strftime('%Y-%m-%d %H:%M:%S'),
                    'aliment_id': aliment['id'],
                    'quantity': quantity,
                })

        food_per_meal = pd.DataFrame(aliments_logs)

        # Fusionner avec repas_df pour ajouter la colonne total_calorique
        return food_per_meal

    def get_daily_activity(self, user_id, business_date: date, aliments_df: pd.DataFrame) -> dict:
        """
        Récupère le journal d'activité alimentaire de l'utilisateur pour une date spécifique.

        Args:
            user_id: user id
            aliments_df: Table des aliments
            business_date (date): La date pour laquelle récupérer le journal d'activité.

        Returns:
            dict: Un dictionnaire contenant la date et la liste des aliments consommés.
        """

        # Si business_date est une chaîne, convertissez-la en date
        if isinstance(business_date, str):
            business_date = datetime.strptime(business_date, "%Y-%m-%d").date()

        np.random.seed(seed=business_date.toordinal())
        random.seed(business_date.toordinal() + user_id)  # Seed for reproducibility

        food_per_meal = self.simulate_daily_activity(user_id, business_date, aliments_df)

        keys = ['user_id', 'meal_id', 'heure_repas', 'aliment_id', 'quantity']

        connexion_day = {key: [] for key in keys}

        for index, row in food_per_meal.iterrows():
            for key in keys:
                connexion_day[key].append(row[key])
            #connexion_day['date'].append(business_date.strftime("%Y-%m-%d"))  # Ajouter la date pour chaque entrée

        return connexion_day


# Sous-classe pour les mangeurs standard
class Standard(User):
    """
    Class representing a standard eater.

    Inherits from User class and initializes specific attributes for a standard eater,
    including meal times and calorie ranges for each meal.

    Args:
        nom (str): User's last name.
        prenom (str): User's first name.
        age (int): User's age.
        sexe (str): User's gender ('homme' or 'femme').
        user_id (int): User's unique identifier.
    """

    def __init__(self, nom, prenom, age, sexe, user_id):
        type_food_file = "standard_class.XLSX"
        super().__init__(nom, prenom, age, sexe, user_id, 'standard', type_food_file)
        self.heures_repas = {
            1: '08:00',  # breakfast
            2: '12:00',  # lunch
            3: '16:00',  # snack
            4: '20:00'  # dinner
        }
        self.intervalles_calories = {
            1: (300, 500),  # breakfast
            2: (600, 800),  # lunch
            3: (200, 300),  # snack
            4: (500, 700)  # dinner
        }


# Classe MangeurStandard héritant de Mangeur
class MeatLover(User):
    """
    Class representing a meat lover eater.

    Inherits from User class and initializes specific attributes for a meat lover,
    including meal times and calorie ranges for each meal.

    Args:
        nom (str): User's last name.
        prenom (str): User's first name.
        age (int): User's age.
        sexe (str): User's gender ('homme' or 'femme').
        user_id (int): User's unique identifier.
    """

    def __init__(self, nom, prenom, age, sexe, user_id):
        type_food_file = "meat_lover_class.XLSX"
        super().__init__(nom, prenom, age, sexe, user_id, 'meat_lover', type_food_file)
        self.heures_repas = {
            1: '08:00',  # breakfast
            2: '12:00',  # lunch
            3: '16:00',  # snack
            4: '20:00'  # dinner
        }
        self.intervalles_calories = {
            1: (400, 600),  # breakfast
            2: (700, 900),  # lunch
            3: (300, 500),  # snack
            4: (600, 800)  # dinner
        }


class Vegetarian(User):
    """
    Class representing a vegetarian eater.

    Inherits from User class and initializes specific attributes for a vegetarian,
    including meal times and calorie ranges for each meal.

    Args:
        nom (str): User's last name.
        prenom (str): User's first name.
        age (int): User's age.
        sexe (str): User's gender ('homme' or 'femme').
        user_id (int): User's unique identifier.
    """

    def __init__(self, nom, prenom, age, sexe, user_id):
        type_food_file = "vegetarian_class.XLSX"
        super().__init__(nom, prenom, age, sexe, user_id, 'vegetarian', type_food_file)
        self.heures_repas = {
            1: '08:00',  # breakfast
            2: '12:00',  # lunch
            3: '16:00',  # snack
            4: '20:00'  # dinner
        }
        self.intervalles_calories = {
            1: (300, 400),  # breakfast
            2: (500, 700),  # lunch
            3: (100, 200),  # snack
            4: (450, 600)  # dinner
        }


class Vegan(User):
    """
    Class representing a vegan eater.

    Inherits from User class and initializes specific attributes for a vegan,
    including meal times and calorie ranges for each meal.

    Args:
        nom (str): User's last name.
        prenom (str): User's first name.
        age (int): User's age.
        sexe (str): User's gender ('homme' or 'femme').
        user_id (int): User's unique identifier.
    """

    def __init__(self, nom, prenom, age, sexe, user_id):
        type_food_file = "vegan_class.XLSX"
        super().__init__(nom, prenom, age, sexe, user_id, 'vegan', type_food_file)
        self.heures_repas = {
            1: '08:00',  # breakfast
            2: '12:00',  # lunch
            3: '16:00',  # snack
            4: '20:00'  # dinner
        }
        self.intervalles_calories = {
            1: (250, 350),  # breakfast
            2: (500, 700),  # lunch
            3: (100, 200),  # snack
            4: (400, 500)  # dinner
        }


class Fasting(User):
    """
    Class representing an intermittent fasting eater.

    Inherits from User class and initializes specific attributes for a fasting eater,
    including meal times and calorie ranges for each meal.

    Args:
        nom (str): User's last name.
        prenom (str): User's first name.
        age (int): User's age.
        sexe (str): User's gender ('homme' or 'femme').
        user_id (int): User's unique identifier.
    """

    def __init__(self, nom, prenom, age, sexe, user_id):
        type_food_file = "fasting_class.XLSX"
        super().__init__(nom, prenom, age, sexe, user_id, 'fasting', type_food_file)
        self.heures_repas = {
            1: '12:00',  # lunch
            2: '18:00',  # dinner
        }
        self.intervalles_calories = {
            1: (1000, 1200),  # lunch
            2: (800, 1000)  # dinner
        }


class Random(User):
    """
    Class representing a random eater.

    Inherits from User class and initializes specific attributes for a random eater,
    including meal times and calorie ranges for each meal.

    Args:
        nom (str): User's last name.
        prenom (str): User's first name.
        age (int): User's age.
        sexe (str): User's gender ('homme' or 'femme').
        user_id (int): User's unique identifier.
    """

    def __init__(self, nom, prenom, age, sexe, user_id):
        type_food_file = "random_eater_class.XLSX"
        super().__init__(nom, prenom, age, sexe, user_id, 'random', type_food_file)
        self.heures_repas = {
            1: '13:00',
        }
        self.intervalles_calories = {
            1: (900, 4500),  # breakfast
        }


# Création d'une instance utilisateur en fonction de la classe de mangeur
def create_user_instance(user_data: dict) -> User:
    """
    Create a user instance based on provided data and eater class.

    This function creates an instance of the appropriate user class (`Standard`, `MeatLover`,
    `Vegetarian`, `Vegan`, `Fasting`, or `Random`) based on the eater class specified in
    `user_data`. If the specified eater class is not found, it returns a base `User` instance.

    Args:
        user_data (dict): A dictionary containing user information, including
                          the 'classe_mangeur' key that specifies the user's eater class.

    Returns:
        User: An instance of the appropriate eater class or a base `User` instance.
    """
    classes_mangeurs = {
        'standard': Standard,
        'meat_lover': MeatLover,
        'vegetarian': Vegetarian,
        'vegan': Vegan,
        'fasting': Fasting,
        'random': Random
    }
    classe_mangeur = user_data.pop('classe_mangeur')
    user_class = classes_mangeurs.get(classe_mangeur, User)
    return user_class(**user_data)
