class DictionariesManager {
    constructor() {
        console.log('🔄 DictionariesManager initialized');
        this.currentDict = 'posts';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupModalHandlers();
    }

    setupEventListeners() {
        // Обработчики для навигационных вкладок
        document.querySelectorAll('.dict-nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const dictType = e.target.getAttribute('data-dict') ||
                    e.target.closest('.dict-nav-link').getAttribute('data-dict');
                this.switchDictionary(dictType);
            });
        });
    }

    setupModalHandlers() {
        console.log('🔄 Setting up modal handlers...');

        // Убираем старые обработчики onclick и добавляем новые
        this.setupAddButton('posts');
        this.setupAddButton('contracts');
        this.setupAddButton('inns');
        this.setupAddButton('agreement_persons');

        // Настраиваем обработчики форм
        this.setupFormHandlers();
    }

    setupAddButton(dictType) {
        const buttons = document.querySelectorAll(`[onclick*="showAddModal('${dictType}')"]`);
        console.log(`Found ${buttons.length} buttons for ${dictType}`);

        buttons.forEach(button => {
            // Убираем старый обработчик
            button.removeAttribute('onclick');

            // Добавляем новый обработчик
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log(`Button clicked for ${dictType}`);
                this.showAddModalSafe(dictType);
            });
        });
    }

    showAddModalSafe(dictType) {
        console.log(`🎯 Safe modal show for: ${dictType}`);

        const modalId = this.getModalId(dictType);
        const modalElement = document.getElementById(modalId);

        if (!modalElement) {
            console.error(`❌ Modal not found: ${modalId}`);
            this.showAlert(`Модальное окно не найдено: ${modalId}`, 'danger');
            return;
        }

        try {
            // Проверяем доступность Bootstrap
            if (typeof bootstrap === 'undefined' || typeof bootstrap.Modal === 'undefined') {
                throw new Error('Bootstrap не загружен');
            }

            // Создаем или получаем экземпляр модального окна
            let modal = bootstrap.Modal.getInstance(modalElement);
            if (!modal) {
                console.log('Creating new Bootstrap modal instance');
                modal = new bootstrap.Modal(modalElement, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });
            }

            // Показываем модальное окно
            modal.show();
            console.log(`✅ Modal shown successfully: ${modalId}`);

        } catch (error) {
            console.error(`❌ Error showing modal ${modalId}:`, error);
            this.showFallbackModal(modalElement);
        }
    }

    showFallbackModal(modalElement) {
        console.log('🔄 Using fallback modal display');

        // Простой показ модального окна без Bootstrap
        modalElement.style.display = 'block';
        modalElement.classList.add('show');
        modalElement.style.backgroundColor = 'rgba(0,0,0,0.5)';

        // Добавляем обработчик закрытия
        const closeModal = () => {
            modalElement.style.display = 'none';
            modalElement.classList.remove('show');
        };

        // Закрытие по клику на backdrop
        modalElement.addEventListener('click', function (e) {
            if (e.target === this) {
                closeModal();
            }
        });

        // Закрытие по кнопке
        const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"], .btn-close, .btn-secondary');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', closeModal);
        });
    }

    setupFormHandlers() {
        console.log('🔄 Setting up form handlers...');

        const forms = {
            'addPostForm': () => this.addPost(),
            'addContractForm': () => this.addContract(),
            'addInnForm': () => this.addInn(),
            'addAgreementPersonForm': () => this.addAgreementPerson()
        };

        Object.entries(forms).forEach(([formId, handler]) => {
            const form = document.getElementById(formId);
            if (form) {
                console.log(`✅ Found form: ${formId}`);
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    console.log(`📝 Form submitted: ${formId}`);
                    handler();
                });
            } else {
                console.log(`❌ Form not found: ${formId}`);
            }
        });
    }

    getModalId(dictType) {
        const modalIds = {
            'posts': 'addpostsModal',
            'contracts': 'addcontractsModal',
            'inns': 'addinnsModal',
            'agreement_persons': 'addagreement_personsModal'
        };
        return modalIds[dictType];
    }

    // Остальные методы остаются без изменений
    switchDictionary(dictType) {
        if (this.currentDict === dictType) return;

        // Обновляем активную вкладку
        document.querySelectorAll('.dict-nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-dict="${dictType}"]`).classList.add('active');

        // Скрываем все секции
        document.querySelectorAll('.dictionary-section').forEach(section => {
            section.classList.remove('active');
        });

        // Показываем выбранную секцию
        const targetSection = document.getElementById(`${dictType}Section`);
        targetSection.classList.add('active');

        this.currentDict = dictType;

        // Загружаем данные если они еще не загружены
        if (targetSection.getAttribute('data-loaded') === 'false') {
            this.loadDictionaryData(dictType);
        }
    }

    loadDictionaryData(dictType) {
        const container = document.getElementById(`${dictType}List`);
        const section = document.getElementById(`${dictType}Section`);

        // Показываем индикатор загрузки
        container.innerHTML = `
            <div class="list-group-item text-center text-muted py-4">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                Загрузка данных...
            </div>
        `;

        fetch(`/api/${dictType}`)
            .then(response => response.json())
            .then(data => {
                this.renderDictionaryList(dictType, data);
                section.setAttribute('data-loaded', 'true');
            })
            .catch(error => {
                console.error(`Ошибка загрузки ${dictType}:`, error);
                container.innerHTML = `
                    <div class="list-group-item text-center text-danger py-4">
                        <i class="bi bi-exclamation-triangle"></i><br>
                        Ошибка загрузки данных
                    </div>
                `;
            });
    }

    renderDictionaryList(dictType, items) {
        const container = document.getElementById(`${dictType}List`);

        if (!items || items.length === 0) {
            container.innerHTML = `
                <div class="list-group-item text-center text-muted py-4">
                    <i class="bi bi-inbox"></i><br>
                    Данные не найдены
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        items.forEach(item => {
            const itemElement = this.createDictionaryItem(dictType, item);
            container.appendChild(itemElement);
        });
    }

    createDictionaryItem(dictType, item) {
        const div = document.createElement('div');
        div.className = 'list-group-item d-flex justify-content-between align-items-center';

        switch (dictType) {
            case 'posts':
                div.innerHTML = `
                    <div>
                        <strong>${this.escapeHtml(item.name)}</strong>
                        ${item.description ? `<br><small class="text-muted">${this.escapeHtml(item.description)}</small>` : ''}
                    </div>
                    <div>
                        <button class="btn btn-sm btn-danger" onclick="dictManager.deleteItem('posts', ${item.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;
                break;

            case 'contracts':
                div.innerHTML = `
                    <div>
                        <strong>${this.escapeHtml(item.number)}</strong>
                        ${item.name ? `<br><small>${this.escapeHtml(item.name)}</small>` : ''}
                        <br><small class="text-muted">
                            ${item.start_date} - ${item.end_date || 'бессрочно'}
                        </small>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-danger" onclick="dictManager.deleteItem('contracts', ${item.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;
                break;

            case 'inns':
                div.innerHTML = `
                    <div>
                        <strong>${this.escapeHtml(item.inn)}</strong>
                        <br><small>${this.escapeHtml(item.organization_name)}</small>
                        ${item.contact_person ? `<br><small class="text-muted">${this.escapeHtml(item.contact_person)}</small>` : ''}
                    </div>
                    <div>
                        <button class="btn btn-sm btn-danger" onclick="dictManager.deleteItem('inns', ${item.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;
                break;

            case 'agreement_persons':
                div.innerHTML = `
                    <div>
                        <strong>${this.escapeHtml(item.full_name)}</strong>
                        ${item.position ? `<br><small>${this.escapeHtml(item.position)}</small>` : ''}
                        ${item.organization ? `<br><small class="text-muted">${this.escapeHtml(item.organization)}</small>` : ''}
                    </div>
                    <div>
                        <button class="btn btn-sm btn-danger" onclick="dictManager.deleteItem('agreement_persons', ${item.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;
                break;
        }

        return div;
    }

    deleteItem(dictType, itemId) {
        if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
            return;
        }

        fetch(`/api/${dictType}/${itemId}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    this.showAlert('Элемент успешно удален', 'success');
                    this.loadDictionaryData(dictType);
                } else {
                    this.showAlert(result.error || 'Ошибка при удалении', 'danger');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                this.showAlert('Ошибка при удалении', 'danger');
            });
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Методы добавления данных
    addPost() {
        const name = document.getElementById('postName').value.trim();
        const description = document.getElementById('postDescription').value.trim();

        if (!name) {
            this.showAlert('Введите название поста', 'warning');
            return;
        }

        fetch('/api/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description
            })
        })
            .then(response => response.json())
            .then(newPost => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addpostsModal'));
                if (modal) modal.hide();
                this.showAlert('Пост успешно добавлен', 'success');
                this.loadDictionaryData('posts');
            })
            .catch(error => {
                console.error('Ошибка:', error);
                this.showAlert('Ошибка при добавлении поста', 'danger');
            });
    }

    addContract() {
        const number = document.getElementById('contractNumber').value.trim();
        const name = document.getElementById('contractName').value.trim();
        const startDate = document.getElementById('contractStartDate').value;
        const endDate = document.getElementById('contractEndDate').value;
        const customer = document.getElementById('contractCustomer').value.trim();

        if (!number || !startDate) {
            this.showAlert('Заполните обязательные поля', 'warning');
            return;
        }

        fetch('/api/contracts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                number: number,
                name: name,
                start_date: startDate,
                end_date: endDate || null,
                customer: customer
            })
        })
            .then(response => response.json())
            .then(newContract => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addcontractsModal'));
                if (modal) modal.hide();
                this.showAlert('Договор успешно добавлен', 'success');
                this.loadDictionaryData('contracts');
            })
            .catch(error => {
                console.error('Ошибка:', error);
                this.showAlert('Ошибка при добавлении договора', 'danger');
            });
    }

    addInn() {
        const inn = document.getElementById('innNumber').value.trim();
        const organizationName = document.getElementById('organizationName').value.trim();

        if (!inn || !organizationName) {
            this.showAlert('Заполните обязательные поля', 'warning');
            return;
        }

        fetch('/api/inns', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                inn: inn,
                organization_name: organizationName,
                contact_person: document.getElementById('contactPerson').value.trim(),
                phone: document.getElementById('innPhone').value.trim(),
                email: document.getElementById('innEmail').value.trim()
            })
        })
            .then(response => response.json())
            .then(newInn => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addinnsModal'));
                if (modal) modal.hide();
                this.showAlert('ИНН успешно добавлен', 'success');
                this.loadDictionaryData('inns');
            })
            .catch(error => {
                console.error('Ошибка:', error);
                this.showAlert('Ошибка при добавлении ИНН', 'danger');
            });
    }

    addAgreementPerson() {
        const fullName = document.getElementById('agreementPersonName').value.trim();

        if (!fullName) {
            this.showAlert('Введите ФИО согласующего лица', 'warning');
            return;
        }

        fetch('/api/agreement_persons', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                full_name: fullName,
                position: document.getElementById('agreementPersonPosition').value.trim(),
                organization: document.getElementById('agreementPersonOrganization').value.trim(),
                phone: document.getElementById('agreementPersonPhone').value.trim(),
                email: document.getElementById('agreementPersonEmail').value.trim()
            })
        })
            .then(response => response.json())
            .then(newPerson => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addagreement_personsModal'));
                if (modal) modal.hide();
                this.showAlert('Согласующее лицо успешно добавлено', 'success');
                this.loadDictionaryData('agreement_persons');
            })
            .catch(error => {
                console.error('Ошибка:', error);
                this.showAlert('Ошибка при добавлении согласующего лица', 'danger');
            });
    }
}

// Инициализация менеджера справочников
let dictManager;

document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 DOM loaded, initializing DictionariesManager...');
    dictManager = new DictionariesManager();

    // Загружаем данные для активной вкладки
    setTimeout(() => {
        dictManager.loadDictionaryData('posts');
    }, 100);
});