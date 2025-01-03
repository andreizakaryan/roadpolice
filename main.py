import requests
import re
from datetime import datetime, timedelta
import os

TARGET_DATE = "2025-03-14"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_notification(dates):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = f"Available Date: {', '.join(dates)}"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Error: {response.text}")


def get_dates():
    start_date = datetime.today()
    target_date = datetime.strptime(TARGET_DATE, "%Y-%m-%d")

    date_list = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range((target_date - start_date).days + 1)
        if (start_date + timedelta(days=i)).weekday() < 5  # Weekday is 0-4 for Mon-Fri
    ]

    session = requests.Session()
    response = session.get('https://roadpolice.am/hy/hqb')
    match = re.search(r'<meta name="csrf-token" content="(.*?)">', response.text)
    if match:
        csrf_token = match.group(1)
    else:
        print("CSRF token not found")
        return []

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://roadpolice.am/hy/hqb",
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest"
    }

    response = session.post(
        'https://roadpolice.am/hy/hqb-disabled-dates',
        data={
            'hqb_id': 1,
            'hqb_exam_status': 2
        },
        headers=headers
    )
    disabled_dates = response.json()['disabledDates']

    available_dates = []
    for date in date_list:
        if date not in disabled_dates:
            available_dates.append(date)
    return available_dates


def main():
    dates = get_dates()
    print(f"Dates: {dates}")
    if len(dates):
        send_notification(dates)


if __name__ == '__main__':
    main()
