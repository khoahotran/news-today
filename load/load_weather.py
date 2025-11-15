from extract.weather_api import fetch_weather
from transform.transform_weather import transform_weather

if __name__ == "__main__":
    print("=== Running Weather ETL ===")
    fetch_weather()
    transform_weather()
    print("=== Done Weather ETL ===")