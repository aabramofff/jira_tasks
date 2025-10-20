import psycopg2
from psycopg2 import sql # Импорт не используется напрямую, но хорошая практика для безопасности SQL

class DBConnector:
    """
    Класс для управления подключением и выполнением SQL-запросов к PostgreSQL.
    
    Соответствует принципу SRP (Single Responsibility Principle), 
    отвечая исключительно за низкоуровневое взаимодействие с базой данных.
    """
    def __init__(self, db_config):
        """
        Инициализация соединения с БД.
        """
        self.connection = None
        self.cursor = None

        try:
            # psycopg2.connect() устанавливает соединение, используя параметры из словаря db_config.
            self.connection = psycopg2.connect(**db_config)
            # Создание объекта курсора для выполнения команд
            self.cursor = self.connection.cursor()
            print("DB: Connected successfully")
        except psycopg2.Error as e:
            # Обработка ошибки подключения к БД
            print(f"DB ERROR: Couldn't connect to PostgreSQL. {e}")
            # Поднимаем исключение ConnectionError, чтобы остановить программу, если БД недоступна
            raise ConnectionError("Failed to connect to database.")

    def execute_many(self, query: str, data: list) -> bool:
        """
        Выполнение пакета (BULK) вставок с использованием executemany.
        """
        # Проверка наличия соединения и данных для вставки
        if not self.connection or not data:
            return False
        
        try:
            # executemany выполняет запрос один раз, но применяет его ко всем записям
            self.cursor.executemany(query, data)
            # Обязательная фиксация изменений в БД
            self.connection.commit()
            return True
        except psycopg2.Error as e:
            # Откат изменений в случае ошибки, чтобы не оставлять БД в несогласованном состоянии
            self.connection.rollback()
            print(f"DB ERROR: Batch insert failed: {e}")
            return False
        
    def fetch_all(self, query: str) -> list | None:
        """
        Выполняет SELECT-запрос и возвращает все результаты.
        """
        if not self.connection:
            return None
    
        try:
            # Выполнение запроса
            self.cursor.execute(query)
            
            # Получение имен столбцов из метаданных курсора
            columns = [desc[0] for desc in self.cursor.description]
            # Получение всех строк
            data = self.cursor.fetchall()
            
            # Преобразование: список кортежей -> список словарей для удобства работы в Python
            return [dict(zip(columns, row)) for row in data]
        except psycopg2.Error as e:
            # Обработка ошибки выполнения SELECT-запроса
            print(f"DB ERROR: Failed to fetch data: {e}")
            return None
        
    def execute_ddl(self, query: str) -> bool:
        """
        Выполняет один запрос DDL (Data Definition Language, например, CREATE INDEX).
        """
        if not self.connection:
            return False
        try:
            self.cursor.execute(query)
            # DDL-запросы также требуют commit
            self.connection.commit()
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            # Выводим ошибку, но позволяем программе продолжить работу, если это не критично
            print(f"DB ERROR: DDL failed: {e}")
            return False
        
    def close(self):
        """
        Закрывает курсор и соединение с БД.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("DB: Connection closed.")
