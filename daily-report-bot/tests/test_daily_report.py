import importlib.util
import os
import pathlib
import tempfile
import unittest

from openpyxl import load_workbook

module_path = pathlib.Path(__file__).resolve().parents[1] / "file_name.py"
spec = importlib.util.spec_from_file_location("daily_report_bot", module_path)
daily_report_bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daily_report_bot)


class DailyReportWorkbookTests(unittest.TestCase):
    def test_create_report_workbook_writes_expected_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workbook_path = daily_report_bot.create_report_workbook(
                weather_text="Sunny",
                comment="Great day",
                output_dir=tmpdir,
            )

            self.assertTrue(os.path.exists(workbook_path))
            self.assertTrue(workbook_path.endswith(".xlsx"))

            workbook = load_workbook(workbook_path)
            sheet = workbook.active
            self.assertEqual(sheet["A1"].value, "Date")
            self.assertEqual(sheet["B1"].value, "Weather")
            self.assertEqual(sheet["C1"].value, "Comment")
            self.assertEqual(sheet["A2"].value, daily_report_bot.datetime.now().strftime("%Y-%m-%d"))
            self.assertEqual(sheet["B2"].value, "Sunny")
            self.assertEqual(sheet["C2"].value, "Great day")


if __name__ == "__main__":
    unittest.main()
