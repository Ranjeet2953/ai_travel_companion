import requests

# Fetch weather data using Weatherstack API
def get_weather(city, api_key):
    url = f"http://api.weatherstack.com/current?access_key={api_key}&query={city}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "current" in data:
            return {
                "temperature": data["current"]["temperature"],
                "weather": data["current"]["weather_descriptions"][0],
                "icon": data["current"]["weather_icons"][0],
                "lat": data["location"]["lat"],
                "lng": data["location"]["lon"],
            }
        return {"error": "Weather data not found for the city."}
    return {"error": f"Failed to fetch weather data. Status code: {response.status_code}"}

# Geocode a city using Positionstack API
def geocode_address(address, api_key):
    url = "http://api.positionstack.com/v1/forward"
    params = {"access_key": api_key, "query": address}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            location = data["data"][0]
            return {"lat": location["latitude"], "lng": location["longitude"]}
        return {"error": "Unable to find coordinates for the given city."}
    return {"error": f"Failed to fetch geocode data. Status code: {response.status_code}"}

# Fetch nearby places using OpenStreetMap's Overpass API
def get_places(location, place_type, api_key):
    url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="{place_type}"](around:5000,{location['lat']},{location['lng']});
      way["amenity"="{place_type}"](around:5000,{location['lat']},{location['lng']});
      relation["amenity"="{place_type}"](around:5000,{location['lat']},{location['lng']});
    );
    out body;
    """
    response = requests.get(url, params={"data": query})
    if response.status_code == 200:
        places = response.json().get("elements", [])
        return [{"name": place.get("tags", {}).get("name", "Unnamed"), "address": "Nearby"} for place in places]
    return {"error": "No places found or failed to fetch places data."}

# Generate an itinerary
def generate_itinerary(city, preferences, weather_data, positionstack_api_key, weatherstack_api_key):
    location = geocode_address(city, positionstack_api_key)
    if "error" in location:
        return {"error": location["error"]}

    itinerary = []

    # Weather-based suggestion
    if weather_data["weather"].lower() in ["rain", "snow"]:
        for preference in preferences.get("indoor", ["museum", "cafe"]):
            places = get_places(location, preference, positionstack_api_key)
            itinerary.extend(places)
    else:
        for preference in preferences.get("outdoor", ["park", "beach", "hill station", "lake", "fort"]):
            places = get_places(location, preference, positionstack_api_key)
            itinerary.extend(places)

    # Add cafes explicitly
    cafes = get_places(location, "cafe", positionstack_api_key)
    itinerary.extend(cafes[:5])

    return itinerary
