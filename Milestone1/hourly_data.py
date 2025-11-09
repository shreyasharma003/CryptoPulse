import requests
import datetime
import time
import csv

API_KEY = "6a561fe685f1900e3a75446828bb620d3df5ef54f981d4ddde85f539360fea54"
BASE_URL = "https://data-api.coindesk.com/index/cc/v1/historical/hours"

def fetch_data(instrument, end_date):
    """Fetch hourly data for given instrument ending at end_date"""
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
    try:
        response = requests.get(BASE_URL, params=params, headers={"Content-type": "application/json; charset=UTF-8"})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"⚠ No data for {instrument} at {end_date}: {e}")
        return {}

def get_all_hourly_data(instrument, start_date):
    """Loop to get all hourly data for given instrument from start_date → now"""
    all_data = []
    now = datetime.datetime.now()

    while start_date < now:
        end_date = start_date + datetime.timedelta(hours=2000)
        if end_date > now:
            end_date = now

        print(f"[{instrument}] Fetching {start_date} → {end_date}")
        data = fetch_data(instrument, end_date)

        if "Data" in data:
            all_data.extend(data["Data"])
        else:
            print(f"No data returned for {instrument} in this range")

        start_date = end_date + datetime.timedelta(hours=1)
        time.sleep(1)

    return all_data

def save_to_csv(data, instrument):
    if not data:
        print(f"No data to save for {instrument}")
        return

    all_keys = sorted({key for row in data for key in row.keys()})

    filename = f"{instrument}_hourly.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved {instrument} hourly data to {filename} "
          f"with {len(data)} rows and {len(all_keys)} columns")

def main():
    instruments = [
        
        ("BTC-INR", datetime.datetime(2016, 1, 1)),   # reliable BTC hourly data
        ("ETH-INR", datetime.datetime(2017, 1, 1)),   # Ethereum
        ("BNB-INR", datetime.datetime(2018, 1, 1)),   # Binance Coin
        ("SOL-INR", datetime.datetime(2021, 1, 1)),   # Solana
        ("DOT-INR", datetime.datetime(2021, 1, 1)),   # Polkadot
        ("XRP-INR", datetime.datetime(2017, 1, 1)),   # Ripple
        ("TRX-INR", datetime.datetime(2018, 1, 1)),   # Tron
        ("DOGE-INR", datetime.datetime(2017, 1, 1)),  # Dogecoin
    ]

    for instrument, start_date in instruments:
        print(f"\n=== Fetching HOURLY data for {instrument} starting {start_date.date()} ===")
        data = get_all_hourly_data(instrument, start_date)
        save_to_csv(data, instrument)

if __name__ == "__main__":
    main()