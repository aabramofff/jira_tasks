import json
from abc import ABC, abstractmethod
from decimal import Decimal;

class ReportFormatter(ABC):
    """Абстрактный интерфейс для форматирования отчетов."""
    @abstractmethod
    def format(self, report_data: dict) -> str:
        pass

class JSONFormatter(ReportFormatter):
    """Форматирует отчет в JSON."""
    
    def default_serializer(self, obj):
        """
        Вспомогательная функция для обработки нестандартных типов данных.
        """
        if isinstance(obj, Decimal):
            # Преобразуем Decimal в float. 
            # Это может потерять часть точности, но совместимо с JSON.
            return float(obj)
        
        # Если это другой неизвестный тип, поднимаем стандартное исключение
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def format(self, report_data: dict) -> str:
        """
        Использует вспомогательную функцию для корректной сериализации.
        """
        # Передаем default_serializer в качестве параметра 'default'
        return json.dumps(
            report_data, 
            indent=4, 
            ensure_ascii=False,
            default=self.default_serializer # <--- Ключевое изменение
        )
