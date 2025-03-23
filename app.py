from flask import Flask, render_template, request
import joblib
import numpy as np
from xhtml2pdf import pisa
from flask import send_file
from xhtml2pdf import pisa
import io

app = Flask(__name__)

# Load trained model
model = joblib.load("model.pkl")

# Define mappings for categorical variables
occupation_mapping = {"Student": 0, "Professional": 1, "Self-employed": 2, "Unemployed": 3, "Other": 4}
screen_time_mapping = {"Less than 1 hour": 0, "1–3 hours": 1, "3–5 hours": 2, "More than 5 hours": 3}
usage_mapping = {"Social media": 0, "Work": 1, "Entertainment": 2, "Communication": 3, "Other": 4}
apps_mapping = {"Social media": 0, "Gaming": 1, "Messaging": 2, "Productivity": 3, "Streaming": 4, "Other": 5}
binary_mapping = {"Yes": 1, "No": 0}
suggestions = {
            "Low": {
                "title": "Low Addiction Risk",
                "description": """
                Based on your responses, we've analyzed your smartphone usage patterns.
                What This Means:
                You appear to have a healthy relationship with your smartphone. You use it as a tool without letting it control your life.
                Keep maintaining these balanced habits.
                """,
                "recommendations": [
                    "Set specific 'no-phone' times during your day, such as during meals or the first hour after waking up.",
                    "Use built-in screen time monitoring tools to track your usage patterns.",
                    "Keep your phone out of reach while working on important tasks.",
                    "Turn off non-essential notifications to reduce distractions.",
                    "Avoid using your phone at least 1 hour before bedtime and keep it outside the bedroom while sleeping."
                ],
                "disclaimer": "This assessment is for informational purposes only and does not constitute medical advice. If you're concerned about your smartphone usage, consider consulting a mental health professional."
            },
            "Medium": {
                "title": "Medium Addiction Risk",
                "description": """
                Based on your responses, we've analyzed your smartphone usage patterns.
                What This Means:
                You show some signs of smartphone dependency. While not severe, you might want to be mindful of your usage patterns and consider implementing some of our suggestions.
                """,
                "recommendations": [
                    "Set specific 'no-phone' times during your day, such as during meals or the first hour after waking up.",
                    "Use built-in screen time monitoring tools to track your usage patterns.",
                    "Try a 'digital detox' for one day each week where you minimize smartphone use.",
                    "Create tech-free zones in your home, such as the bedroom or dining area.",
                    "Engage in offline hobbies like reading, exercising, or drawing."
                ],
                "disclaimer": "This assessment is for informational purposes only and does not constitute medical advice. If you're concerned about your smartphone usage, consider consulting a mental health professional."
            },
            "High": {
                "title": "High Addiction Risk",
                "description": """
                Based on your responses, we've analyzed your smartphone usage patterns.
                What This Means:
                Your relationship with your smartphone appears to be problematic. Your usage patterns suggest a severe addiction that is likely impacting your well-being significantly.
                """,
                "recommendations": [
                    "Establish clear time limits for smartphone usage each day.",
                    "Practice mindfulness techniques when you feel the urge to check your phone unnecessarily.",
                    "Set up accountability with friends or family to help maintain healthier smartphone habits.",
                    "Try a longer digital detox period (3-7 days) with a trusted friend or family member's support.",
                    "Seek professional help if your smartphone usage is significantly affecting your daily life."
                ],
                "disclaimer": "This assessment is for informational purposes only and does not constitute medical advice. If you're concerned about your smartphone usage, consider consulting a mental health professional."
            }
        }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Extract form inputs
        input_data = [
            occupation_mapping[request.form["Occupation"]],
            screen_time_mapping[request.form["ScreenTime"]],
            usage_mapping[request.form["Usage"]],
            apps_mapping[request.form["Apps"]],
            binary_mapping[request.form["Anxious"]],
            binary_mapping[request.form["TriedReduce"]],
            binary_mapping[request.form["Prioritize"]],
            binary_mapping[request.form["SleepAffected"]],
            binary_mapping[request.form["DuringMeals"]],
            binary_mapping[request.form["PhysicalDiscomfort"]],
            binary_mapping[request.form["CheckWithoutReason"]],
            binary_mapping[request.form["IgnoreTasks"]],
            binary_mapping[request.form["SetLimits"]],
            binary_mapping[request.form["CopeWithStress"]],
            binary_mapping[request.form["Satisfied"]],
        ]

        # Convert to NumPy array
        input_data = np.array(input_data).reshape(1, -1)

        # Prediction
        prediction = model.predict(input_data)[0]

        # Mapping prediction numbers to labels
        prediction_mapping = {0: "Low", 1: "Medium", 2: "High"}
        prediction_label = prediction_mapping.get(prediction, "Unknown")

        # Detailed suggestions for each addiction level
        

        suggestion = suggestions.get(prediction_label, {"title": "Unknown", "description": "No suggestions available.", "recommendations": [], "disclaimer": ""})

        return render_template("index.html", result=prediction_label, suggestion=suggestion)

    except Exception as e:
        return str(e)

@app.route("/download_pdf/<result>")
def download_pdf(result):
    try:
        if result not in suggestions:
            return "Invalid result!"

        suggestion = suggestions[result]
        html = render_template("report.html", result=result, suggestion=suggestion)

        # Create PDF in memory buffer
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

        if pisa_status.err:
            return "Failed to generate PDF"

        # Move buffer pointer to the beginning
        pdf_buffer.seek(0)

        return send_file(pdf_buffer, as_attachment=True, mimetype='application/pdf', download_name=f"{result}_Report.pdf")

    except Exception as e:
        return f"Error: {e}"
if __name__ == "__main__":
    app.run(debug=True)