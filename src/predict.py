import joblib

# Load trained model
model = joblib.load("model/scam_detection_model.pkl")

# Scam keywords
scam_keywords = [
    "otp",
    "password",
    "bank details",
    "account",
    "urgent",
    "immediately",
    "lottery",
    "prize",
    "winner",
    "money",
    "transfer",
    "kyc",
    "blocked",
    "verify",
    "click",
    "payment"
]

while True:
    text = input("\nEnter call conversation (type 'exit' to stop): ")

    if text.lower() == "exit":
        break

    prediction = model.predict([text])[0]
    confidence = model.predict_proba([text]).max()

    # Find suspicious keywords
    detected_keywords = []

    for keyword in scam_keywords:
        if keyword.lower() in text.lower():
            detected_keywords.append(keyword)

    # Calculate risk score
    risk_score = confidence * 100

    # Increase risk if suspicious keywords are found
    risk_score += len(detected_keywords) * 3

    if risk_score > 100:
        risk_score = 100

    print("\n-----------------------------")
    print("       SCAM CALL DETECTOR")
    print("-----------------------------")

    print("Prediction:", prediction)
    print("Risk Score:", round(risk_score, 2), "%")

    if risk_score >= 70:
        print("Risk Level: HIGH")
    elif risk_score >= 40:
        print("Risk Level: MEDIUM")
    else:
        print("Risk Level: LOW")

    if detected_keywords:
        print("\nSuspicious patterns detected:")
        for keyword in detected_keywords:
            print("-", keyword)

    print("-----------------------------")