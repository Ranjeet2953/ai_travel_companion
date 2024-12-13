from flask import Flask, render_template, request
from backend import get_weather, generate_itinerary

app = Flask(__name__)

# API Keys
weatherstack_api_key = "1433886070c0b484145828694c0ffbe8"
google_api_key = "5b97650ff70d7e9fad9d7aa77f8b9784"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/itinerary", methods=["POST"])
def itinerary():
    city = request.form.get("city")
    preferences = request.form.getlist("preferences")

    if not city:
        return render_template("results.html", error="City name cannot be empty.")

    # Fetch weather data
    weather_data = get_weather(city, weatherstack_api_key)
    if "error" in weather_data:
        return render_template("results.html", error=weather_data["error"])

    # Generate itinerary with various preferences
    itinerary = generate_itinerary(
        city,
        {"indoor": preferences, "outdoor": preferences},
        weather_data,
        google_api_key,
        weatherstack_api_key
    )

    if "error" in itinerary:
        return render_template("results.html", error=itinerary["error"])

    return render_template("results.html", city=city, weather=weather_data, itinerary=itinerary)

if __name__ == "__main__":
    app.run(debug=True)
