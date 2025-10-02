import argparse
import sys

# Импорты модулей проекта
from config import DB_CONFIG
from db.db_connector import DBConnector
from data_loading.data_reader import JSONReader
from data_loading.data_processor import DataProcessor
from reporting.reporter import Reporter
from reporting.sql_queries import SQL_CREATE_INDEXES # Для оптимизации

def main():
    """
    Парсинг аргументов и основная логика работы скрипта.
    """
    # 1. Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="University Data Loader and Reporter.")
    parser.add_argument('--students', type=str, required=True, help="Path to the students JSON file.")
    parser.add_argument('--rooms', type=str, required=True, help="Path to the rooms JSON file.")
    parser.add_argument('--format', choices=['xml', 'json'], required=True, help="Output format: xml or json.")
    
    args = parser.parse_args()

    # 2. Инициализация ключевых компонентов
    db_connector: DBConnector = None
    try:
        # Устанавливаем соединение с БД
        db_connector = DBConnector(DB_CONFIG)
        json_reader = JSONReader()
        
        # 3. Загрузка данных
        processor = DataProcessor(db_connector, json_reader)
        processor.load_data(args.rooms, args.students)

        # 4. Оптимизация (Создание индексов)
        print("DB: Applying indexes for query optimization...")
        db_connector.execute_ddl(SQL_CREATE_INDEXES)

        # 5. Генерация отчета
        reporter = Reporter(db_connector)
        report = reporter.generate_report(args.format)
        
        # 6. Вывод результата (stdout)
        print("\n" + "="*20 + " FINAL REPORT " + "="*20)
        print(report)
        print("="*54 + "\n")

    except ConnectionError:
        print("FATAL ERROR: Shutting down due to database connection failure.")
        sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: An unhandled exception occurred: {e}")
        sys.exit(1)
    finally:
        # Гарантированное закрытие соединения, даже при ошибке
        if db_connector:
            db_connector.close()


if __name__ == "__main__":
    main()
