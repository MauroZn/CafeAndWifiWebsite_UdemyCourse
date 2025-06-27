import requests
import time
from main import app, db, Cafe

def get_coordinates(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "CafeMapApp/1.0 (pigna933@gmail.com)"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None

with app.app_context():
    cafes = Cafe.query.all()
    for cafe in cafes:
        if cafe.latitude is None or cafe.longitude is None:
            query = f"{cafe.name}, {cafe.location}"
            lat, lon = get_coordinates(query)
            if lat and lon:
                cafe.latitude = lat
                cafe.longitude = lon
                db.session.commit()
                print(f"Updated {cafe.name} → ({lat}, {lon})")
            else:
                print(f"Could not geocode: {query}")
            time.sleep(1)
