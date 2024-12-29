import os
import random
import time
import csv
from datetime import date
from pathlib import Path
from collections import Counter

TOP_PERCENTILE = 0.3  # Adjust for selection percentile (30% slowest responses)


def clear_screen():
    """Clear the terminal screen in a portable way."""
    print("\033c", end="")  # ANSI escape code for clearing the screen


def get_user_file(username):
    """Get the CSV file path for the user."""
    return f"{username}_performance.csv"


def initialize_csv(file_path):
    """Ensure the CSV file has the correct header."""
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["date", "problem", "time", "correct"])
            writer.writeheader()


def load_data(file_path):
    """Load data from CSV file for the specific user."""
    data = []
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["time"] = float(row["time"])
            row["correct"] = row["correct"] == "True"
            data.append(row)
    return data


def save_data(file_path, session_data):
    """Save session data to CSV file."""
    with open(file_path, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "problem", "time", "correct"])
        writer.writerows(session_data)


def get_last_complete_session(data):
    """Get the most recent day with at least 10 correct answers."""
    day_data = {}
    for row in data:
        if row["correct"]:
            day_data.setdefault(row["date"], []).append(row)

    # Find the last date with at least 10 correct answers
    completed_sessions = {day: rows for day, rows in day_data.items() if len(rows) >= 10}
    if not completed_sessions:
        return []

    last_date = max(completed_sessions.keys())
    return completed_sessions[last_date]


def prioritize_problems(data):
    """Prioritize problems based on incorrect answers and long response times."""
    incorrect_problems = [row["problem"] for row in data if not row["correct"]]
    if incorrect_problems:
        return incorrect_problems

    # If no incorrect problems, select based on slowest response times
    sorted_data = sorted(data, key=lambda x: x["time"], reverse=True)
    top_slowest = sorted_data[:int(len(sorted_data) * TOP_PERCENTILE)]
    return [row["problem"] for row in top_slowest]


def generate_problem_pool():
    """Generate a full pool of non-trivial multiplication problems."""
    return [f"{i}x{j}" for i in range(2, 10) for j in range(2, 10)]


def main():
    clear_screen()
    print("Welcome to the Multiplication Practice Tool!\n")

    # Ask for username
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty. Exiting...")
        return

    # Get user-specific file
    user_file = get_user_file(username)
    initialize_csv(user_file)

    # Load historical data for the user
    data = load_data(user_file)
    today = date.today().isoformat()

    # Get the last completed session
    last_session_data = get_last_complete_session(data)

    # Main practice loop
    while True:
        # Prepare problems
        problem_pool = generate_problem_pool()
        if last_session_data:
            prioritized_problems = prioritize_problems(last_session_data)
            problems_pool = prioritized_problems if prioritized_problems else problem_pool
        else:
            problems_pool = problem_pool

        session_data = []
        correct_count = 0

        for trial in range(10):
            clear_screen()
            problem = random.choice(problems_pool)
            factors = list(map(int, problem.split("x")))
            correct_answer = factors[0] * factors[1]

            print(f"{problem}")

            start_time = time.time()
            try:
                user_answer = int(input("Your answer: "))
            except ValueError:
                user_answer = -1
            end_time = time.time()

            response_time = end_time - start_time
            is_correct = user_answer == correct_answer
            session_data.append({
                "date": today,
                "problem": problem,
                "time": response_time,
                "correct": is_correct,
            })

            if is_correct:
                print("Correct!")
                correct_count += 1
            else:
                print(f"Wrong! The correct answer is {correct_answer}.")
            time.sleep(1)

        # Save session data
        save_data(user_file, session_data)
        data.extend(session_data)  # Update user's data for the session

        # Show 3 slowest responses from the session
        session_data_sorted = sorted(session_data, key=lambda x: x["time"], reverse=True)
        clear_screen()
        print("Session complete!\nHere are your 3 slowest responses:")
        for i, entry in enumerate(session_data_sorted[:3], start=1):
            print(f"{i}. Problem: {entry['problem']} - Time: {entry['time']:.2f} seconds")

        # Check if user completed a full session of 10 correct answers
        if correct_count < 10:
            print("\nYou did not get 10 correct answers. Try again!")
        else:
            # Ask if the user wants to continue
            choice = input("\nDo you want to continue for another 10 trials? (yes/no): ").strip().lower()
            if choice != "yes":
                print("Thanks for practicing! Goodbye!")
                break


if __name__ == "__main__":
    main()
