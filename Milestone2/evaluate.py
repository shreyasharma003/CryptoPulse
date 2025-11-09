from predict_live_crypto import predict_future, get_live_data
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Current USD to INR rate (you can update this dynamically if needed)
USD_INR = 83.0  

def evaluate_model(symbol="BTC", days=0, hours=0, test_steps=50):
    """
    Evaluate prediction accuracy using backtesting.
    """
    df = get_live_data(symbol, interval="1h" if hours > 0 else "1d", limit=500)
    actual = df["close"].values[-test_steps:]
    preds = []

    for i in range(test_steps):
        result = predict_future(symbol, days=days if hours == 0 else 0, hours=hours if hours > 0 else 0)
        preds.append(result["predicted_price"])

    mae = mean_absolute_error(actual, preds)
    rmse = np.sqrt(mean_squared_error(actual, preds))
    mape = np.mean(np.abs((actual - preds) / actual)) * 100

    # Convert to INR
    mae_inr = mae * USD_INR
    rmse_inr = rmse * USD_INR

    print(f"\n📊 Evaluation for {symbol}:")
    print(f"MAE  = {mae:.2f} USD  (≈ ₹{mae_inr:.2f})")
    print(f"RMSE = {rmse:.2f} USD  (≈ ₹{rmse_inr:.2f})")
    print(f"MAPE = {mape:.2f}%")

if __name__ == "__main__":
    evaluate_model("BTC", hours=1, test_steps=20)
