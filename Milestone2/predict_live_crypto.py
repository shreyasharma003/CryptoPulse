import os
import requests
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# =========================
# Supported Coins (8 only)
# =========================
symbol_map = {
    "BNB": "BNBUSDT",
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT",
    "XRP": "XRPUSDT",
    "DOGE": "DOGEUSDT",
    "DOT": "DOTUSDT",
    "TRX": "TRXUSDT"
}

# =========================
# Fetch Live Binance Data
# =========================
def get_live_data(symbol="BTC", interval="1h", limit=500):
    """
    Fetch OHLCV data from Binance API
    """
    pair = symbol_map.get(symbol.upper())
    if not pair:
        raise ValueError(f"Symbol {symbol} not supported.")

    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": pair, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception("Error fetching data from Binance API")

    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "qav", "num_trades", "taker_base_vol", "taker_quote_vol", "ignore"
    ])

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    return df


# =========================
# Predict Future Price
# =========================
def predict_future(symbol="BTC", days=0, hours=0):
    """
    Predicts future price of crypto after given days+hours.
    """
    symbol = symbol.upper()

    # Decide whether to use daily or hourly model
    if days > 0:
        duration = "daily"
        steps = days
    else:
        duration = "hourly"
        steps = hours

    # Load model
    model_filename = f"{symbol}-INR_{duration}.h5"
    model_path = os.path.join("crypto_models", model_filename)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_filename}")

    model = load_model(model_path)

    # Fetch live data
    interval = "1d" if duration == "daily" else "1h"
    df = get_live_data(symbol, interval=interval, limit=200)

    closes = df["close"].values.reshape(-1, 1)

    # Scale
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(closes)

    # Predict sequentially for required steps
    last_sequence = scaled[-60:]
    for _ in range(steps):
        X_input = last_sequence.reshape(1, 60, 1)
        pred_scaled = model.predict(X_input, verbose=0)
        pred_price = scaler.inverse_transform(pred_scaled)[0][0]

        # Append prediction back
        new_point = scaler.transform([[pred_price]])
        last_sequence = np.vstack([last_sequence[1:], new_point])

    # Extract last OHLC values
    now_price = df["close"].iloc[-1]
    high_price = df["high"].iloc[-1]
    low_price = df["low"].iloc[-1]

    direction = "UP" if pred_price > now_price else "DOWN"

    return {
        "symbol": symbol,
        "after": f"{days} days {hours} hours",
        "current_price": now_price,
        "predicted_price": pred_price,
        "high": high_price,
        "low": low_price,
        "direction": direction
    }


# =========================
# Run Predictions for All 8 Coins
# =========================
if __name__ == "__main__":
    coins = list(symbol_map.keys())

    # Example: predict 2 days 10 hours ahead for all 8 coins
    days, hours = 2, 10  

    for coin in coins:
        try:
            result = predict_future(coin, days=days, hours=hours)
            print(f"\n🔹 Predicted {result['symbol']} price after {result['after']}:")
            print(f"   Current:   {result['current_price']:.2f} USDT")
            print(f"   Predicted: {result['predicted_price']:.2f} USDT")
            print(f"   High:      {result['high']:.2f}, Low: {result['low']:.2f}")
            print(f"   Direction: {result['direction']}")
        except Exception as e:
            print(f"\n❌ Error for {coin}: {e}")
