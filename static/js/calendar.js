class Calendar {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentDate = new Date();
        this.selectedDate = new Date();
        this.events = this.loadEvents();
        this.init();
    }

    init() {
        this.render();
        this.loadHolidays();
    }

    render() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const monthNames = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ];

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDay = firstDay.getDay();

        // Корректировка для понедельника как первого дня недели
        const startOffset = startingDay === 0 ? 6 : startingDay - 1;

        let calendarHTML = `
            <div class="calendar-header mb-3">
                <div class="row align-items-center">
                    <div class="col">
                        <h4 class="mb-0">${monthNames[month]} ${year}</h4>
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-sm btn-outline-primary" onclick="calendar.prevMonth()">
                            <i class="bi bi-chevron-left"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-primary" onclick="calendar.nextMonth()">
                            <i class="bi bi-chevron-right"></i>
                        </button>
                    </div>
                </div>
            </div>

            <div class="calendar-grid">
                <div class="calendar-weekdays">
                    ${this.getWeekdays().map(day => `<div class="calendar-weekday">${day}</div>`).join('')}
                </div>
                <div class="calendar-days">
        `;

        // Пустые ячейки перед первым днем месяца
        for (let i = 0; i < startOffset; i++) {
            calendarHTML += `<div class="calendar-day empty"></div>`;
        }

        // Дни месяца
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const isToday = this.isSameDay(date, today);
            const isSelected = this.isSameDay(date, this.selectedDate);
            const isWeekend = date.getDay() === 0 || date.getDay() === 6;
            const hasEvents = this.hasEvents(date);
            const dayEvents = this.getEventsForDate(date);

            let dayClass = 'calendar-day';
            if (isToday) dayClass += ' today';
            if (isSelected) dayClass += ' selected';
            if (isWeekend) dayClass += ' weekend';
            if (hasEvents) dayClass += ' has-events';

            calendarHTML += `
                <div class="${dayClass}" onclick="calendar.selectDate(${year}, ${month}, ${day})">
                    <div class="day-number">${day}</div>
                    ${hasEvents ? `<div class="day-events">${dayEvents.map(event => 
                        `<span class="event-dot" style="background-color: ${event.color}" title="${event.title}"></span>`
                    ).join('')}</div>` : ''}
                </div>
            `;
        }

        calendarHTML += `
                </div>
            </div>

            <div class="calendar-events mt-3">
                <h6>События на ${this.selectedDate.toLocaleDateString('ru-RU')}:</h6>
                <div id="dayEvents">
                    ${this.renderDayEvents()}
                </div>
            </div>
        `;

        this.container.innerHTML = calendarHTML;
    }

    getWeekdays() {
        return ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    }

    isSameDay(date1, date2) {
        return date1.getDate() === date2.getDate() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getFullYear() === date2.getFullYear();
    }

    prevMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.render();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.render();
    }

    selectDate(year, month, day) {
    this.selectedDate = new Date(year, month, day);
    this.render();
    
    // Показываем модальное окно добавления события при двойном клике
    setTimeout(() => {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        CalendarEvents.showAddEventModal(dateStr);
    }, 300);
    }

    hasEvents(date) {
        return this.events.some(event => this.isSameDay(new Date(event.date), date));
    }

    getEventsForDate(date) {
        return this.events.filter(event => this.isSameDay(new Date(event.date), date));
    }

    renderDayEvents() {
        const events = this.getEventsForDate(this.selectedDate);
        if (events.length === 0) {
            return '<p class="text-muted">Нет событий</p>';
        }

        return events.map(event => `
            <div class="event-item p-2 mb-2 border rounded" style="border-left: 4px solid ${event.color} !important;">
                <div class="d-flex justify-content-between align-items-center">
                    <strong>${event.title}</strong>
                    <small class="text-muted">${event.time || ''}</small>
                </div>
                ${event.description ? `<small class="text-muted">${event.description}</small>` : ''}
            </div>
        `).join('');
    }

    loadEvents() {
        // Загрузка событий из localStorage или базы данных
        const savedEvents = localStorage.getItem('calendarEvents');
        if (savedEvents) {
            return JSON.parse(savedEvents);
        }

        // Пример событий по умолчанию
        return [
            {
                date: new Date().toISOString().split('T')[0],
                title: 'Текущий день',
                color: '#007bff',
                description: 'Сегодняшний день'
            }
        ];
    }

    saveEvents() {
        localStorage.setItem('calendarEvents', JSON.stringify(this.events));
    }

    addEvent(event) {
        this.events.push(event);
        this.saveEvents();
        this.render();
    }

    loadHolidays() {
        // Загрузка праздников (можно расширить)
        const currentYear = this.currentDate.getFullYear();
        const holidays = [
            { date: `${currentYear}-01-01`, title: 'Новый год', color: '#dc3545' },
            { date: `${currentYear}-01-07`, title: 'Рождество', color: '#dc3545' },
            { date: `${currentYear}-02-23`, title: 'День защитника Отечества', color: '#dc3545' },
            { date: `${currentYear}-03-08`, title: 'Международный женский день', color: '#dc3545' },
            { date: `${currentYear}-05-01`, title: 'Праздник весны и труда', color: '#dc3545' },
            { date: `${currentYear}-05-09`, title: 'День Победы', color: '#dc3545' },
            { date: `${currentYear}-06-12`, title: 'День России', color: '#dc3545' },
            { date: `${currentYear}-11-04`, title: 'День народного единства', color: '#dc3545' }
        ];

        holidays.forEach(holiday => {
            if (!this.events.some(e => e.date === holiday.date)) {
                this.events.push(holiday);
            }
        });
    }
}

// Инициализация календаря когда DOM загружен
document.addEventListener('DOMContentLoaded', function() {
    window.calendar = new Calendar('calendar');
});