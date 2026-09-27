from flask import Flask, render_template, request, send_from_directory
import joblib
import pandas as pd
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

from src.speech_to_text import transcribe_audio


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# LOAD ML MODELS
# ============================================================

text_model = joblib.load(
    "model/scam_detection_model.pkl"
)

behavior_model = joblib.load(
    "model/behavior_model.pkl"
)


# ============================================================
# FOLDERS
# ============================================================

UPLOAD_FOLDER = "audio/uploads"
DATA_FOLDER = "data"

HISTORY_FILE = os.path.join(
    DATA_FOLDER,
    "history.json"
)


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    DATA_FOLDER,
    exist_ok=True
)


# ============================================================
# HISTORY FUNCTIONS
# ============================================================

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except Exception:

        return []


def save_history(history):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# STATISTICS
# ============================================================

def get_statistics():

    history = load_history()

    total = len(history)

    scam = sum(
        1
        for item in history
        if item.get("prediction") == "SCAM"
    )

    genuine = sum(
        1
        for item in history
        if item.get("prediction") == "GENUINE"
    )

    high = sum(
        1
        for item in history
        if item.get("risk_level") == "HIGH"
    )

    medium = sum(
        1
        for item in history
        if item.get("risk_level") == "MEDIUM"
    )

    low = sum(
        1
        for item in history
        if item.get("risk_level") == "LOW"
    )

    return {
        "total": total,
        "scam": scam,
        "genuine": genuine,
        "high": high,
        "medium": medium,
        "low": low
    }


# ============================================================
# BEHAVIOR DETECTION
# ============================================================

def detect_behavior(text):

    text_lower = text.lower()


    # OTP / verification related words

    otp_words = [
        "otp",
        "one time password",
        "verification code",
        "security code",
        "pin"
    ]


    # Money related words

    money_words = [
        "send money",
        "transfer money",
        "payment",
        "pay now",
        "bank transfer",
        "account number",
        "upi",
        "refund"
    ]


    # Urgency related words

    urgent_words = [
        "immediately",
        "urgent",
        "right now",
        "act now",
        "quickly",
        "within minutes",
        "today",
        "blocked",
        "suspended",
        "close your account",
        "last warning"
    ]


    otp_request = int(
        any(
            word in text_lower
            for word in otp_words
        )
    )


    money_request = int(
        any(
            word in text_lower
            for word in money_words
        )
    )


    urgent_language = int(
        any(
            word in text_lower
            for word in urgent_words
        )
    )


    return [
        0,                  # unknown_number
        0,                  # international_number
        0,                  # repeated_calls
        otp_request,        # otp_request
        money_request,      # money_request
        urgent_language,    # urgent_language
        10                  # call_duration
    ]


# ============================================================
# CALL ANALYSIS
# ============================================================

def analyze_call(text):

    # --------------------------------------------------------
    # TEXT MODEL
    # --------------------------------------------------------

    text_probabilities = (
        text_model.predict_proba([text])[0]
    )

    text_classes = list(
        text_model.classes_
    )

    scam_index = text_classes.index(
        "scam"
    )

    text_scam_score = (
        text_probabilities[scam_index]
        * 100
    )


    # --------------------------------------------------------
    # BEHAVIOR MODEL
    # --------------------------------------------------------

    behavior_values = detect_behavior(
        text
    )


    behavior_columns = [
        "unknown_number",
        "international_number",
        "repeated_calls",
        "otp_request",
        "money_request",
        "urgent_language",
        "call_duration"
    ]


    behavior_data = pd.DataFrame(
        [behavior_values],
        columns=behavior_columns
    )


    behavior_probabilities = (
        behavior_model.predict_proba(
            behavior_data
        )[0]
    )


    behavior_classes = list(
        behavior_model.classes_
    )


    behavior_scam_index = (
        behavior_classes.index(
            "scam"
        )
    )


    behavior_scam_score = (
        behavior_probabilities[
            behavior_scam_index
        ]
        * 100
    )


    # --------------------------------------------------------
    # HYBRID SCORE
    # --------------------------------------------------------

    final_score = (
        text_scam_score * 0.60
        +
        behavior_scam_score * 0.40
    )


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    if final_score >= 50:

        prediction = "SCAM"

    else:

        prediction = "GENUINE"


    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if final_score >= 70:

        risk_level = "HIGH"

    elif final_score >= 40:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    # --------------------------------------------------------
    # SHORT VOICE MESSAGE
    # --------------------------------------------------------

    if risk_level == "HIGH":

        voice_message = (
            "Warning! Scam risk detected."
        )

    elif risk_level == "MEDIUM":

        voice_message = (
            "Caution! Suspicious activity detected."
        )

    else:

        voice_message = (
            "Call appears safe."
        )


    # --------------------------------------------------------
    # SUSPICIOUS INDICATORS
    # --------------------------------------------------------

    indicators = []


    # OTP

    if any(
        word in text.lower()
        for word in [
            "otp",
            "one time password",
            "verification code",
            "security code",
            "pin"
        ]
    ):

        indicators.append(
            "OTP / Verification Request"
        )


    # Money

    if any(
        word in text.lower()
        for word in [
            "send money",
            "transfer money",
            "payment",
            "pay now",
            "bank transfer",
            "account number",
            "upi",
            "refund"
        ]
    ):

        indicators.append(
            "Money / Banking Request"
        )


    # Urgency

    if any(
        word in text.lower()
        for word in [
            "immediately",
            "urgent",
            "right now",
            "act now",
            "quickly",
            "within minutes",
            "today",
            "blocked",
            "suspended",
            "close your account",
            "last warning"
        ]
    ):

        indicators.append(
            "Urgent Language"
        )


    if not indicators:

        indicators.append(
            "No strong indicators detected"
        )


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {

        "prediction": prediction,

        "text_score": round(
            text_scam_score,
            2
        ),

        "behavior_score": round(
            behavior_scam_score,
            2
        ),

        "final_score": round(
            final_score,
            2
        ),

        "risk_level": risk_level,

        "text": text,

        "voice_message": voice_message,

        "indicators": indicators
    }


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    history = load_history()

    # Statistics

    stats = get_statistics()

    # Last 5 analyses

    recent = history[-5:]

    recent.reverse()

    return render_template(
        "home.html",
        stats=stats,
        recent=recent
    )


# ============================================================
# ANALYZE PAGE
# ============================================================

@app.route(
    "/analyze",
    methods=["GET", "POST"]
)
def analyze():

    # --------------------------------------------------------
    # GET REQUEST
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "analyze.html",
            result=None
        )


    # --------------------------------------------------------
    # CHECK AUDIO
    # --------------------------------------------------------

    if "audio" not in request.files:

        return render_template(
            "analyze.html",
            result=None,
            error="Please select an audio file."
        )


    audio = request.files["audio"]


    if audio.filename == "":

        return render_template(
            "analyze.html",
            result=None,
            error="Please select an audio file."
        )


    # --------------------------------------------------------
    # SECURE FILE NAME
    # --------------------------------------------------------

    filename = secure_filename(
        audio.filename
    )


    if not filename:

        return render_template(
            "analyze.html",
            result=None,
            error="Invalid audio file."
        )


    # --------------------------------------------------------
    # SAVE AUDIO
    # --------------------------------------------------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    audio.save(
        file_path
    )


    # --------------------------------------------------------
    # WHISPER TRANSCRIPTION
    # --------------------------------------------------------

    try:

        text = transcribe_audio(
            file_path
        )

    except Exception as error:

        print(
            "Transcription error:",
            error
        )

        return render_template(
            "analyze.html",
            result=None,
            error="Audio transcription failed."
        )


    if not text:

        return render_template(
            "analyze.html",
            result=None,
            error="Could not transcribe the audio."
        )


    # --------------------------------------------------------
    # ML ANALYSIS
    # --------------------------------------------------------

    result = analyze_call(
        text
    )


    # --------------------------------------------------------
    # FILE INFORMATION
    # --------------------------------------------------------

    result["filename"] = filename

    result["date"] = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )


    # ========================================================
    # SAVE RESULT TO HISTORY
    # ========================================================

    history = load_history()


    history.append({

        "filename": filename,

        "date": result["date"],

        "prediction": result["prediction"],

        "risk_level": result["risk_level"],

        "final_score": result["final_score"],

        "text_score": result["text_score"],

        "behavior_score": result["behavior_score"],

        # NEW:
        # Save complete transcription

        "text": result["text"],

        # NEW:
        # Save suspicious indicators

        "indicators": result["indicators"]

    })


    save_history(
        history
    )


    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    return render_template(
        "analyze.html",
        result=result
    )


# ============================================================
# AUDIO PLAYBACK
# ============================================================

@app.route(
    "/audio/<path:filename>"
)
def audio_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# HISTORY PAGE
# ============================================================

@app.route("/history")
def history():

    history_data = load_history()

    history_data.reverse()

    return render_template(
        "history.html",
        history=history_data
    )


# ============================================================
# RISK MAP PAGE
# ============================================================

@app.route("/map")
def risk_map():

    stats = get_statistics()

    return render_template(
        "map.html",
        scam_count=stats["scam"],
        genuine_count=stats["genuine"],
        stats=stats
    )


# ============================================================
# ANALYTICS PAGE
# ============================================================

@app.route("/analytics")
def analytics():

    history = load_history()


    # --------------------------------------------------------
    # RISK COUNTS
    # --------------------------------------------------------

    counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }


    # --------------------------------------------------------
    # PREDICTION COUNTS
    # --------------------------------------------------------

    pred = {
        "SCAM": 0,
        "GENUINE": 0
    }


    # --------------------------------------------------------
    # COUNT HISTORY
    # --------------------------------------------------------

    for item in history:

        risk = item.get(
            "risk_level"
        )

        prediction = item.get(
            "prediction"
        )


        if risk in counts:

            counts[risk] += 1


        if prediction in pred:

            pred[prediction] += 1


    # --------------------------------------------------------
    # SEND DATA TO ANALYTICS.HTML
    # --------------------------------------------------------

    return render_template(
        "analytics.html",
        counts=counts,
        pred=pred
    )


# ============================================================
# ABOUT PAGE
# ============================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# ============================================================
# START FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )