from db.db_connector import DBConnector
from data_loading.data_reader import DataReader
# Импорт SQL-констант для вставки данных
from reporting.sql_queries import SQL_ROOMS_INSERTION, SQL_STUDENTS_INSERTION

class DataProcessor:
    """
    Класс-процессор, отвечающий за логику ETL-загрузки (Extract, Transform, Load) 
    из файлов в базу данных.
    
    Соответствует принципу SRP (Single Responsibility Principle): 
    оркестрация и преобразование данных.
    """
    def __init__(self, db_connector: DBConnector, data_reader: DataReader):
        # Композиция: DataProcessor зависит от абстракций DBConnector и DataReader.
        # Это соответствует принципу DIP (Dependency Inversion Principle).
        self.db = db_connector
        self.reader = data_reader

    def load_data(self, rooms_path: str, students_path: str) -> None:
        """
        Основной метод загрузки данных.
        
        Args:
            rooms_path (str): Путь к файлу с данными комнат.
            students_path (str): Путь к файлу с данными студентов.
        """
        print("\n--- Starting Data Load ---")
        
        # 1. Загрузка комнат (родительская таблица)
        # Этот шаг должен идти первым, чтобы удовлетворить ограничение FOREIGN KEY
        # при вставке данных студентов.
        rooms_data = self.reader.read(rooms_path)
        if rooms_data:
            self.db.execute_many(SQL_ROOMS_INSERTION, self._prepare_rooms_data(rooms_data))

        # 2. Загрузка студентов (дочерняя таблица)
        students_data = self.reader.read(students_path)
        if students_data:
            self.db.execute_many(SQL_STUDENTS_INSERTION, self._prepare_students_data(students_data))

        print("--- Data Load Complete ---\n")

    def _prepare_rooms_data(self, data: list) -> list:
        """
        Преобразует список словарей комнат в список кортежей, 
        готовый для пакетной вставки в SQL.
        """
        # Преобразование в список кортежей: [(id, name), ...]
        return [(r['id'], r['name']) for r in data]
    
    def _prepare_students_data(self, data: list) -> list:
        """
        Преобразует список словарей студентов в список кортежей.
        
        Осуществляет "Transform" часть ETL: сопоставление полей JSON с БД.
        JSON поля: 'id', 'name', 'birthday', 'sex', 'room'
        BD столбцы: id, name, birthday, sex, room_id
        """
        # Преобразование в список кортежей. ВАЖНО: 'room' из JSON 
        # сопоставляется с 'room_id' в SQL-запросе.
        return [
            (s['id'], s['name'], s['birthday'], s['sex'], s['room'])
            for s in data
        ]

    def _insert_rooms(self, data: list) -> None:
        """
        Выполняет пакетную вставку данных комнат.
        """
        prepared_data = self._prepare_rooms_data(data)
        if self.db.execute_many(SQL_ROOMS_INSERTION, prepared_data):
            print(f"PROCESSOR: Successfully inserted {len(prepared_data)} rooms.")

    def _insert_students(self, data: list) -> None:
        """
        Выполняет пакетную вставку данных студентов.
        """
        prepared_data = self._prepare_students_data(data)
        if self.db.execute_many(SQL_STUDENTS_INSERTION, prepared_data):
            print(f"PROCESSOR: Successfully inserted {len(prepared_data)} students.")
