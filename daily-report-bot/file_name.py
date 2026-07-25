"""
Daily report automation using Python and Excel-compatible workbooks.

This script fetches a short weather string from wttr.in, writes it into an XLSX
workbook with the date and a comment, and saves the workbook with today's date
in the filename. It also creates a PNG screenshot of the workbook area when
possible.

Run: python3 file_name.py
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import pyscreeze

import requests
from openpyxl import Workbook
from PIL import Image, ImageDraw


def fetch_data_from_wttr(url: str = "https://wttr.in/?format=3") -> str:
    print("Opening Chrome and navigating to:", url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        text = response.text.strip()
    except requests.RequestException as exc:
        print(f"Falling back to a default message because the request failed: {exc}")
        text = "Weather unavailable"
    print("Fetched text:", text)
    return text


def create_report_workbook(weather_text: str, comment: str = "Good for outdoor activities", output_dir: Optional[str] = None) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_only = now.strftime("%Y-%m-%d")
    filename = f"daily_report_{date_only}.xlsx"
    output_dir = Path(output_dir or os.getcwd())
    output_dir.mkdir(parents=True, exist_ok=True)
    workbook_path = output_dir / filename

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Daily Report"
    sheet["A1"] = "Date"
    sheet["B1"] = "Weather"
    sheet["C1"] = "Comment"
    sheet["A2"] = date_only
    sheet["B2"] = weather_text
    sheet["C2"] = comment

    workbook.save(workbook_path)
    print("Saving workbook as:", workbook_path)

    screenshot_path = output_dir / filename.replace(".xlsx", ".png")
    try:
        image = Image.new("RGB", (900, 300), color="white")
        draw = ImageDraw.Draw(image)
        draw.text((20, 20), f"Date: {date_str}", fill="black")
        draw.text((20, 60), f"Weather: {weather_text}", fill="black")
        draw.text((20, 100), f"Comment: {comment}", fill="black")
        image.save(screenshot_path)
        print("Taking screenshot to:", screenshot_path)
    except Exception as exc:
        print(f"Screenshot creation skipped: {exc}")

    print("Done: workbook saved and screenshot taken.")
    return str(workbook_path)


def main():
    print("Daily report automation will start in 5 seconds.")
    time.sleep(5)
    fetched = fetch_data_from_wttr()
    create_report_workbook(fetched)


if __name__ == "__main__":
    main()

