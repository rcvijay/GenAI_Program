Student Grade System — Setup and Run Instructions (macOS)

Prerequisites:
- Python 3.x installed (use `python3 --version` to check).

Setup:
1. Open the Terminal app and change to the project directory:

	cd /path/to/StudentGradeSystem

2. Create a virtual environment (recommended):

	python3 -m venv venv

3. Activate the virtual environment:

	source venv/bin/activate

	After activation your prompt should include `(venv)`.

4. (Optional) Install dependencies if a `requirements.txt` exists:

	pip install -r requirements.txt

Run the program:

With the virtual environment activated, run:

	python3 garde-system.py

Notes:
- Do not use `sudo su` or run the program as root — it's unnecessary and unsafe for this workflow.
- If the script filename is different (for example `grade-system.py`), use that filename instead.
