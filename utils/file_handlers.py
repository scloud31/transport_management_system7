import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import shutil

class FileHandler:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
    
    def save_employee_photo(self, photo_file):
        """Сохранение фото сотрудника"""
        if not photo_file or not photo_file.filename:
            return None
            
        # Генерация уникального имени файла
        file_ext = os.path.splitext(photo_file.filename)[1]
        filename = f"employee_{uuid.uuid4().hex}{file_ext}"
        filepath = os.path.join(self.upload_folder, 'photos', filename)
        
        try:
            # Сохранение файла
            photo_file.save(filepath)
            
            # Оптимизация изображения
            self._optimize_image(filepath)
            
            return f"photos/{filename}"
        except Exception as e:
            print(f"Ошибка сохранения фото: {e}")
            return None
    
    def save_document(self, document_file, document_type):
        """Сохранение документа"""
        if not document_file or not document_file.filename:
            return None
            
        filename = secure_filename(document_file.filename)
        filepath = os.path.join(self.upload_folder, 'documents', document_type, filename)
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            document_file.save(filepath)
            return f"documents/{document_type}/{filename}"
        except Exception as e:
            print(f"Ошибка сохранения документа: {e}")
            return None
    
    def save_template(self, template_file, template_type):
        """Сохранение шаблона документа"""
        if not template_file or not template_file.filename:
            return None
            
        file_ext = os.path.splitext(template_file.filename)[1]
        filename = f"{template_type}_{uuid.uuid4().hex}{file_ext}"
        filepath = os.path.join(self.upload_folder, 'templates', filename)
        
        try:
            template_file.save(filepath)
            return f"templates/{filename}"
        except Exception as e:
            print(f"Ошибка сохранения шаблона: {e}")
            return None
    
    def save_generated_document(self, document_content, filename, document_type):
        """Сохранение сгенерированного документа"""
        filepath = os.path.join(self.upload_folder, 'generated', document_type, filename)
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            if isinstance(document_content, bytes):
                with open(filepath, 'wb') as f:
                    f.write(document_content)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(document_content)
            
            return f"generated/{document_type}/{filename}"
        except Exception as e:
            print(f"Ошибка сохранения сгенерированного документа: {e}")
            return None
    
    def delete_file(self, file_path):
        """Удаление файла"""
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Ошибка удаления файла: {e}")
                return False
        return False
    
    def _optimize_image(self, image_path, max_size=(800, 800), quality=85):
        """Оптимизация изображения"""
        try:
            with Image.open(image_path) as img:
                # Изменение размера если нужно
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Конвертация в RGB если нужно
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Сохранение с оптимизацией
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
        except Exception as e:
            print(f"Ошибка оптимизации изображения: {e}")
    
    def get_file_size(self, file_path):
        """Получение размера файла"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    def cleanup_old_files(self, directory, max_age_days=30):
        """Очистка старых файлов"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_age = current_time - os.path.getctime(file_path)
                
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        print(f"Удален старый файл: {file_path}")
                    except Exception as e:
                        print(f"Ошибка удаления файла {file_path}: {e}")