// Дополнительные функции для работы с событиями календаря
class CalendarEvents {
    static showAddEventModal(date) {
        const modalHTML = `
            <div class="modal fade" id="addEventModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Добавить событие</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addEventForm">
                                <div class="mb-3">
                                    <label class="form-label">Дата</label>
                                    <input type="date" class="form-control" name="eventDate" value="${date}" readonly>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Название события *</label>
                                    <input type="text" class="form-control" name="eventTitle" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Время</label>
                                    <input type="time" class="form-control" name="eventTime">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Описание</label>
                                    <textarea class="form-control" name="eventDescription" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Цвет</label>
                                    <select class="form-select" name="eventColor">
                                        <option value="#007bff">Синий</option>
                                        <option value="#28a745">Зеленый</option>
                                        <option value="#dc3545">Красный</option>
                                        <option value="#ffc107">Желтый</option>
                                        <option value="#6f42c1">Фиолетовый</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                            <button type="button" class="btn btn-success" onclick="CalendarEvents.saveEvent()">Сохранить</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        const modal = new bootstrap.Modal(document.getElementById('addEventModal'));
        modal.show();

        // Удаляем модальное окно после закрытия
        document.getElementById('addEventModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    static saveEvent() {
        const form = document.getElementById('addEventForm');
        if (form.checkValidity()) {
            const formData = new FormData(form);
            const event = {
                date: formData.get('eventDate'),
                title: formData.get('eventTitle'),
                time: formData.get('eventTime'),
                description: formData.get('eventDescription'),
                color: formData.get('eventColor')
            };

            if (window.calendar) {
                window.calendar.addEvent(event);
            }

            bootstrap.Modal.getInstance(document.getElementById('addEventModal')).hide();
        } else {
            form.reportValidity();
        }
    }
}

// Добавляем контекстное меню для дней календаря
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('contextmenu', function(e) {
        if (e.target.closest('.calendar-day:not(.empty)')) {
            e.preventDefault();
            const dayElement = e.target.closest('.calendar-day');
            const dayNumber = dayElement.querySelector('.day-number').textContent;
            const year = window.calendar.currentDate.getFullYear();
            const month = window.calendar.currentDate.getMonth();
            const date = `${year}-${String(month + 1).padStart(2, '0')}-${String(dayNumber).padStart(2, '0')}`;
            
            CalendarEvents.showAddEventModal(date);
        }
    });
});