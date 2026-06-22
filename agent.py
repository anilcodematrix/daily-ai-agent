#!/usr/bin/env python3
"""
Daily AI Agent - Automatically makes GitHub contributions every day.
Generates daily logs with motivational quotes, tech tips, and activity summaries.
Runs via GitHub Actions on a daily schedule (cron).
"""

import os
import json
import random
import datetime
import requests
import base64


# CONFIG (values injected from GitHub Secrets)
GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO   = os.environ.get("GITHUB_REPOSITORY", "anilcodematrix/daily-ai-agent")
GITHUB_ACTOR  = os.environ.get("GITHUB_ACTOR", "anilcodematrix")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
}


# CONTENT BANKS
MOTIVATIONAL_QUOTES = [
    ("The best way to predict the future is to create it.", "Abraham Lincoln"),
    ("Code is like humor. When you have to explain it, its bad.", "Cory House"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Stay hungry, stay foolish.", "Steve Jobs"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Any fool can write code that a computer can understand.", "Martin Fowler"),
    ("Debugging is twice as hard as writing the code.", "Brian W. Kernighan"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("Programs must be written for people to read.", "Harold Abelson"),
    ("Simplicity is the soul of efficiency.", "Austin Freeman"),
    ("It always seems impossible until it is done.", "Nelson Mandela"),
]

TECH_TIPS = [
    ("Python", "Use list comprehensions for cleaner code: [x*2 for x in range(10)]"),
    ("Git", "Use git stash to temporarily save changes without committing."),
    ("GitHub", "Use GitHub Actions to automate CI/CD pipelines directly in your repo."),
    ("Python", "Use enumerate() to get both index and value: for i, v in enumerate(lst)"),
    ("JavaScript", "Use const and let instead of var for block-scoped variables."),
    ("CSS", "Use CSS variables (--var-name) for consistent theming across your project."),
    ("Python", "Use f-strings for fast string formatting: f Hello {name}"),
    ("Git", "Use git log --oneline --graph for a visual branch history."),
    ("Python", "Use pathlib.Path instead of os.path for modern file handling."),
    ("SQL", "Use indexes on frequently queried columns to speed up lookups."),
    ("AI/ML", "Always split dataset: 80% train, 10% validation, 10% test."),
    ("AI/ML", "Normalize features before training - scale matters for many algorithms."),
    ("Security", "Never hardcode credentials - always use environment variables."),
]

AI_FACTS = [
    "AI can now generate images, music, text, and code from simple prompts.",
    "The term Artificial Intelligence was coined by John McCarthy in 1956.",
    "GPT models are trained on hundreds of billions of tokens of text data.",
    "Machine Learning is a subset of AI; Deep Learning is a subset of ML.",
    "Neural networks are loosely inspired by the structure of the human brain.",
    "Reinforcement Learning was used to train AlphaGo to beat Go champions.",
    "Python is the most popular language for AI/ML due to its rich ecosystem.",
    "Transfer learning allows models trained on one task to be fine-tuned for another.",
    "The Turing Test, proposed in 1950, tests machine intelligence.",
    "Large Language Models can perform tasks they were never explicitly trained for.",
]

LEARNING_GOALS = [
    "Learn one new algorithm or data structure today.",
    "Read documentation for a library you use but dont fully understand.",
    "Build a small project to solidify what you have learned this week.",
    "Write a unit test for code you have already written.",
    "Contribute to an open-source project - even fixing a typo counts!",
    "Refactor old code to make it cleaner and more readable.",
    "Document your code with meaningful comments and docstrings.",
    "Review someone elses code to learn new patterns and techniques.",
    "Deploy a small app to practice your DevOps skills.",
    "Study one AI/ML concept and implement a minimal example.",
]


def get_file_sha(path):
    """Get file SHA needed to update existing files."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json().get("sha")
    return None


def upsert_file(path, content, message):
    """Create or update a file via GitHub API."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    sha = get_file_sha(path)
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "committer": {
            "name": GITHUB_ACTOR,
            "email": f"{GITHUB_ACTOR}@users.noreply.github.com",
        },
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    if r.status_code in (200, 201):
        return True
    print(f"Error: {r.status_code} - {r.text}")
    return False


def build_daily_log():
    """Build the daily log content."""
    now       = datetime.datetime.utcnow()
    date_str  = now.strftime("%Y-%m-%d")
    time_str  = now.strftime("%H:%M:%S UTC")
    weekday   = now.strftime("%A")
    week_num  = now.isocalendar()[1]

    quote, author = random.choice(MOTIVATIONAL_QUOTES)
    tech_cat, tech_tip = random.choice(TECH_TIPS)
    ai_fact   = random.choice(AI_FACTS)
    goal      = random.choice(LEARNING_GOALS)

    content = f"""# Daily AI Agent Log - {date_str}

Auto-generated by Daily AI Agent | {time_str}

## Date Info
- Date: {date_str}
- Weekday: {weekday}
- Week: Week {week_num} of {now.year}
- Time (UTC): {time_str}

## Quote of the Day
"{quote}"
-- {author}

## Tech Tip of the Day
Category: {tech_cat}
{tech_tip}

## AI Fact of the Day
{ai_fact}

## Todays Learning Goal
{goal}

## Agent Status
- Daily log generated successfully
- Contribution count updated
- GitHub Actions workflow running on schedule
- Next run: tomorrow at 00:00 UTC
"""
    return date_str, content


def update_tracker():
    """Update the JSON contribution tracker."""
    tracker_path = "data/contribution_tracker.json"
    sha = get_file_sha(tracker_path)

    if sha:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{tracker_path}"
        r = requests.get(url, headers=HEADERS)
        raw = base64.b64decode(r.json()["content"]).decode()
        tracker = json.loads(raw)
    else:
        tracker = {
            "total_runs": 0,
            "start_date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
            "logs": []
        }

    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    tracker["total_runs"] += 1
    tracker["last_run"] = today
    tracker["logs"].append({"date": today, "run": tracker["total_runs"]})
    tracker["logs"] = tracker["logs"][-90:]  # keep last 90

    content = json.dumps(tracker, indent=2)
    msg = f"chore(tracker): update contribution tracker [{today}] run #{tracker['total_runs']}"
    return upsert_file(tracker_path, content, msg)


def main():
    """Main entry point."""
    print("Daily AI Agent starting...")

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN is not set!")
        raise SystemExit(1)

    # 1) Create daily log
    print("Generating daily log...")
    date_str, log_content = build_daily_log()
    path = f"logs/{date_str}.md"
    ok1 = upsert_file(path, log_content, f"feat(log): add daily log for {date_str}")
    print(f"Daily log {path}: {'OK' if ok1 else 'FAILED'}")

    # 2) Update tracker
    print("Updating contribution tracker...")
    ok2 = update_tracker()
    print(f"Tracker: {'OK' if ok2 else 'FAILED'}")

    print("Daily AI Agent completed!")
    if all([ok1, ok2]):
        print("Status: ALL TASKS SUCCESSFUL")
    else:
        print("Status: SOME TASKS FAILED")


if __name__ == "__main__":
    main()
