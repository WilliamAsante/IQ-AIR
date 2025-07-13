import os
import requests
import csv
from datetime import datetime

CITY = "Tarkwa"
STATE = "Western"
COUNTRY = "Ghana"
CSV_FILENAME = "tarkwa_air_quality_history.csv"

CSV_HEADER = [
    "collection_timestamp_utc", "pollution_timestamp_utc", "aqi_us",
    "main_pollutant_us", "temperature_celsius", "humidity_percent",
    "wind_speed_m_s", "wind_direction_degrees", "weather_icon_code"
]

def main():
    print(f"--- Running data collection for {CITY}, {COUNTRY} at {datetime.utcnow().isoformat()} UTC ---")

    api_key = os.getenv('AIRVISUAL_API_KEY')
    if not api_key:
        print("FATAL ERROR: AIRVISUAL_API_KEY environment variable not set.")
        return

    api_url = f"http://api.airvisual.com/v2/city?city={CITY}&state={STATE}&country={COUNTRY}&key={api_key}"
    print(f"Requesting data from API...")

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('status') != 'success':
            message = data.get('data', {}).get('message', 'Unknown error')
            print(f"API returned a non-success status: {message}")
            return

        current_data = data.get('data', {}).get('current', {})
        pollution = current_data.get('pollution', {})
        weather = current_data.get('weather', {})

        if not current_data or not pollution or not weather:
            print("ERROR: Could not find 'current', 'pollution', or 'weather' data.")
            return
            
        data_row = [
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), pollution.get('ts'),
            pollution.get('aqius'), pollution.get('mainus'), weather.get('tp'),
            weather.get('hu'), weather.get('ws'), weather.get('wd'), weather.get('ic')
        ]

        file_exists = os.path.exists(CSV_FILENAME)
        with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(CSV_HEADER)
                print(f"'{CSV_FILENAME}' not found. Created file and wrote headers.")
            writer.writerow(data_row)
        print(f"Successfully collected and saved data: {data_row}")

    except requests.exceptions.RequestException as e:
        print(f"Network or HTTP error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("--- Script finished ---")

if __name__ == "__main__":
    main()
