from flask import Flask, session, request, jsonify, send_from_directory
from models import db, User,Prediction     # import db and User model
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from crypto_models import predict_future, symbol_map, estimate_confidence, generate_predicted_series
import os
from datetime import datetime

app = Flask(__name__)  # REQUIRED

# Enable CORS, allow credentials and specify frontend origin(s)
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5000","http://127.0.0.1:5500"])

# Secret key for session management, replace with env var or secure key in production
app.secret_key = 'Shreya03'

# Configure Database (MySQL)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Shreya03@127.0.0.1/mycryptodb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize db with app
db.init_app(app)

# Serve frontend static files from ../frontend folder relative to this file
@app.route('/<path:filename>')
def serve_frontend(filename):
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
    return send_from_directory(frontend_dir, filename)

@app.route("/")
def home():
    return "Hello, Flask is running with MySQL!"

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("fullName")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_pw)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Account created successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Set session info here
    session['user_id'] = user.id
    session['user_name'] = user.name

    return jsonify({
        "message": "Login successful",
        "user": {"id": user.id, "name": user.name, "email": user.email}
    })

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@app.route('/user', methods=["GET"])
def get_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({"id": user.id, "fullName": user.name, "email": user.email})
    return jsonify({"error": "Not logged in"}), 401
@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized. Please login.'}), 401

    data = request.json
    symbol = data.get('symbol')
    mode = data.get('mode')   # "daily" or "hourly"
    value = int(data.get('value', 0))

    if not symbol or not mode or value <= 0:
        return jsonify({'error': 'Invalid input'}), 400

    try:
        # Call prediction model
        days = value if mode == "daily" else 0
        hours = value if mode == "hourly" else 0
        result = predict_future(symbol=symbol, days=days, hours=hours)

        # Estimate confidence based on prediction dispersion
        confidence = estimate_confidence(symbol=symbol, days=days, hours=hours)

        # Save in DB
        prediction = Prediction(
            user_id=session['user_id'],
            symbol=result['symbol'],
            mode=mode,
            value=value,
            current_price=result['current_price'],
            predicted_price=result['predicted_price'],
            high=result['high'],
            low=result['low'],
            direction=result['direction'],
            confidence=confidence
        )
        db.session.add(prediction)
        db.session.commit()

        # Return response
        return jsonify({
            "coin_name": symbol_map.get(symbol, symbol),
            "symbol": result['symbol'],
            "current_price": result['current_price'],
            "predicted_price": result['predicted_price'],
            "high": result['high'],
            "low": result['low'],
            "direction": result['direction'],
            "confidence": confidence,
            "timeframe": result['after']
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/predictions', methods=['GET'])
def get_predictions():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized. Please login.'}), 401
    predictions = Prediction.query.filter_by(user_id=session['user_id']).order_by(Prediction.timestamp.desc()).all()
    output = []
    for p in predictions:
        output.append({
            'symbol': p.symbol,
            'mode': p.mode,
            'value': p.value,
            'current_price': p.current_price,
            'predicted_price': p.predicted_price,
            'high': p.high,
            'low': p.low,
            'direction': p.direction,
            'confidence': p.confidence,
            'timestamp': p.timestamp.isoformat()
        })
    return jsonify(output)

@app.route('/get-latest-prediction', methods=['GET'])
def get_latest_prediction():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized. Please login.'}), 401
    
    latest_prediction = Prediction.query.filter_by(user_id=session['user_id'])\
                                        .order_by(Prediction.timestamp.desc())\
                                        .first()
    if not latest_prediction:
        return jsonify({'error': 'No predictions found'}), 404

    days = latest_prediction.value if latest_prediction.mode == 'daily' else 0
    hours = latest_prediction.value if latest_prediction.mode == 'hourly' else 0

    # Compute series on-the-fly so we don't need localStorage
    try:
        predicted_series = generate_predicted_series(latest_prediction.symbol, days=days, hours=hours)
    except Exception:
        predicted_series = []

    return jsonify({
        'coin': latest_prediction.symbol,
        'mode': latest_prediction.mode,
        'days': days,
        'hours': hours,
        'current': latest_prediction.current_price,
        'predicted': latest_prediction.predicted_price,
        'high': latest_prediction.high,
        'low': latest_prediction.low,
        'direction': latest_prediction.direction,
        'confidence': latest_prediction.confidence,
        'predicted_series': predicted_series,
        'timestamp': latest_prediction.timestamp.isoformat()
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # This will create tables inside mycryptodb
    app.run(debug=True)
