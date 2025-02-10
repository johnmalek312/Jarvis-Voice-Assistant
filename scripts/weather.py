from tool_registry import register_tool
from .data_manager import DataManager as dm
import requests
import datetime

@register_tool()
def get_user_location() -> str:
    """Get the user's location. Returns location data as a string."""
    try:
        user_location = dm.user.get('location', {})
        city = user_location.get('city')
        state = user_location.get('state')
        country = user_location.get('country')
        return f"City: {city}, State: {state}, Country: {country}"
    except Exception as e:
        return "Error while getting user location: " + str(e)
@register_tool()
def get_place_id(city: str, country: str = "") -> str:
    """Gets the place id for a specific city in a specific country. If no country is provided, it will use the user country. if the city is not in the country, it will return most likely referred city."""
    try:
        parameters = {'key': dm.meteosource['api_key'], 'text': city}
        url = "https://www.meteosource.com/api/v1/free/find_places"
        data = requests.get(url, parameters).json() # this will return a list of places
        if not country:
            country = dm.user["location"]["country"]
        for place in data:
            if place['country'].lower() == country.lower():
                return place['place_id']
        return data[0]["place_id"]
    except Exception as e:
        return "Error while getting place ID: " + str(e)
@register_tool()
def get_weather(place_id: str = "") -> str:
    """Gets the current weather for a specific place id. If no place id is provided, it will use the user's location."""
    try:
        if not place_id:
            place_id = dm.user['location'].get('Place_id')
            if not place_id:
                place_id = get_place_id(dm.user['location']['city'])
                set_user_place_id(place_id)
        parameters = {'key': dm.meteosource['api_key'], 'place_id': place_id, 'section': 'current'}
        url = "https://www.meteosource.com/api/v1/free/point"
        data = requests.get(url, parameters).json()
        current = data["current"]
        return current
    except Exception as e:
        return "Error while getting weather: " + str(e)

@register_tool()
def get_weekly_forecast(place_id: str = "") -> list[dict]:
    """
    Retrieve a 7-day weather forecast (for today and the next 6 days) for a specified place_id. If place_id is not provided it uses user's location.

    Returns:
        list: Daily weather data containing temperature, wind, and cloud cover information.
            Returns empty list if request fails.
    Useful for retrieving weather forecasts instead of current weather data.
    Notes:
        - Data includes date, temperature (avg/min/max), wind, and cloud cover

    Use this function if you asked for future weather forecast.
    """
    try:
        if not place_id:
            place_id = dm.user['location'].get('Place_id')
            if not place_id:
                place_id = get_place_id(dm.user['location']['city'])
                set_user_place_id(place_id)
        parameters = {
            'key': dm.meteosource['api_key'],
            'place_id': place_id,
            'sections': 'daily'
        }
        response = requests.get('https://www.meteosource.com/api/v1/free/point', params=parameters)
        if response.status_code == 200:
            daily_data = response.json().get('daily', {}).get('data', [])
            today = datetime.datetime.today().date()
            for index, day in enumerate(daily_data):
                forecast_date = datetime.datetime.strptime(day['day'], "%Y-%m-%d").date()
                delta = (forecast_date - today).days
                if delta == 0:
                    day['day'] = "Today"
                elif delta == 1:
                    day['day'] = "Tomorrow"
                else:
                    day['day'] = f"In {delta} days"
                day.pop('morning', None)
                day.pop('afternoon', None)
                day.pop('evening', None)
                if 'all_day' in day:
                    day['all_day'].pop('precipitation', None)
            return daily_data
        else:
            raise Exception(f"Bad response from Meteosource API: {response.status_code}, {response.text}")
    except Exception as e:
        return "Error while fetching weekly forecast data: " + str(e)

def set_user_place_id(place_id: str) -> None:
    """Sets the user's place id."""
    user_location = dm.user['location']
    user_location['Place_id'] = place_id
    dm.save_data_cache('../scripts_data/general_data.json')