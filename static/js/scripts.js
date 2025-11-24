// Основные JavaScript функции для системы

// Инициализация tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Функция для подтверждения удаления
function confirmAction(message, callback) {
    if (confirm(message)) {
        if (typeof callback === 'function') {
            callback();
        }
        return true;
    }
    return false;
}

// Работа с датами
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

// Валидация форм
function validateForm(formId) {
    const form = document.getElementById(formId);
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// API функции для работы со справочниками
class DictionaryAPI {
    static async addItem(endpoint, data) {
        try {
            const response = await fetch(`/api/${endpoint}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Ошибка добавления:', error);
            return null;
        }
    }

    static async deleteItem(endpoint, id) {
        try {
            const response = await fetch(`/api/${endpoint}/${id}`, {
                method: 'DELETE'
            });
            return await response.json();
        } catch (error) {
            console.error('Ошибка удаления:', error);
            return null;
        }
    }
}

// Утилиты для работы с файлами
class FileUtils {
    static previewImage(input, previewId) {
        const file = input.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.getElementById(previewId);
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
            reader.readAsDataURL(file);
        }
    }

    static validateFileSize(input, maxSizeMB) {
        const file = input.files[0];
        if (file && file.size > maxSizeMB * 1024 * 1024) {
            alert(`Файл слишком большой. Максимальный размер: ${maxSizeMB}MB`);
            input.value = '';
            return false;
        }
        return true;
    }
}

// Поиск и фильтрация в таблицах
class TableFilter {
    static initSearch(inputId, tableSelector) {
        const input = document.getElementById(inputId);
        if (!input) return;

        input.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const rows = document.querySelectorAll(`${tableSelector} tbody tr`);
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }

    static initSelectFilter(selectId, columnIndex, tableSelector) {
        const select = document.getElementById(selectId);
        if (!select) return;

        select.addEventListener('change', function() {
            const filterValue = this.value;
            const rows = document.querySelectorAll(`${tableSelector} tbody tr`);
            
            rows.forEach(row => {
                const cell = row.cells[columnIndex];
                const cellText = cell.textContent.trim();
                
                if (!filterValue || cellText === filterValue) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}
// Дополнительные функции для работы со временем
class TimeManager {
    static initTimeSensitiveElements() {
        // Обновляем все элементы с временными метками на странице
        this.updateTimeElements();
        
        // Запускаем периодическое обновление
        setInterval(() => this.updateTimeElements(), 60000); // Каждую минуту
    }

    static updateTimeElements() {
        // Находим все элементы с атрибутами времени
        const timeElements = document.querySelectorAll('[data-time]');
        
        timeElements.forEach(element => {
            const timestamp = element.getAttribute('data-time');
            const format = element.getAttribute('data-time-format') || 'relative';
            
            if (timestamp) {
                const date = new Date(timestamp);
                element.textContent = this.formatTime(date, format);
                
                // Добавляем всплывающую подсказку с полной датой
                element.title = date.toLocaleString('ru-RU');
            }
        });
    }

    static formatTime(date, format) {
        const now = new Date();
        const diff = now - date;
        const diffMinutes = Math.floor(diff / (1000 * 60));
        const diffHours = Math.floor(diff / (1000 * 60 * 60));
        const diffDays = Math.floor(diff / (1000 * 60 * 60 * 24));

        switch (format) {
            case 'relative':
                if (diffMinutes < 1) return 'только что';
                if (diffMinutes < 60) return `${diffMinutes} мин. назад`;
                if (diffHours < 24) return `${diffHours} ч. назад`;
                if (diffDays < 7) return `${diffDays} дн. назад`;
                return date.toLocaleDateString('ru-RU');
            
            case 'datetime':
                return date.toLocaleString('ru-RU');
            
            case 'date':
                return date.toLocaleDateString('ru-RU');
            
            case 'time':
                return date.toLocaleTimeString('ru-RU', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
            
            default:
                return date.toLocaleString('ru-RU');
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    TimeManager.initTimeSensitiveElements();
});