import joblib
import pandas as pd

# Load both models
text_model = joblib.load("model/scam_detection_model.pkl")
behavior_model = joblib.load("model/behavior_model.pkl")

# Get conversation
text = input("Enter call conversation: ")

# Text model prediction
text_prediction = text_model.predict([text])[0]
text_probability = text_model.predict_proba([text]).max()

print("\nEnter call behavior details:")

unknown_number = int(input("Unknown number? (1 = Yes, 0 = No): "))
international_number = int(input("International number? (1 = Yes, 0 = No): "))
repeated_calls = int(input("Repeated calls? (1 = Yes, 0 = No): "))
otp_request = int(input("OTP requested? (1 = Yes, 0 = No): "))
money_request = int(input("Money requested? (1 = Yes, 0 = No): "))
urgent_language = int(input("Urgent language? (1 = Yes, 0 = No): "))
call_duration = int(input("Call duration in seconds: "))

# Create behavior data
behavior_data = pd.DataFrame([[
    unknown_number,
    international_number,
    repeated_calls,
    otp_request,
    money_request,
    urgent_language,
    call_duration
]], columns=[
    "unknown_number",
    "international_number",
    "repeated_calls",
    "otp_request",
    "money_request",
    "urgent_language",
    "call_duration"
])

# Behavior prediction
behavior_prediction = behavior_model.predict(behavior_data)[0]
behavior_probability = behavior_model.predict_proba(behavior_data).max()

# Calculate scam scores
text_scam_score = (
    text_model.predict_proba([text])[0][
        list(text_model.classes_).index("scam")
    ] * 100
)

behavior_scam_score = (
    behavior_model.predict_proba(behavior_data)[0][
        list(behavior_model.classes_).index("scam")
    ] * 100
)

# Hybrid score
final_score = (text_scam_score * 0.6) + (behavior_scam_score * 0.4)

# Final prediction
if final_score >= 50:
    final_prediction = "SCAM"
else:
    final_prediction = "GENUINE"

print("\n==============================")
print("      HYBRID SCAM DETECTOR")
print("==============================")

print("Text Model Prediction:", text_prediction)
print("Text Scam Score:", round(text_scam_score, 2), "%")

print("Behavior Model Prediction:", behavior_prediction)
print("Behavior Scam Score:", round(behavior_scam_score, 2), "%")

print("\nFINAL PREDICTION:", final_prediction)
print("FINAL RISK SCORE:", round(final_score, 2), "%")

if final_score >= 70:
    print("RISK LEVEL: HIGH")
elif final_score >= 40:
    print("RISK LEVEL: MEDIUM")
else:
    print("RISK LEVEL: LOW")

print("==============================")