import requests
from datetime import datetime, timedelta
import json

NOTION_API_KEY = "ntn_k3476940573aNdHEb1u4xIHjiOk5nnrIBjVnhvKoznUc3B"
DATABASE_ID = "1370cf3de71d80679701e81e2437f71a"

# Get today's date & end of the week (Sunday)
today = datetime.today()
end_of_week = today + timedelta(days=(6 - today.weekday()))  # Sunday

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

payload = {"filter": {"property": "Date", "date": {"on_or_after": today.strftime("%Y-%m-%d")}}}

response = requests.post(url, json=payload, headers=headers)
data = response.json()


# Separate lists for today & upcoming client meetings
today_tasks = []
client_meetings = []

for entry in data["results"]:
    # Extract date
    date_start_raw = entry["properties"]["Date"]["date"]["start"]
    if date_start_raw:
        date_start = datetime.fromisoformat(date_start_raw)
    # Strip timezone
    date_start = date_start.replace(tzinfo=None)
else:
    date_start = None
    date_end_raw = entry["properties"]["Date"]["date"]["end"]

    date_start = datetime.fromisoformat(date_start_raw) if date_start_raw else None
    date_end = datetime.fromisoformat(date_end_raw).strftime("%I:%M %p") if date_end_raw else "No End Time"


    # Extract project name from custom emoji
    icon_data = entry.get("icon", {})
    if icon_data and icon_data.get("type") == "custom_emoji":
        project_raw = icon_data["custom_emoji"]["name"]
        project = project_raw.split("-")[0].upper()  # Extract name before hyphen and uppercase
    else:
        project = "No Project"

    # Extract title
    title = entry["properties"]["Title / Reference Material (if any)"]["title"][0]["text"]["content"]

    # Extract event type
    event_type_list = entry["properties"]["Event Type"]["multi_select"]
    if event_type_list:
        event_type = ", ".join(tag["name"] for tag in event_type_list)
    else:
        event_type = "No Event Type"


    # Format date for today tasks
    formatted_date_today = f"{date_start.strftime('%Y/%m/%d %I:%M %p')} → {date_end}" if date_start else "No Start Time"

    # Format date for client meetings (include weekday)
    formatted_date_meeting = f"{date_start.strftime('%Y/%m/%d (%A) %I:%M %p')} → {date_end}" if date_start else "No Start Time"

    # Categorize tasks
    if date_start and date_start.date() == today.date():
        today_tasks.append((date_start, f"{formatted_date_today}, Project {project}, {title}, {event_type}"))
    elif date_start and today.date() <= date_start.date() <= end_of_week.date() and event_type == "Client Meeting":
        client_meetings.append((date_start, f"{formatted_date_meeting}, Project {project}, {title}"))

# Sort both lists by start time
today_tasks.sort(key=lambda x: x[0] if x[0] else datetime.max)
client_meetings.sort(key=lambda x: x[0] if x[0] else datetime.max)

# Format output
output_today = "\n".join(f"{i+1}. {task[1]}" for i, task in enumerate(today_tasks))
output_meetings = "\n".join(f"{i+1}. {meeting[1]}" for i, meeting in enumerate(client_meetings))

final_output = f"My agenda today:\n{output_today}\n\nMy upcoming client meetings:\n{output_meetings}" if client_meetings else f"My agenda today:\n{output_today}\n\nNo upcoming client meetings."

# print(final_output)



TELEGRAM_BOT_TOKEN = "7629770393:AAHtvtbixqbU-hFbJtOv1c4hnL9jp32Zdcs"
TELEGRAM_USER_ID = "5681725788"

def send_telegram_dm(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    requests.post(url, json=data)

# Send the agenda to your DM
send_telegram_dm(final_output)
