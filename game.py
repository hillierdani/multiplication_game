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
    os.system("cls" if os.name == "nt" else "clear")


def load_data():
    """Load data from CSV file."""
    data = []
    with open(DATA_FILE, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["time"] = float(row["time"])
            data.append(row)
    return data


def save_data(session_data):
    """Save session data to CSV file."""
    headers = ["date", "problem", "time"]
    with open(DATA_FILE, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if file.tell() == 0:
            writer.writeheader()  # Write header if file is empty
        writer.writerows(session_data)


def get_slowest_problems(data, top_percentile=TOP_PERCENTILE):
    """Get the slowest problems based on the top percentile."""
    if not data:
        return []
    data_sorted = sorted(data, key=lambda x: x["time"], reverse=True)
    cutoff = int(len(data_sorted) * top_percentile)
    return [row["problem"] for row in data_sorted[:cutoff]]


def main():
    clear_screen()
    print("Welcome to the Multiplication Practice Tool!\n")

    # Load historical data
    data = load_data()
    today = date.today().isoformat()

    # Prepare problems
    if data:
        slowest_problems = get_slowest_problems(data)
        problems_pool = slowest_problems if slowest_problems else [f"{i}x{j}" for i in range(1, 11) for j in
                                                                   range(1, 11)]
    else:
        problems_pool = [f"{i}x{j}" for i in range(1, 11) for j in range(1, 11)]

    session_data = []

    for trial in range(10):
        clear_screen()
        problem = random.choice(problems_pool)
        factors = list(map(int, problem.split("x")))
        correct_answer = factors[0] * factors[1]

        print(f"Trial {trial + 1}/10")
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

    # Show 3 slowest responses from the session
    session_data_sorted = sorted(session_data, key=lambda x: x["time"], reverse=True)
    clear_screen()
    print("Session complete!\nHere are your 3 slowest responses:")
    for i, entry in enumerate(session_data_sorted[:3], start=1):
        print(f"{i}. Problem: {entry['problem']} - Time: {entry['time']:.2f} seconds")


if __name__ == "__main__":
    main()
