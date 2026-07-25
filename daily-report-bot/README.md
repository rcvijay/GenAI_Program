# Daily Report Bot (PyAutoGUI)

This script automates creating a daily status report by fetching a short weather
summary, writing it to an Excel-compatible workbook, and saving a PNG snapshot of
the generated content.

What it does

- Fetches a short weather string from `https://wttr.in/?format=3`.
- Creates an Excel-compatible workbook with the date, the fetched text, and a short comment.
- Saves the workbook as `daily_report_YYYY-MM-DD.xlsx` in the current folder.
- Writes a simple PNG snapshot of the generated report as `daily_report_YYYY-MM-DD.png`.

Requirements

- Python 3.8+.
- Install dependencies:

```
pip install -r requirements.txt
```

Run

```
python3 file_name.py
```

Notes and limitations

- The script uses a direct workbook writer rather than UI automation, so it works
  without Microsoft Excel being installed.
- Network access is required for the weather fetch; if it fails, the script uses a
  fallback message.
