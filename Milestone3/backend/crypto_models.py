# backend/crypto_model.py
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

    # Convert to float
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
    return df

# =========================
# Predict Future Price
# =========================
def predict_future(symbol="BTC", days=0, hours=0):
    symbol = symbol.upper()

    # Ensure days and hours are integers (important for JSON inputs)
    try:
        days = int(days)
        hours = int(hours)
    except ValueError:
        raise ValueError("Days and hours must be integers.")

    # Decide model type
    if days > 0:
        duration = "daily"
        steps = days
    elif hours > 0:
        duration = "hourly"
        steps = hours
    else:
        raise ValueError("Either days or hours must be greater than 0.")

    # Model path
    BASE_DIR = os.path.dirname(__file__)
    MODEL_DIR = os.path.join(BASE_DIR, "crypto_models")
    model_filename = f"{symbol}-INR_{duration}.h5"
    model_path = os.path.join(MODEL_DIR, model_filename)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    # Load model
    model = load_model(model_path)

    # Fetch live data
    interval = "1d" if duration == "daily" else "1h"
    df = get_live_data(symbol, interval=interval, limit=200)

    closes = df["close"].values.reshape(-1, 1)

    # Scale
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(closes)

    # Sequential prediction
    last_sequence = scaled[-60:]
    pred_price = None
    for _ in range(steps):
        X_input = last_sequence.reshape(1, 60, 1)
        pred_scaled = model.predict(X_input, verbose=0)
        pred_price = scaler.inverse_transform(pred_scaled)[0][0]

        # Append back to sequence
        new_point = scaler.transform([[pred_price]])
        last_sequence = np.vstack([last_sequence[1:], new_point])

    # Current OHLC
    now_price = float(df["close"].iloc[-1])
    high_price = float(df["high"].iloc[-1])
    low_price = float(df["low"].iloc[-1])
    pred_price = float(pred_price)

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
# Generate multi-step predicted series (without changing DB)
# =========================
def generate_predicted_series(symbol: str, days: int = 0, hours: int = 0) -> list:
    symbol = symbol.upper()

    try:
        days = int(days)
        hours = int(hours)
    except ValueError:
        raise ValueError("Days and hours must be integers.")

    if days > 0:
        duration = "daily"
        steps = days
    elif hours > 0:
        duration = "hourly"
        steps = hours
    else:
        return []

    BASE_DIR = os.path.dirname(__file__)
    MODEL_DIR = os.path.join(BASE_DIR, "crypto_models")
    model_filename = f"{symbol}-INR_{duration}.h5"
    model_path = os.path.join(MODEL_DIR, model_filename)
    if not os.path.exists(model_path):
        return []

    model = load_model(model_path)
    interval = "1d" if duration == "daily" else "1h"
    df = get_live_data(symbol, interval=interval, limit=200)
    closes = df["close"].values.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(closes)
    last_sequence = scaled[-60:]

    series = []
    for _ in range(steps):
        X_input = last_sequence.reshape(1, 60, 1)
        pred_scaled = model.predict(X_input, verbose=0)
        pred_price = float(scaler.inverse_transform(pred_scaled)[0][0])
        series.append(pred_price)
        last_point = scaler.transform([[pred_price]])
        last_sequence = np.vstack([last_sequence[1:], last_point])

    return series


# =========================
# Confidence Estimation via Prediction Dispersion (MC-jitter)
# =========================
def estimate_confidence(symbol: str, days: int = 0, hours: int = 0, samples: int = 20, jitter_scale: float = 0.003) -> float:
    """
    Estimate confidence by running multiple predictions with slight noise
    added to the scaled input sequence (Monte Carlo jitter), and converting
    the dispersion (std dev) of predicted prices into a 0–100 confidence.

    Confidence mapping:
      confidence = 100 * (1 - min(1, std_pred / (baseline * current_price)))
    where baseline is a small fraction (e.g., 2%) of current price.

    Returns a float in [5, 99].
    """
    symbol = symbol.upper()

    # Validate horizon
    try:
        days = int(days)
        hours = int(hours)
    except ValueError:
        raise ValueError("Days and hours must be integers.")

    if days > 0:
        duration = "daily"
        steps = days
    elif hours > 0:
        duration = "hourly"
        steps = hours
    else:
        raise ValueError("Either days or hours must be greater than 0.")

    # Load model
    BASE_DIR = os.path.dirname(__file__)
    MODEL_DIR = os.path.join(BASE_DIR, "crypto_models")
    model_filename = f"{symbol}-INR_{duration}.h5"
    model_path = os.path.join(MODEL_DIR, model_filename)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = load_model(model_path)

    # Fetch live data
    interval = "1d" if duration == "daily" else "1h"
    df = get_live_data(symbol, interval=interval, limit=200)
    closes = df["close"].values.reshape(-1, 1)

    # Scale
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(closes)

    last_sequence = scaled[-60:]
    now_price = float(df["close"].iloc[-1])

    # Run multiple jittered predictions
    preds = []
    for _ in range(max(3, int(samples))):
        seq = last_sequence.copy()
        # Add small Gaussian noise in scaled space, clip to [0,1]
        noise = np.random.normal(loc=0.0, scale=jitter_scale, size=seq.shape)
        seq = np.clip(seq + noise, 0.0, 1.0)

        pred_end = None
        for _ in range(steps):
            X_input = seq.reshape(1, 60, 1)
            pred_scaled = model.predict(X_input, verbose=0)
            pred_end = scaler.inverse_transform(pred_scaled)[0][0]
            new_point = scaler.transform([[pred_end]])
            seq = np.vstack([seq[1:], new_point])

        preds.append(float(pred_end))

    preds = np.array(preds, dtype=float)
    std_pred = float(np.std(preds)) if preds.size else 0.0

    # Map dispersion to confidence; baseline 2% of current price
    baseline = max(1e-6, 0.02 * now_price)
    ratio = min(1.0, std_pred / baseline)
    confidence = 100.0 * (1.0 - ratio)

    # Clamp to reasonable bounds
    confidence = max(5.0, min(99.0, confidence))
    return float(round(confidence, 1))