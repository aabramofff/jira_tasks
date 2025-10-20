from db.db_connector import DBConnector
from reporting.formatter import ReportFormatter, JSONFormatter
import reporting.sql_queries as sq

class Reporter:
    """
    Класс, ответственный за выполнение аналитических SQL-запросов 
    и генерацию отчета.
    """
    def __init__(self, db_connector: DBConnector):
        self.db = db_connector

    def generate_report(self, output_format: str) -> str:
        """
        Выполняет все 4 запроса, собирает результаты и форматирует их.
        """
        print("\n--- Starting Report Generation ---")

        # 1. Сборка результатов
        report_data = {
            "students_per_room": self.db.fetch_all(sq.SQL_STUDENTS_PER_ROOM),
            "smallest_avg_age": self.db.fetch_all(sq.SQL_SMALLEST_AVG_AGE),
            "largest_age_diff": self.db.fetch_all(sq.SQL_LARGEST_AGE_DIFF),
            "mixed_sex_rooms": self.db.fetch_all(sq.SQL_MIXED_SEX_ROOMS),
        }
        
        # Фильтрация неудачных запросов
        for key in list(report_data.keys()):
            if report_data[key] is None:
                 print(f"REPORT ERROR: Failed to get data for {key}. Removing from report.")
                 del report_data[key]

        # 2. Выбор и использование форматера (DIP)
        formatter: ReportFormatter
        if output_format == 'json':
            formatter = JSONFormatter()
        else:
            raise ValueError(f"Unsupported format: {output_format}")

        print(f"REPORT: Formatting output as {output_format.upper()}.")
        return formatter.format(report_data)
