class MultiSelectTag {
    constructor(selectId, options = {}) {
        this.select = document.getElementById(selectId);
        this.options = Object.assign({
            rounded: false,
            shadow: false,
            placeholder: 'Select options'
        }, options);

        this.init();
    }

    init() {
        if (!this.select) return;

        // Создаем контейнер для мультиселекта
        this.container = document.createElement('div');
        this.container.className = 'multiselect-container';
        if (this.options.rounded) this.container.classList.add('rounded');
        if (this.options.shadow) this.container.classList.add('shadow');

        // Создаем поле для отображения выбранных опций
        this.displayField = document.createElement('div');
        this.displayField.className = 'multiselect-display';
        this.displayField.textContent = this.options.placeholder;
        this.displayField.addEventListener('click', () => this.toggleDropdown());

        // Создаем выпадающий список
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'multiselect-dropdown';

        // Добавляем опции
        Array.from(this.select.options).forEach(option => {
            if (option.value) {
                const item = this.createDropdownItem(option);
                this.dropdown.appendChild(item);
            }
        });

        this.container.appendChild(this.displayField);
        this.container.appendChild(this.dropdown);

        // Заменяем оригинальный select
        this.select.parentNode.insertBefore(this.container, this.select);
        this.select.style.display = 'none';

        // Закрытие при клике вне элемента
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.closeDropdown();
            }
        });
    }

    createDropdownItem(option) {
        const item = document.createElement('div');
        item.className = 'multiselect-item';
        item.innerHTML = `
            <input type="checkbox" value="${option.value}" id="opt_${option.value}">
            <label for="opt_${option.value}">${option.text}</label>
        `;

        const checkbox = item.querySelector('input');
        checkbox.addEventListener('change', () => this.updateSelection());

        return item;
    }

    updateSelection() {
        const selectedItems = this.container.querySelectorAll('input:checked');
        const selectedValues = Array.from(selectedItems).map(item => item.value);
        const selectedTexts = Array.from(selectedItems).map(item =>
            item.nextElementSibling.textContent);

        // Обновляем оригинальный select
        Array.from(this.select.options).forEach(option => {
            option.selected = selectedValues.includes(option.value);
        });

        // Обновляем отображение
        if (selectedTexts.length > 0) {
            this.displayField.textContent = selectedTexts.join(', ');
        } else {
            this.displayField.textContent = this.options.placeholder;
        }
    }

    toggleDropdown() {
        this.dropdown.classList.toggle('show');
    }

    closeDropdown() {
        this.dropdown.classList.remove('show');
    }
}