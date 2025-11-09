from crypto_models import predict_future, symbol_map  # your updated file

# =========================
# Supported coins
# =========================
coins_list = ["BNB", "BTC", "ETH", "SOL", "XRP", "DOGE", "DOT", "TRX"]

# =========================
# Interactive input
# =========================
symbol = input(f"Enter coin symbol {coins_list}: ").upper()
while symbol not in coins_list:
    symbol = input(f"Invalid symbol. Enter again from {coins_list}: ").upper()

try:
    days = int(input("Enter number of days for prediction: "))
    hours = int(input("Enter number of hours for prediction: "))
except ValueError:
    print("Invalid input. Setting default duration to 2 days 10 hours.")
    days, hours = 2, 10

# =========================
# Run prediction
# =========================
try:
    result = predict_future(symbol, days=days, hours=hours)
    print(f"\n🔹 Predicted {result['symbol']} price after {result['after']}:")
    print(f"   Current:   ₹{result['current_price']:.2f}")
    print(f"   Predicted: ₹{result['predicted_price']:.2f}")
    print(f"   High:      ₹{result['high']:.2f}, Low: ₹{result['low']:.2f}")
    print(f"   Direction: {result['direction']}")
except Exception as e:
    print(f"\n❌ Error: {e}")
