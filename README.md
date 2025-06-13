# Sensor API - Food Tracking Data Generation

A simulation API for food tracking that generates realistic data based on different user profiles.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YGueguen16u/sensor_api
cd sensor_api
```

2. Create a Python virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
sensor_api/
├── app.py                  # API entry point
├── requirements.txt        # Project dependencies
├── fake_data/             # Data generation module
│   ├── __init__.py        # Initialization and instance creation
│   ├── app_tracker.py     # Meal tracking management
│   ├── sensor.py          # User type classes
│   └── *.XLSX            # Data files for each profile
├── tests/                 # Unit tests
└── data/                  # Data folder
```

## Usage

1. Start the server:
```bash
uvicorn app:app --reload
```

2. Access the API:
- Base URL: `http://localhost:8000`
- Swagger Documentation: `http://localhost:8000/docs`

### Request Example

```bash
curl "http://localhost:8000/?user_id=4&year=2024&month=07&day=18&meal_id=1"
```

## User Types

1. **Standard**: 4 meals/day (300-800 cal/meal)
2. **MeatLover**: Meat enthusiast (400-900 cal/meal)
3. **Vegetarian**: Plant-based with dairy (300-700 cal/meal)
4. **Vegan**: Strictly plant-based (250-700 cal/meal)
5. **Fasting**: Intermittent fasting (2 meals/day, 800-1200 cal/meal)
6. **Random**: Random eating pattern (1 meal/day, 900-4500 cal)

## Constraints

- Data available only from 2024 onwards
- No future data available
- Number of meals varies by user profile
- Caloric factor based on gender (1.2 for male)

## Testing

Run the tests:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
