from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

# Question class to represent a question
class Question:
    def __init__(self, text, options, correct_answer):
        self.text = text
        self.options = options
        self.correct_answer = correct_answer

# Quiz class to manage quiz progress
class Quiz:
    def __init__(self, questions):
        self.questions = questions
        self.current_question_index = 0
        self.score = 0

    def get_current_question(self):
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def check_answer(self, selected_option):
        current_question = self.get_current_question()
        if current_question and selected_option == current_question.correct_answer:
            self.score += 1
        self.current_question_index += 1

    def is_completed(self):
        return self.current_question_index >= len(self.questions)

    def reset(self):
        self.current_question_index = 0
        self.score = 0

# Function to connect to the MySQL database
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",          # Database host
        user="root",               # Your MySQL username
        password="mm7766554",      # Your MySQL password
        database="quiz_db",        # Your database name
        auth_plugin="mysql_native_password"  # Adding the auth plugin for MySQL 8+
    )
    return conn

app = Flask(__name__)

# Function to fetch quiz questions from the database
def get_questions_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_questions")  # Fetch all questions
    rows = cursor.fetchall()
    questions = []
    for row in rows:
        question = Question(row[1], [row[2], row[3], row[4], row[5]], row[6])
        questions.append(question)
    conn.close()
    return questions

# Initialize the quiz with questions fetched from the database
questions = get_questions_from_db()
quiz = Quiz(questions)

@app.route("/", methods=["GET", "POST"])
def quiz_page():
    if quiz.is_completed():  # If quiz is completed, redirect to result
        return redirect(url_for("result"))

    question = quiz.get_current_question()

    if request.method == "POST":
        selected_option = request.form.get("option")
        if selected_option:
            quiz.check_answer(selected_option)
            return redirect(url_for("quiz_page"))  # Redirect to the next question

    return render_template(
        "quiz.html",  # Template to display the question
        question=question,
        question_index=quiz.current_question_index + 1,  # 1-based index for user-friendliness
        total_questions=len(quiz.questions)
    )

@app.route("/result")
def result():
    try:
        # Store the score in the database after quiz completion
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the score into quiz_scores table
        cursor.execute("""
            INSERT INTO quiz_scores (user_name, score)
            VALUES (%s, %s)
        """, ("Test User", quiz.score))

        conn.commit()  # Commit the changes to the database
        conn.close()  # Close the connection

        # Return the result to the user
        return render_template("result.html", score=quiz.score, total_questions=len(quiz.questions))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "An error occurred while saving your score. Please try again later."

@app.route("/restart")
def restart_quiz():
    # Reset the quiz
    quiz.reset()
    return redirect(url_for("quiz_page"))

if __name__ == "__main__":
    app.run(debug=True)
