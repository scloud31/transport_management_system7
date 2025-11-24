class RealTimeClock {
    constructor() {
        this.timeElement = document.getElementById('current-time');
        this.is12HourFormat = false;
        this.showSeconds = true;
        this.init();
    }

    init() {
        this.updateTime();
        // Обновляем время каждую секунду
        setInterval(() => this.updateTime(), 1000);
        
        // Добавляем обработчик клика для смены формата времени
        this.timeElement.style.cursor = 'pointer';
        this.timeElement.title = 'Кликните для смены формата времени';
        this.timeElement.addEventListener('click', () => this.toggleFormat());
    }

    updateTime() {
        const now = new Date();
        let timeString;

        if (this.is12HourFormat) {
            // 12-часовой формат (AM/PM)
            let hours = now.getHours();
            const minutes = now.getMinutes();
            const seconds = now.getSeconds();
            const ampm = hours >= 12 ? 'PM' : 'AM';
            
            hours = hours % 12;
            hours = hours ? hours : 12; // 0 часов становится 12
            
            if (this.showSeconds) {
                timeString = `${this.padZero(hours)}:${this.padZero(minutes)}:${this.padZero(seconds)} ${ampm}`;
            } else {
                timeString = `${this.padZero(hours)}:${this.padZero(minutes)} ${ampm}`;
            }
        } else {
            // 24-часовой формат
            const hours = now.getHours();
            const minutes = now.getMinutes();
            const seconds = now.getSeconds();
            
            if (this.showSeconds) {
                timeString = `${this.padZero(hours)}:${this.padZero(minutes)}:${this.padZero(seconds)}`;
            } else {
                timeString = `${this.padZero(hours)}:${this.padZero(minutes)}`;
            }
        }

        const dateString = now.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            weekday: 'long'
        });

        this.timeElement.innerHTML = `
            <i class="bi bi-clock"></i> 
            ${dateString} | 
            <strong>${timeString}</strong>
        `;
    }

    padZero(number) {
        return number.toString().padStart(2, '0');
    }

    toggleFormat() {
        this.is12HourFormat = !this.is12HourFormat;
        this.updateTime();
        
        // Показываем уведомление о смене формата
        this.showFormatNotification();
    }

    showFormatNotification() {
        // Создаем временное уведомление
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
        notification.style.cssText = `
            top: 80px;
            right: 20px;
            z-index: 1060;
            min-width: 300px;
        `;
        notification.innerHTML = `
            <i class="bi bi-info-circle"></i>
            Формат времени изменен на ${this.is12HourFormat ? '12-часовой' : '24-часовой'}
            <button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматически скрываем через 3 секунды
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    // Дополнительные методы для управления отображением
    setShowSeconds(show) {
        this.showSeconds = show;
        this.updateTime();
    }

    getCurrentTimestamp() {
        return new Date();
    }

    // Метод для форматирования времени для использования в других частях приложения
    static formatTime(date, includeSeconds = true) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        
        if (includeSeconds) {
            return `${hours}:${minutes}:${seconds}`;
        } else {
            return `${hours}:${minutes}`;
        }
    }

    static formatDate(date) {
        return date.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            weekday: 'long'
        });
    }
}

// Инициализация часов при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    window.realTimeClock = new RealTimeClock();
});

// Дополнительные утилиты для работы со временем
const TimeUtils = {
    // Расчет разницы между двумя датами
    getTimeDifference(startDate, endDate) {
        const diff = endDate - startDate;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        return {
            days: days,
            hours: hours % 24,
            minutes: minutes % 60,
            seconds: seconds % 60,
            totalSeconds: seconds,
            totalMinutes: minutes,
            totalHours: hours,
            totalDays: days
        };
    },

    // Форматирование длительности
    formatDuration(duration) {
        const parts = [];
        
        if (duration.days > 0) {
            parts.push(`${duration.days} д.`);
        }
        if (duration.hours > 0) {
            parts.push(`${duration.hours} ч.`);
        }
        if (duration.minutes > 0) {
            parts.push(`${duration.minutes} мин.`);
        }
        if (duration.seconds > 0 && parts.length === 0) {
            parts.push(`${duration.seconds} сек.`);
        }

        return parts.join(' ') || '0 сек.';
    },

    // Проверка рабочего времени (9:00-18:00)
    isWorkingTime(date = new Date()) {
        const hours = date.getHours();
        return hours >= 9 && hours < 18;
    },

    // Проверка выходного дня
    isWeekend(date = new Date()) {
        const day = date.getDay();
        return day === 0 || day === 6; // 0 - воскресенье, 6 - суббота
    },

    // Добавление дней к дате
    addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    },

    // Получение начала дня
    startOfDay(date = new Date()) {
        const result = new Date(date);
        result.setHours(0, 0, 0, 0);
        return result;
    },

    // Получение конца дня
    endOfDay(date = new Date()) {
        const result = new Date(date);
        result.setHours(23, 59, 59, 999);
        return result;
    }
};
// Обновление заголовка вкладки с временем (опционально)
class TabTitleUpdater {
    constructor() {
        this.originalTitle = document.title;
        this.isEnabled = false;
    }

    enable() {
        this.isEnabled = true;
        this.updateTitle();
        setInterval(() => this.updateTitle(), 1000);
    }

    disable() {
        this.isEnabled = false;
        document.title = this.originalTitle;
    }

    updateTitle() {
        if (!this.isEnabled) return;
        
        const now = new Date();
        const timeString = RealTimeClock.formatTime(now, true);
        document.title = `[${timeString}] ${this.originalTitle}`;
    }
}

// Инициализация обновления заголовка (раскомментируйте для включения)
document.addEventListener('DOMContentLoaded', function() {
    window.tabTitleUpdater = new TabTitleUpdater();
    window.tabTitleUpdater.enable();
});