from crypto_models import predict_future

if __name__ == "__main__":
    try:
        # Example test cases
        print("🔮 Predicting BTC after 1 day...")
        result = predict_future(symbol="BTC", days=1)
        print(result)

        print("\n🔮 Predicting ETH after 12 hours...")
        result = predict_future(symbol="ETH", hours=12)
        print(result)

    except Exception as e:
        print(f"Error: {e}")
