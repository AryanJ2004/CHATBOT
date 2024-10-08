from flask import Flask, render_template, request
from fuzzywuzzy import process
import google.generativeai as genai
from dotenv import load_dotenv
import os
import mysql.connector
import random

# Load environment variables
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Initialize the GenerativeAI model
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_ADDON_HOST"),
        user=os.environ.get("MYSQL_ADDON_USER"),
        password=os.environ.get("MYSQL_ADDON_PASSWORD"),  # This line is now correct
        database=os.environ.get("MYSQL_ADDON_DB")
    )

# Function to fetch predefined answers from the database
def fetch_predefined_answers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT pattern, response FROM predefined_answers")
    data = cursor.fetchall()

    questions = {}
    for row in data:
        pattern = row["pattern"].lower()
        if pattern in questions:
            questions[pattern].append(row["response"])
        else:
            questions[pattern] = [row["response"]]

    cursor.close()
    connection.close()

    return questions

# Route for the home page
@app.route("/")
def index():
    return render_template('chat.html')

# Route to handle chat requests
@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    response = get_chat_response(msg)
    return response

# Function to get the response for a given input text
def get_chat_response(text):
    # Make the input lowercase for case-insensitive comparison
    text_lower = text.lower()

    # Fetch predefined answers from the database
    predefined_answers = fetch_predefined_answers()

    # Find the closest matching question using fuzzywuzzy
    matching_patterns = list(predefined_answers.keys())
    closest_match, score = process.extractOne(text_lower, matching_patterns)

    # Check if the similarity score is above a certain threshold (e.g., 80)
    threshold = 90  # Adjusted threshold for fuzzy matching
    if score >= threshold:
        return random.choice(predefined_answers[closest_match])

    # If no close match, generate a response using the AI model
    try:
        response = model.generate_content(text)  # Generative AI call
        if response.candidates and response.candidates[0].content:
            formatted_response = response.candidates[0].content.parts[0].text
        else:
            formatted_response = "I don't know the answer to that."

        return formatted_response
    except Exception as e:
        if "timeout" in str(e).lower():
            return "Sorry, the GenerativeAI API timed out. Please try again later."
        else:
            return "An error occurred. Please try again later."

if __name__ == "__main__":
    app.run(debug=True)
