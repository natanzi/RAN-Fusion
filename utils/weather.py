import requests
from traffic.network_metrics import calculate_signal_strength

# Function to fetch weather data from OpenWeatherMap API
def fetch_weather(api_key, latitude, longitude):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': api_key
    }
    response = requests.get(base_url, params=params)
    return response.json()

# Function to adjust signal strength based on weather
def weather_adjusted_signal_strength(ue, gNodeB, api_key):
    weather_data = fetch_weather(api_key, gNodeB.Latitude, gNodeB.Longitude)
    weather_condition = weather_data['weather'][0]['main']

    # Placeholder for actual weather impact calculation
    # You would replace this with a more sophisticated model based on research
    weather_impact_factor = {
        'Clear': 1.0,
        'Clouds': 0.9,
        'Rain': 0.8,
        'Fog': 0.7,
        'Snow': 0.6,
        'Thunderstorm': 0.5
    }.get(weather_condition, 1.0)

    # Calculate the original signal strength
    original_signal_strength = calculate_signal_strength(ue, gNodeB)

    # Adjust the signal strength based on weather impact
    adjusted_signal_strength = original_signal_strength * weather_impact_factor

    return adjusted_signal_strength

# Example usage:
# api_key = 'your_openweathermap_api_key'
# adjusted_strength = weather_adjusted_signal_strength(ue_instance, gNodeB_instance, api_key)