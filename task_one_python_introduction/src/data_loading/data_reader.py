# src/data_loading/data_reader.py

import json
from abc import ABC, abstractmethod

class DataReader(ABC):
    """Абстрактный класс для чтения данных."""
    @abstractmethod
    def read(self, file_path: str) -> list | None:
        pass

class JSONReader(DataReader):
    """
    Чистая реализация для чтения и парсинга JSON-файлов.
    Использует стандартный UTF-8.
    """
    def read(self, file_path: str) -> list | None:
        """Читает и парсит JSON-файл в список словарей."""
        try:
            # Используем стандартное открытие файла в текстовом режиме ('r') с UTF-8.
            # Если файлы чистые, этот код работает быстрее и без ошибок.
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                print(f"READER: Successfully read {len(data)} records from {file_path}.")
                return data
            else:
                print(f"READER ERROR: File {file_path} does not contain a list.")
                return None

        except FileNotFoundError:
            print(f"READER ERROR: File not found at path: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"READER ERROR: Invalid JSON format in file: {file_path}. {e}")
            return None
        except Exception as e:
            # Общий обработчик для непредвиденных ошибок чтения/доступа
            print(f"READER ERROR: An unexpected error occurred: {e}")
            return None