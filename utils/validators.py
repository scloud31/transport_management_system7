import re
from datetime import datetime, date
from urllib.parse import urlparse

class Validators:
    
    @staticmethod
    def validate_required(value, field_name):
        """Проверка обязательного поля"""
        if not value or str(value).strip() == '':
            return f"Поле '{field_name}' обязательно для заполнения"
        return None
    
    @staticmethod
    def validate_email(email):
        """Валидация email"""
        if not email:
            return None
            
        # Простая валидация email через регулярное выражение
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return "Неверный формат email адреса"
        return None
    
    @staticmethod
    def validate_phone(phone, country='RU'):
        """Валидация номера телефона"""
        if not phone:
            return None
            
        # Упрощенная валидация телефона для России
        # Убираем все нецифровые символы
        clean_phone = re.sub(r'\D', '', phone)
        
        # Проверяем длину (10 или 11 цифр для России)
        if len(clean_phone) not in [10, 11]:
            return "Неверный формат номера телефона"
            
        # Проверяем код страны/оператора
        if len(clean_phone) == 11 and not clean_phone.startswith(('7', '8')):
            return "Неверный формат номера телефона"
            
        return None
    
    @staticmethod
    def validate_passport(series, number):
        """Валидация паспортных данных"""
        if series and number:
            if not re.match(r'^\d{4}$', str(series)):
                return "Серия паспорта должна содержать 4 цифры"
            if not re.match(r'^\d{6}$', str(number)):
                return "Номер паспорта должен содержать 6 цифр"
        return None
    
    @staticmethod
    def validate_license_plate(plate):
        """Валидация государственного номера"""
        if not plate:
            return None
            
        # Российский формат: A123BC123 или A123BC123
        pattern = r'^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$'
        if not re.match(pattern, plate.upper()):
            return "Неверный формат государственного номера"
        return None
    
    @staticmethod
    def validate_inn(inn):
        """Валидация ИНН"""
        if not inn:
            return None
            
        inn = str(inn).strip()
        
        if len(inn) not in (10, 12):
            return "ИНН должен содержать 10 или 12 цифр"
        
        if not inn.isdigit():
            return "ИНН должен содержать только цифры"
        
        # Упрощенная проверка (без контрольных цифр)
        return None
    
    @staticmethod
    def validate_date_range(start_date, end_date, field_names=('Дата начала', 'Дата окончания')):
        """Проверка корректности диапазона дат"""
        if start_date and end_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                
            if start_date > end_date:
                return f"{field_names[1]} не может быть раньше {field_names[0]}"
        return None
    
    @staticmethod
    def validate_future_date(date_value, field_name):
        """Проверка что дата в будущем"""
        if date_value:
            if isinstance(date_value, str):
                date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                
            if date_value < datetime.now().date():
                return f"{field_name} не может быть в прошлом"
        return None
    
    @staticmethod
    def validate_past_date(date_value, field_name):
        """Проверка что дата в прошлом"""
        if date_value:
            if isinstance(date_value, str):
                date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                
            if date_value > datetime.now().date():
                return f"{field_name} не может быть в будущем"
        return None
    
    @staticmethod
    def validate_file_extension(filename, allowed_extensions):
        """Проверка расширения файла"""
        if not filename:
            return None
            
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if file_ext not in allowed_extensions:
            return f"Недопустимый формат файла. Разрешены: {', '.join(allowed_extensions)}"
        return None
    
    @staticmethod
    def validate_file_size(file_size, max_size_mb):
        """Проверка размера файла"""
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return f"Размер файла превышает {max_size_mb}MB"
        return None
    
    @staticmethod
    def validate_numeric_range(value, min_value=None, max_value=None, field_name=''):
        """Проверка числового диапазона"""
        if value is None:
            return None
            
        try:
            num_value = float(value)
            errors = []
            
            if min_value is not None and num_value < min_value:
                errors.append(f"не может быть меньше {min_value}")
            
            if max_value is not None and num_value > max_value:
                errors.append(f"не может быть больше {max_value}")
            
            if errors:
                return f"{field_name} {', '.join(errors)}"
            return None
        except (ValueError, TypeError):
            return f"{field_name} должно быть числом"
    
    @staticmethod
    def validate_url(url):
        """Валидация URL"""
        if not url:
            return None
            
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                return None
            return "Неверный формат URL"
        except Exception:
            return "Неверный формат URL"
    
    @staticmethod
    def validate_password_strength(password):
        """Проверка сложности пароля"""
        if not password:
            return "Пароль не может быть пустым"
        
        if len(password) < 8:
            return "Пароль должен содержать минимум 8 символов"
        
        if not re.search(r'[A-Z]', password):
            return "Пароль должен содержать хотя бы одну заглавную букву"
        
        if not re.search(r'[a-z]', password):
            return "Пароль должен содержать хотя бы одну строчную букву"
        
        if not re.search(r'\d', password):
            return "Пароль должен содержать хотя бы одну цифру"
        
        return None

class ValidationResult:
    def __init__(self):
        self.errors = {}
        self.is_valid = True
    
    def add_error(self, field, error):
        self.errors[field] = error
        self.is_valid = False
    
    def get_errors(self):
        return self.errors
    
    def has_errors(self):
        return not self.is_valid