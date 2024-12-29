import os
import random
import time
import csv
from datetime import date
from pathlib import Path

DATA_FILE = "multiplication_performance.csv"
TOP_PERCENTILE = 0.3  # Adjust for selection percentile (30% slowest responses)

# Ensure data file exists
Path(DATA_FILE).touch(exist_ok=True)


def clear_screen():
    """Clear the terminal screen in a portable way."""
    print("\033c", end="")  # ANSI escape code for clearing the screen


def initialize_csv():
    """Ensure the CSV file has the correct header."""
    if os.path.getsize(DATA_FILE) == 0:  # Check if file is empty
        with open(DATA_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["date", "username", "problem", "time"])
            writer.writeheader()


def load_data(username):
    """Load data from CSV file for the specific user."""
    data = []
    with open(DATA_FILE, "r") as file:
        reader = csv.DictReader(file)
        if "username" not in reader.fieldnames:
            print("The CSV file is missing the required header. Exiting...")
            exit()
        for row in reader:
            if row["username"] == username:
                row["time"] = float(row["time"])
                data.append(row)
    return data


def save_data(session_data):
    """Save session data to CSV file."""
    headers = ["date", "username", "problem", "time"]
    with open(DATA_FILE, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerows(session_data)


def get_slowest_problems(data, top_percentile=TOP_PERCENTILE):
    """Get the slowest problems based on the top percentile."""
    if not data:
        return []
    data_sorted = sorted(data, key=lambda x: x["time"], reverse=True)
    cutoff = int(len(data_sorted) * top_percentile)
    return [row["problem"] for row in data_sorted[:cutoff]]


def generate_problem_pool():
    """Generate a full pool of non-trivial multiplication problems."""
    return [f"{i}x{j}" for i in range(2, 10) for j in range(2, 10)]


def main():
    clear_screen()
    print("Welcome to the Multiplication Practice Tool!\n")

    # Initialize CSV
    initialize_csv()

    # Ask for username
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty. Exiting...")
        return

    # Load historical data for the user
    data = load_data(username)
    today = date.today().isoformat()

    # Main practice loop
    while True:
        # Prepare problems
        problem_pool = generate_problem_pool()
        if data:
            slowest_problems = get_slowest_problems(data)
            problems_pool = slowest_problems if slowest_problems else problem_pool
        else:
            problems_pool = problem_pool

        session_data = []

        for trial in range(10):
            clear_screen()
            problem = random.choice(problems_pool)
            factors = list(map(int, problem.split("x")))
            correct_answer = factors[0] * factors[1]

            print(f"User: {username} | Trial {trial + 1}/10")
            print(f"Solve: {problem}")

            start_time = time.time()
            try:
                user_answer = int(input("Your answer: "))
            except ValueError:
                user_answer = -1
            end_time = time.time()

            response_time = end_time - start_time
            session_data.append({
                "date": today,
                "username": username,
                "problem": problem,
                "time": response_time,
            })

            if user_answer == correct_answer:
                print("Correct!")
            else:
                print(f"Wrong! The correct answer is {correct_answer}.")
            time.sleep(1)

        # Save session data
        save_data(session_data)
        data.extend(session_data)  # Update user's data for the session

        # Show 3 slowest responses from the session
        session_data_sorted = sorted(session_data, key=lambda x: x["time"], reverse=True)
        clear_screen()
        print("Session complete!\nHere are your 3 slowest responses:")
        for i, entry in enumerate(session_data_sorted[:3], start=1):
            print(f"{i}. Problem: {entry['problem']} - Time: {entry['time']:.2f} seconds")

        # Ask if the user wants to continue
        choice = input("\nDo you want to continue for another 10 trials? (yes/no): ").strip().lower()
        if choice != "yes":
            print("Thanks for practicing! Goodbye!")
            break


if __name__ == "__main__":
    main()
