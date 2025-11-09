import requests
import datetime
import time
import csv

API_KEY = "6a561fe685f1900e3a75446828bb620d3df5ef54f981d4ddde85f539360fea54"
BASE_URL = "https://data-api.coindesk.com/index/cc/v1/historical/days?market=cadli&instrument=BTC-USD&limit=30&aggregate=1&fill=true&apply_mapping=true&response_format=JSON"
CHUNK_DAYS = 365  

def fetch_data(instrument, end_date, retries=3):
    """Fetch daily data for a given instrument ending at end_date with retry support."""
    params = {
        "market": "cadli",
        "instrument": instrument,
        "limit": 2000,
        "aggregate": 1,
        "fill": "true",
        "apply_mapping": "true",
        "response_format": "JSON",
        "api_key": API_KEY,
        "to_ts": int(end_date.timestamp())
    }
    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL, params=params,
                                    headers={"Content-type": "application/json; charset=UTF-8"},
                                    timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Attempt {attempt+1} failed for {instrument}: {e}")
            time.sleep(2)
    print(f"Failed to fetch data for {instrument} ending {end_date.date()} after {retries} attempts")
    return {"Data": []}

def get_all_daily_data(instrument, start_date):
    """Loop to get all daily data for an instrument from start_date → now in safe chunks."""
    all_data = []
    now = datetime.datetime.now()
    while start_date < now:
        end_date = min(start_date + datetime.timedelta(days=CHUNK_DAYS), now)
        print(f"[{instrument}] Fetching {start_date.date()} → {end_date.date()}")
        data = fetch_data(instrument, end_date)
        if "Data" in data and data["Data"]:
            all_data.extend(data["Data"])
        else:
            print(f"No data returned for {instrument} in {start_date.date()} → {end_date.date()}")
        start_date = end_date + datetime.timedelta(days=1)
        time.sleep(1)  # avoid hitting rate limits
    return all_data

def save_to_csv(data, instrument):
    """Save fetched data to CSV."""
    if not data:
        print(f"No data to save for {instrument}")
        return
    all_keys = sorted({key for row in data for key in row.keys()})
    filename = f"{instrument}_daily.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {instrument} daily data to {filename}: {len(data)} rows, {len(all_keys)} columns")

def process_instrument(name, start_date):
    print(f"\n=== Fetching DAILY data for {name} starting {start_date.date()} ===")
    data = get_all_daily_data(name, start_date)
    save_to_csv(data, name)

def main():
    instruments = [
        ("BTC-INR", datetime.datetime(2009, 1, 3)),
        ("ETH-INR", datetime.datetime(2015, 8, 7)),
        ("BNB-INR", datetime.datetime(2017, 7, 25)),
        ("SOL-INR", datetime.datetime(2020, 3, 20)),
        ("DOT-INR", datetime.datetime(2020, 5, 26)),
        ("XRP-INR", datetime.datetime(2012, 5, 1)),
        ("TRX-INR", datetime.datetime(2017, 9, 13)),
        ("DOGE-INR", datetime.datetime(2013, 12, 6)),
    ]

    for instrument, start_date in instruments:
        process_instrument(instrument, start_date)

if __name__ == "__main__":
    main()