from database.models import *
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, send_from_directory
from database import db  # Импортируем db из database пакета
import os
from datetime import datetime, date, timedelta
import json
from werkzeug.utils import secure_filename
from utils.document_generator import DocumentGenerator
from utils.file_handlers import FileHandler
from utils.validators import Validators, ValidationResult

app = Flask(__name__)
app.config['SECRET_KEY'] = 'transport-system-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transport_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'storage'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Инициализируем базу данных с приложением
db.init_app(app)

# Create upload directories
for folder in ['templates', 'photos', 'documents', 'generated', 'tests']:
    os.makedirs(f'{app.config["UPLOAD_FOLDER"]}/{folder}', exist_ok=True)

file_handler = FileHandler(app.config['UPLOAD_FOLDER'])

# Импортируем модели ПОСЛЕ инициализации db

# ========== API ДЛЯ СОГЛАСУЮЩИХ ЛИЦ ==========


@app.route('/api/agreement_persons', methods=['GET', 'POST'])
def api_agreement_persons():
    if request.method == 'POST':
        data = request.get_json()
        new_person = AgreementPerson(
            full_name=data['full_name'],
            organization=data.get('organization', ''),
            position=data.get('position', ''),
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )
        db.session.add(new_person)
        db.session.commit()
        return jsonify({
            'id': new_person.id,
            'full_name': new_person.full_name,
            'organization': new_person.organization,
            'position': new_person.position,
            'phone': new_person.phone,
            'email': new_person.email
        })

    persons = AgreementPerson.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': person.id,
        'full_name': person.full_name,
        'organization': person.organization,
        'position': person.position,
        'phone': person.phone,
        'email': person.email
    } for person in persons])


@app.route('/api/agreement_persons/<int:person_id>', methods=['DELETE'])
def api_delete_agreement_person(person_id):
    person = AgreementPerson.query.get_or_404(person_id)
    try:
        # Проверяем использование
        pass_requests_count = PassRequest.query.filter_by(
            agreement_person_id=person_id).count()
        if pass_requests_count > 0:
            return jsonify({
                'success': False,
                'error': f'Это согласующее лицо используется в {pass_requests_count} заявках'
            }), 400

        person.is_active = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== API ДЛЯ ПОСТОВ ==========


@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'POST':
        data = request.get_json()
        new_post = Post(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(new_post)
        db.session.commit()
        return jsonify({
            'id': new_post.id,
            'name': new_post.name,
            'description': new_post.description
        })

    posts = Post.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': post.id,
        'name': post.name,
        'description': post.description
    } for post in posts])


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    try:
        # Проверяем, используется ли этот пост в заявках
        pass_requests_count = PassRequest.query.filter(
            PassRequest.post_ids.contains(str(post_id))
        ).count()

        if pass_requests_count > 0:
            return jsonify({
                'success': False,
                'error': f'Этот пост используется в {pass_requests_count} заявках'
            }), 400

        # Мягкое удаление
        post.is_active = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== API ДЛЯ ДОГОВОРОВ ==========


@app.route('/api/contracts', methods=['GET', 'POST'])
def api_contracts():
    if request.method == 'POST':
        data = request.get_json()
        new_contract = Contract(
            number=data['number'],
            name=data.get('name', ''),
            start_date=datetime.strptime(
                data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(
                data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            customer=data.get('customer', '')
        )
        db.session.add(new_contract)
        db.session.commit()
        return jsonify({
            'id': new_contract.id,
            'number': new_contract.number,
            'name': new_contract.name,
            'start_date': new_contract.start_date.strftime('%Y-%m-%d'),
            'end_date': new_contract.end_date.strftime('%Y-%m-%d') if new_contract.end_date else None,
            'customer': new_contract.customer
        })

    contracts = Contract.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': contract.id,
        'number': contract.number,
        'name': contract.name,
        'start_date': contract.start_date.strftime('%Y-%m-%d'),
        'end_date': contract.end_date.strftime('%Y-%m-%d') if contract.end_date else None,
        'customer': contract.customer
    } for contract in contracts])


@app.route('/api/contracts/<int:contract_id>', methods=['DELETE'])
def api_delete_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    try:
        # Проверяем использование
        pass_requests_count = PassRequest.query.filter_by(
            contract_id=contract_id).count()
        shift_requests_count = ShiftRequest.query.filter_by(
            contract_id=contract_id).count()
        total_count = pass_requests_count + shift_requests_count

        if total_count > 0:
            return jsonify({
                'success': False,
                'error': f'Этот договор используется в {total_count} заявках'
            }), 400

        contract.is_active = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== API ДЛЯ ИНН ==========


@app.route('/api/inns', methods=['GET', 'POST'])
def api_inns():
    if request.method == 'POST':
        data = request.get_json()
        new_inn = OrganizationINN(
            inn=data['inn'],
            organization_name=data['organization_name'],
            contact_person=data.get('contact_person', ''),
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )
        db.session.add(new_inn)
        db.session.commit()
        return jsonify({
            'id': new_inn.id,
            'inn': new_inn.inn,
            'organization_name': new_inn.organization_name,
            'contact_person': new_inn.contact_person,
            'phone': new_inn.phone,
            'email': new_inn.email
        })

    inns = OrganizationINN.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': inn.id,
        'inn': inn.inn,
        'organization_name': inn.organization_name,
        'contact_person': inn.contact_person,
        'phone': inn.phone,
        'email': inn.email
    } for inn in inns])


@app.route('/api/inns/<int:inn_id>', methods=['DELETE'])
def api_delete_inn(inn_id):
    inn = OrganizationINN.query.get_or_404(inn_id)
    try:
        # Проверяем использование
        pass_requests_count = PassRequest.query.filter_by(
            inn_id=inn_id).count()
        if pass_requests_count > 0:
            return jsonify({
                'success': False,
                'error': f'Этот ИНН используется в {pass_requests_count} заявках'
            }), 400

        inn.is_active = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== API ДЛЯ ТРАНСПОРТА ==========


@app.route('/api/vehicle_types', methods=['GET', 'POST'])
def api_vehicle_types():
    if request.method == 'POST':
        data = request.get_json()
        new_type = VehicleType(name=data['name'])
        db.session.add(new_type)
        db.session.commit()
        return jsonify({'id': new_type.id, 'name': new_type.name})

    types = VehicleType.query.all()
    return jsonify([{'id': t.id, 'name': t.name} for t in types])


@app.route('/api/vehicle_types/<int:type_id>', methods=['DELETE'])
def api_delete_vehicle_type(type_id):
    vehicle_type = VehicleType.query.get_or_404(type_id)
    try:
        # Проверяем, используется ли этот тип транспорта
        vehicles_count = Vehicle.query.filter_by(
            vehicle_type_id=type_id).count()
        if vehicles_count > 0:
            return jsonify({'success': False, 'error': f'Этот тип транспорта используется в {vehicles_count} транспортных средствах'}), 400

        db.session.delete(vehicle_type)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/vehicle_categories', methods=['GET', 'POST'])
def api_vehicle_categories():
    if request.method == 'POST':
        data = request.get_json()
        new_category = VehicleCategory(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'id': new_category.id, 'name': new_category.name})

    categories = VehicleCategory.query.all()
    return jsonify([{'id': cat.id, 'name': cat.name} for cat in categories])


@app.route('/api/vehicle_categories/<int:category_id>', methods=['DELETE'])
def api_delete_vehicle_category(category_id):
    category = VehicleCategory.query.get_or_404(category_id)
    try:
        # Проверяем, используется ли эта категория
        vehicles_count = Vehicle.query.filter_by(
            vehicle_category_id=category_id).count()
        if vehicles_count > 0:
            return jsonify({'success': False, 'error': f'Эта категория используется в {vehicles_count} транспортных средствах'}), 400

        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== API ДЛЯ ТИПОВ ТРАНСПОРТА ==========
# @app.route('/api/vehicle_types/<int:type_id>', methods=['DELETE'])
# def api_delete_vehicle_type(type_id):
#     vehicle_type = VehicleType.query.get_or_404(type_id)
#     try:
#         # Проверяем, используется ли этот тип транспорта
#         vehicles_count = Vehicle.query.filter_by(vehicle_type_id=type_id).count()
#         if vehicles_count > 0:
#             return jsonify({'success': False, 'error': f'Этот тип транспорта используется в {vehicles_count} транспортных средствах'}), 400

#         db.session.delete(vehicle_type)
#         db.session.commit()
#         return jsonify({'success': True})
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'error': str(e)}), 500
# ========== API ДЛЯ СПРАВОЧНИКОВ (дополняем) ==========

@app.route('/api/cities', methods=['GET', 'POST'])
def api_cities():
    if request.method == 'POST':
        data = request.get_json()
        new_city = City(name=data['name'])
        db.session.add(new_city)
        db.session.commit()
        return jsonify({'id': new_city.id, 'name': new_city.name})

    cities = City.query.all()
    return jsonify([{'id': city.id, 'name': city.name} for city in cities])


@app.route('/api/cities/<int:city_id>', methods=['DELETE'])
def api_delete_city(city_id):
    city = City.query.get_or_404(city_id)
    db.session.delete(city)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/positions/<int:position_id>', methods=['DELETE'])
def api_delete_position(position_id):
    position = Position.query.get_or_404(position_id)
    db.session.delete(position)
    db.session.commit()
    return jsonify({'success': True})

# ========== ДОКУМЕНТЫ СОТРУДНИКА ==========


@app.route('/employees/<int:employee_id>/documents')
def employee_documents(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    # Здесь будет логика для получения документов сотрудника
    return render_template('employees/documents.html', employee=employee, current_time=datetime.now())


@app.route('/employees/<int:employee_id>/documents/upload', methods=['POST'])
def upload_employee_document(employee_id):
    try:
        if 'document' in request.files:
            document_file = request.files['document']
            if document_file.filename:
                # Сохранение документа
                filename = secure_filename(document_file.filename)
                file_path = f"documents/employee_{employee_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                document_file.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], file_path))

                # Здесь можно создать запись в таблице документов
                flash('Документ успешно загружен', 'success')
    except Exception as e:
        flash(f'Ошибка при загрузке документа: {str(e)}', 'error')

    return redirect(url_for('employee_documents', employee_id=employee_id))

# ========== ПРОПУСКИ СОТРУДНИКА ==========


@app.route('/employees/<int:employee_id>/passes')
def employee_passes(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    # Здесь будет логика для получения пропусков сотрудника
    return render_template('employees/passes.html', employee=employee, current_time=datetime.now())


@app.route('/')
def main_menu():
    return render_template('main_menu.html', current_time=datetime.now())

# ========== СОТРУДНИКИ ==========


@app.route('/employees')
def employees_list():
    employees = Employee.query.all()
    departments = Department.query.all()
    positions = Position.query.all()
    return render_template('employees/list.html',
                           employees=employees,
                           departments=departments,
                           positions=positions,
                           current_time=datetime.now())


@app.route('/employees/add', methods=['GET', 'POST'])
def employee_add():
    if request.method == 'POST':
        try:
            # Валидация данных
            validator = ValidationResult()

            # Проверка обязательных полей
            required_fields = {
                'last_name': 'Фамилия',
                'first_name': 'Имя'
            }

            for field, name in required_fields.items():
                error = Validators.validate_required(
                    request.form.get(field), name)
                if error:
                    validator.add_error(field, error)

            # Валидация email
            if request.form.get('email'):
                error = Validators.validate_email(request.form['email'])
                if error:
                    validator.add_error('email', error)

            # Валидация телефона
            if request.form.get('phone'):
                error = Validators.validate_phone(request.form['phone'])
                if error:
                    validator.add_error('phone', error)

            if validator.has_errors():
                for field, error in validator.errors.items():
                    flash(f'{error}', 'error')
                return render_template('employees/add_edit.html',
                                       departments=Department.query.all(),
                                       positions=Position.query.all(),
                                       cities=City.query.all(),
                                       current_time=datetime.now())

            employee = Employee(
                last_name=request.form['last_name'],
                first_name=request.form['first_name'],
                middle_name=request.form.get('middle_name'),
                gender=request.form.get('gender'),
                birth_date=datetime.strptime(
                    request.form['birth_date'], '%Y-%m-%d').date() if request.form.get('birth_date') else None,
                department_id=request.form.get('department_id'),
                position_id=request.form.get('position_id'),
                passport_series=request.form.get('passport_series'),
                passport_number=request.form.get('passport_number'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                city_id=request.form.get('city_id'),
                has_driver_license=bool(
                    request.form.get('has_driver_license')),
                license_categories=','.join(
                    request.form.getlist('license_categories')),
                pass_number=request.form.get('pass_number'),
                pass_expiry=datetime.strptime(
                    request.form['pass_expiry'], '%Y-%m-%d').date() if request.form.get('pass_expiry') else None,
                clothing_size=request.form.get('clothing_size'),
                shoe_size=request.form.get('shoe_size'),
                height=request.form.get('height')
            )

            # Обработка фото
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename:
                    # Валидация файла
                    error = Validators.validate_file_extension(
                        photo.filename, ['jpg', 'jpeg', 'png', 'gif'])
                    if error:
                        flash(error, 'error')
                    else:
                        photo_path = file_handler.save_employee_photo(photo)
                        if photo_path:
                            employee.photo_path = photo_path

            db.session.add(employee)
            db.session.commit()
            flash('Сотрудник успешно добавлен', 'success')
            return redirect(url_for('employees_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении сотрудника: {str(e)}', 'error')

    departments = Department.query.all()
    positions = Position.query.all()
    cities = City.query.all()
    return render_template('employees/add_edit.html',
                           departments=departments,
                           positions=positions,
                           cities=cities, current_time=datetime.now())


@app.route('/employees/<int:employee_id>')
def employee_card(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    return render_template('employees/card.html', employee=employee, current_time=datetime.now())

# @app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
# def employee_edit(employee_id):
#     employee = Employee.query.get_or_404(employee_id)

#     if request.method == 'POST':
#         try:
#             # Обновляем все поля
#             employee.last_name = request.form['last_name']
#             employee.first_name = request.form['first_name']
#             employee.middle_name = request.form.get('middle_name')
#             employee.gender = request.form.get('gender')
#             employee.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date() if request.form.get('birth_date') else None
#             employee.department_id = request.form.get('department_id')
#             employee.position_id = request.form.get('position_id')
#             employee.passport_series = request.form.get('passport_series')
#             employee.passport_number = request.form.get('passport_number')
#             employee.phone = request.form.get('phone')
#             employee.email = request.form.get('email')
#             employee.city_id = request.form.get('city_id')
#             employee.has_driver_license = bool(request.form.get('has_driver_license'))
#             employee.license_categories = ','.join(request.form.getlist('license_categories'))
#             employee.pass_number = request.form.get('pass_number')
#             employee.pass_expiry = datetime.strptime(request.form['pass_expiry'], '%Y-%m-%d').date() if request.form.get('pass_expiry') else None
#             employee.medical_exam_expiry = datetime.strptime(request.form['medical_exam_expiry'], '%Y-%m-%d').date() if request.form.get('medical_exam_expiry') else None
#             employee.medical_exam_not_required = bool(request.form.get('medical_exam_not_required'))
#             employee.psychiatric_exam_expiry = datetime.strptime(request.form['psychiatric_exam_expiry'], '%Y-%m-%d').date() if request.form.get('psychiatric_exam_expiry') else None
#             employee.psychiatric_exam_not_required = bool(request.form.get('psychiatric_exam_not_required'))
#             employee.clothing_size = request.form.get('clothing_size')
#             employee.shoe_size = request.form.get('shoe_size')
#             employee.height = request.form.get('height')
#             employee.updated_at = datetime.utcnow()

#             # Обработка фото
#             if 'photo' in request.files:
#                 photo = request.files['photo']
#                 if photo.filename:
#                     # Сохраняем новое фото (здесь нужно добавить логику сохранения файла)
#                     pass

#             db.session.commit()
#             flash('Данные сотрудника успешно обновлены', 'success')
#             return redirect(url_for('employee_card', employee_id=employee.id))

#         except Exception as e:
#             db.session.rollback()
#             flash(f'Ошибка при обновлении данных сотрудника: {str(e)}', 'error')

#     departments = Department.query.all()
#     positions = Position.query.all()
#     cities = City.query.all()
#     return render_template('employees/add_edit.html',
#                          employee=employee,
#                          departments=departments,
#                          positions=positions,
#                          cities=cities, current_time=datetime.now())

# @app.route('/employees/<int:employee_id>/delete', methods=['POST'])
# def employee_delete(employee_id):
#     employee = Employee.query.get_or_404(employee_id)
#     try:
#         # Удаляем фото если есть
#         if employee.photo_path:
#             file_handler.delete_file(os.path.join(app.config['UPLOAD_FOLDER'], employee.photo_path))

#         db.session.delete(employee)
#         db.session.commit()
#         flash('Сотрудник успешно удален', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash(f'Ошибка при удалении сотрудника: {str(e)}', 'error')

#     return redirect(url_for('employees_list'))

# ========== СОТРУДНИКИ (дополняем маршруты) ==========


@app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
def employee_edit(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        try:
            # Обновляем все поля сотрудника
            employee.last_name = request.form['last_name']
            employee.first_name = request.form['first_name']
            employee.middle_name = request.form.get('middle_name')
            employee.gender = request.form.get('gender')

            # Обработка даты рождения
            birth_date = request.form.get('birth_date')
            employee.birth_date = datetime.strptime(
                birth_date, '%Y-%m-%d').date() if birth_date else None

            employee.department_id = request.form.get('department_id')
            employee.position_id = request.form.get('position_id')
            employee.passport_series = request.form.get('passport_series')
            employee.passport_number = request.form.get('passport_number')
            employee.phone = request.form.get('phone')
            employee.email = request.form.get('email')
            employee.city_id = request.form.get('city_id')
            employee.has_driver_license = bool(
                request.form.get('has_driver_license'))

            # Обработка категорий прав
            license_categories = request.form.getlist('license_categories')
            employee.license_categories = ','.join(
                license_categories) if license_categories else None

            employee.pass_number = request.form.get('pass_number')

            # Обработка даты окончания допуска
            pass_expiry = request.form.get('pass_expiry')
            employee.pass_expiry = datetime.strptime(
                pass_expiry, '%Y-%m-%d').date() if pass_expiry else None

            # Обработка медосмотров
            medical_exam_expiry = request.form.get('medical_exam_expiry')
            employee.medical_exam_expiry = datetime.strptime(
                medical_exam_expiry, '%Y-%m-%d').date() if medical_exam_expiry else None
            employee.medical_exam_not_required = bool(
                request.form.get('medical_exam_not_required'))

            # Обработка психиатрического освидетельствования
            psychiatric_exam_expiry = request.form.get(
                'psychiatric_exam_expiry')
            employee.psychiatric_exam_expiry = datetime.strptime(
                psychiatric_exam_expiry, '%Y-%m-%d').date() if psychiatric_exam_expiry else None
            employee.psychiatric_exam_not_required = bool(
                request.form.get('psychiatric_exam_not_required'))

            employee.clothing_size = request.form.get('clothing_size')
            employee.shoe_size = request.form.get('shoe_size')
            employee.height = request.form.get('height')
            employee.updated_at = datetime.utcnow()

            # Обработка фото
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename:
                    # Сохраняем новое фото
                    filename = secure_filename(photo.filename)
                    photo_path = f"photos/employee_{employee_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    photo.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], photo_path))
                    employee.photo_path = photo_path

            db.session.commit()
            flash('Данные сотрудника успешно обновлены', 'success')
            return redirect(url_for('employee_card', employee_id=employee.id))

        except Exception as e:
            db.session.rollback()
            flash(
                f'Ошибка при обновлении данных сотрудника: {str(e)}', 'error')

    departments = Department.query.all()
    positions = Position.query.all()
    cities = City.query.all()
    return render_template('employees/add_edit.html',
                           employee=employee,
                           departments=departments,
                           positions=positions,
                           cities=cities, current_time=datetime.now())


@app.route('/employees/<int:employee_id>/delete', methods=['POST'])
def employee_delete(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    try:
        # Удаляем фото если есть
        if employee.photo_path:
            photo_path = os.path.join(
                app.config['UPLOAD_FOLDER'], employee.photo_path)
            if os.path.exists(photo_path):
                os.remove(photo_path)

        db.session.delete(employee)
        db.session.commit()
        flash('Сотрудник успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении сотрудника: {str(e)}', 'error')

    return redirect(url_for('employees_list'))

# # ========== ТРАНСПОРТ ==========
# @app.route('/transport')
# def transport_list():
#     vehicles = Vehicle.query.all()
#     return render_template('transport/list.html', vehicles=vehicles, current_time=datetime.now())

# @app.route('/transport/add', methods=['GET', 'POST'])
# def transport_add():
#     if request.method == 'POST':
#         try:
#             # Валидация
#             validator = ValidationResult()

#             required_fields = {
#                 'brand': 'Марка',
#                 'license_plate': 'Госномер'
#             }

#             for field, name in required_fields.items():
#                 error = Validators.validate_required(request.form.get(field), name)
#                 if error:
#                     validator.add_error(field, error)

#             # Валидация госномера
#             if request.form.get('license_plate'):
#                 error = Validators.validate_license_plate(request.form['license_plate'])
#                 if error:
#                     validator.add_error('license_plate', error)

#             if validator.has_errors():
#                 for field, error in validator.errors.items():
#                     flash(f'{error}', 'error')
#                 return render_template('transport/add_edit.html',
#                                      vehicle_types=VehicleType.query.all(),
#                                      vehicle_categories=VehicleCategory.query.all(),
#                                      departments=Department.query.all(),
#                                      current_time=datetime.now())

#             vehicle = Vehicle(
#                 vehicle_type_id=request.form.get('vehicle_type_id'),
#                 brand=request.form['brand'],
#                 license_plate=request.form['license_plate'],
#                 department_id=request.form.get('department_id'),
#                 vehicle_category_id=request.form.get('vehicle_category_id'),
#                 manufacture_year=request.form.get('manufacture_year'),
#                 pass_number=request.form.get('pass_number'),
#                 pass_expiry=datetime.strptime(request.form['pass_expiry'], '%Y-%m-%d').date() if request.form.get('pass_expiry') else None,
#                 insurance_expiry=datetime.strptime(request.form['insurance_expiry'], '%Y-%m-%d').date() if request.form.get('insurance_expiry') else None,
#                 inspection_expiry=datetime.strptime(request.form['inspection_expiry'], '%Y-%m-%d').date() if request.form.get('inspection_expiry') else None
#             )

#             db.session.add(vehicle)
#             db.session.commit()
#             flash('Транспорт успешно добавлен', 'success')
#             return redirect(url_for('transport_list'))

#         except Exception as e:
#             db.session.rollback()
#             flash(f'Ошибка при добавлении транспорта: {str(e)}', 'error')

#     vehicle_types = VehicleType.query.all()
#     vehicle_categories = VehicleCategory.query.all()
#     departments = Department.query.all()
#     return render_template('transport/add_edit.html',
#                          vehicle_types=vehicle_types,
#                          vehicle_categories=vehicle_categories,
#                          departments=departments, current_time=datetime.now())

# @app.route('/transport/<int:vehicle_id>')
# def vehicle_card(vehicle_id):
#     vehicle = Vehicle.query.get_or_404(vehicle_id)
#     return render_template('transport/card.html', vehicle=vehicle, current_time=datetime.now())

# @app.route('/transport/<int:vehicle_id>/edit', methods=['GET', 'POST'])
# def vehicle_edit(vehicle_id):
#     vehicle = Vehicle.query.get_or_404(vehicle_id)

#     if request.method == 'POST':
#         try:
#             vehicle.vehicle_type_id = request.form.get('vehicle_type_id')
#             vehicle.brand = request.form['brand']
#             vehicle.license_plate = request.form['license_plate']
#             vehicle.department_id = request.form.get('department_id')
#             vehicle.vehicle_category_id = request.form.get('vehicle_category_id')
#             vehicle.manufacture_year = request.form.get('manufacture_year')
#             vehicle.pass_number = request.form.get('pass_number')
#             vehicle.pass_expiry = datetime.strptime(request.form['pass_expiry'], '%Y-%m-%d').date() if request.form.get('pass_expiry') else None
#             vehicle.insurance_expiry = datetime.strptime(request.form['insurance_expiry'], '%Y-%m-%d').date() if request.form.get('insurance_expiry') else None
#             vehicle.inspection_expiry = datetime.strptime(request.form['inspection_expiry'], '%Y-%m-%d').date() if request.form.get('inspection_expiry') else None
#             vehicle.updated_at = datetime.utcnow()

#             db.session.commit()
#             flash('Данные транспорта успешно обновлены', 'success')
#             return redirect(url_for('vehicle_card', vehicle_id=vehicle.id))

#         except Exception as e:
#             db.session.rollback()
#             flash(f'Ошибка при обновлении данных транспорта: {str(e)}', 'error')

#     vehicle_types = VehicleType.query.all()
#     vehicle_categories = VehicleCategory.query.all()
#     departments = Department.query.all()
#     return render_template('transport/add_edit.html',
#                          vehicle=vehicle,
#                          vehicle_types=vehicle_types,
#                          vehicle_categories=vehicle_categories,
#                          departments=departments, current_time=datetime.now())

# @app.route('/transport/<int:vehicle_id>/delete', methods=['POST'])
# def vehicle_delete(vehicle_id):
#     vehicle = Vehicle.query.get_or_404(vehicle_id)
#     try:
#         db.session.delete(vehicle)
#         db.session.commit()
#         flash('Транспорт успешно удален', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash(f'Ошибка при удалении транспорта: {str(e)}', 'error')

#     return redirect(url_for('transport_list'))

# ========== ТРАНСПОРТ ==========


@app.route('/transport')
def transport_list():
    vehicles = Vehicle.query.all()
    vehicle_types = VehicleType.query.all()
    vehicle_categories = VehicleCategory.query.all()
    departments = Department.query.all()
    return render_template('transport/list.html',
                           vehicles=vehicles,
                           vehicle_types=vehicle_types,
                           vehicle_categories=vehicle_categories,
                           departments=departments,
                           current_time=datetime.now())


@app.route('/transport/add', methods=['GET', 'POST'])
def transport_add():
    if request.method == 'POST':
        try:
            vehicle = Vehicle(
                vehicle_type_id=request.form.get('vehicle_type_id'),
                brand=request.form['brand'],
                license_plate=request.form['license_plate'],
                department_id=request.form.get('department_id'),
                vehicle_category_id=request.form.get('vehicle_category_id'),
                manufacture_year=request.form.get('manufacture_year'),
                pass_number=request.form.get('pass_number'),
                pass_expiry=datetime.strptime(
                    request.form['pass_expiry'], '%Y-%m-%d').date() if request.form.get('pass_expiry') else None,
                insurance_expiry=datetime.strptime(
                    request.form['insurance_expiry'], '%Y-%m-%d').date() if request.form.get('insurance_expiry') else None,
                inspection_expiry=datetime.strptime(
                    request.form['inspection_expiry'], '%Y-%m-%d').date() if request.form.get('inspection_expiry') else None
            )

            db.session.add(vehicle)
            db.session.commit()
            flash('Транспорт успешно добавлен', 'success')
            return redirect(url_for('transport_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении транспорта: {str(e)}', 'error')

    vehicle_types = VehicleType.query.all()
    vehicle_categories = VehicleCategory.query.all()
    departments = Department.query.all()
    return render_template('transport/add_edit.html',
                           vehicle_types=vehicle_types,
                           vehicle_categories=vehicle_categories,
                           departments=departments, current_time=datetime.now())


@app.route('/transport/<int:vehicle_id>')
def vehicle_card(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return render_template('transport/card.html', vehicle=vehicle, current_time=datetime.now())


@app.route('/transport/<int:vehicle_id>/edit', methods=['GET', 'POST'])
def vehicle_edit(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        try:
            vehicle.vehicle_type_id = request.form.get('vehicle_type_id')
            vehicle.brand = request.form['brand']
            vehicle.license_plate = request.form['license_plate']
            vehicle.department_id = request.form.get('department_id')
            vehicle.vehicle_category_id = request.form.get(
                'vehicle_category_id')
            vehicle.manufacture_year = request.form.get('manufacture_year')
            vehicle.pass_number = request.form.get('pass_number')

            pass_expiry = request.form.get('pass_expiry')
            vehicle.pass_expiry = datetime.strptime(
                pass_expiry, '%Y-%m-%d').date() if pass_expiry else None

            insurance_expiry = request.form.get('insurance_expiry')
            vehicle.insurance_expiry = datetime.strptime(
                insurance_expiry, '%Y-%m-%d').date() if insurance_expiry else None

            inspection_expiry = request.form.get('inspection_expiry')
            vehicle.inspection_expiry = datetime.strptime(
                inspection_expiry, '%Y-%m-%d').date() if inspection_expiry else None

            vehicle.updated_at = datetime.utcnow()

            db.session.commit()
            flash('Данные транспорта успешно обновлены', 'success')
            return redirect(url_for('vehicle_card', vehicle_id=vehicle.id))

        except Exception as e:
            db.session.rollback()
            flash(
                f'Ошибка при обновлении данных транспорта: {str(e)}', 'error')

    vehicle_types = VehicleType.query.all()
    vehicle_categories = VehicleCategory.query.all()
    departments = Department.query.all()
    return render_template('transport/add_edit.html',
                           vehicle=vehicle,
                           vehicle_types=vehicle_types,
                           vehicle_categories=vehicle_categories,
                           departments=departments, current_time=datetime.now())


@app.route('/transport/<int:vehicle_id>/delete', methods=['POST'])
def vehicle_delete(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    try:
        db.session.delete(vehicle)
        db.session.commit()
        flash('Транспорт успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении транспорта: {str(e)}', 'error')

    return redirect(url_for('transport_list'))

# ========== API ДЛЯ ТИПОВ ТРАНСПОРТА ==========
# @app.route('/api/vehicle_types/<int:type_id>', methods=['DELETE'])
# def api_delete_vehicle_type(type_id):
#     vehicle_type = VehicleType.query.get_or_404(type_id)
#     db.session.delete(vehicle_type)
#     db.session.commit()
#     return jsonify({'success': True})

# @app.route('/api/vehicle_categories', methods=['GET', 'POST'])
# def api_vehicle_categories():
#     if request.method == 'POST':
#         data = request.get_json()
#         new_category = VehicleCategory(name=data['name'])
#         db.session.add(new_category)
#         db.session.commit()
#         return jsonify({'id': new_category.id, 'name': new_category.name})

#     categories = VehicleCategory.query.all()
#     return jsonify([{'id': cat.id, 'name': cat.name} for cat in categories])

# @app.route('/api/vehicle_categories/<int:category_id>', methods=['DELETE'])
# def api_delete_vehicle_category(category_id):
#     category = VehicleCategory.query.get_or_404(category_id)
#     db.session.delete(category)
#     db.session.commit()
#     return jsonify({'success': True})

# ========== КАБИНЕТ НАЧАЛЬНИКА ТЦ ==========


@app.route('/head_of_department')
def head_of_department_index():
    return render_template('head_of_department/index.html', current_time=datetime.now())

# Заявки на пропуска


@app.route('/head_of_department/pass_requests')
def pass_requests_list():
    requests = PassRequest.query.all()
    return render_template('head_of_department/pass_requests/list.html', requests=requests, current_time=datetime.now())


@app.route('/head_of_department/pass_requests/manage_dictionaries')
def manage_dictionaries():
    posts = Post.query.filter_by(is_active=True).all()
    contracts = Contract.query.filter_by(is_active=True).all()
    inns = OrganizationINN.query.filter_by(is_active=True).all()
    agreement_persons = AgreementPerson.query.filter_by(is_active=True).all()

    return render_template('head_of_department/pass_requests/manage_dictionaries.html',
                           posts=posts,
                           contracts=contracts,
                           inns=inns,
                           agreement_persons=agreement_persons,
                           current_time=datetime.now())


@app.route('/head_of_department/pass_requests/create/<request_type>')
def create_pass_request(request_type):
    posts = Post.query.filter_by(is_active=True).all()
    contracts = Contract.query.filter_by(is_active=True).all()
    agreement_persons = AgreementPerson.query.filter_by(
        is_active=True).all()  # Теперь используем нашу модель
    employees = Employee.query.all()
    vehicles = Vehicle.query.all()
    inns = OrganizationINN.query.filter_by(is_active=True).all()

    return render_template(f'head_of_department/pass_requests/create_{request_type}.html',
                           posts=posts,
                           contracts=contracts,
                           agreement_persons=agreement_persons,
                           employees=employees,
                           vehicles=vehicles,
                           inns=inns,
                           request_type=request_type,
                           current_time=datetime.now())


@app.route('/head_of_department/pass_requests/save', methods=['POST'])
def save_pass_request():
    try:
        request_type = request.form.get('request_type')
        post_ids = request.form.getlist('posts')  # список выбранных постов
        employee_ids = request.form.getlist(
            'employees')  # список выбранных сотрудников
        vehicle_ids = request.form.getlist(
            'vehicles')  # список выбранного транспорта

        print(f"📝 Debug: post_ids = {post_ids}")
        print(f"📝 Debug: employee_ids = {employee_ids}")
        print(f"📝 Debug: vehicle_ids = {vehicle_ids}")

        # Создаем заявку с правильными названиями полей
        pass_request = PassRequest(
            request_type=request_type,
            post_ids=json.dumps(post_ids),
            start_date=datetime.strptime(
                request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(
                request.form['end_date'], '%Y-%m-%d').date(),
            contract_id=request.form.get('contract_id'),
            inn_id=request.form.get('inn_id'),
            purpose=request.form.get('purpose'),
            formed_by=request.form.get('formed_by'),
            agreement_person_id=request.form.get('agreement_person_id'),
            is_one_time=bool(request.form.get('is_one_time')),
            # ← ИСПРАВЛЕНО: employee_ids вместо employees
            employee_ids=json.dumps(employee_ids),
            # ← ИСПРАВЛЕНО: vehicle_ids вместо vehicles
            vehicle_ids=json.dumps(vehicle_ids),
            status='draft'
        )

        # Генерация документа если есть шаблон
        if 'template' in request.files and request.files['template'].filename:
            template_file = request.files['template']
            template_path = file_handler.save_template(
                template_file, 'pass_requests')
            if template_path:
                pass_request.template_path = template_path

                # Генерация документа
                doc_generator = DocumentGenerator(
                    os.path.join(app.config['UPLOAD_FOLDER'], template_path),
                    os.path.join(app.config['UPLOAD_FOLDER'], 'generated')
                )

                # Получаем данные для документа
                posts = [Post.query.get(
                    int(post_id)).name for post_id in post_ids if post_id]
                employees = [Employee.query.get(
                    int(emp_id)).get_full_name() for emp_id in employee_ids if emp_id]
                vehicles = [Vehicle.query.get(
                    int(veh_id)).license_plate for veh_id in vehicle_ids if veh_id]

                document_data = {
                    'start_date': request.form['start_date'],
                    'end_date': request.form['end_date'],
                    'posts': posts,
                    'employees': employees,
                    'vehicles': vehicles,
                    'formed_by': request.form.get('formed_by'),
                    'purpose': request.form.get('purpose', '')
                }

                generated_doc_path = doc_generator.generate_pass_request(
                    document_data, request_type)
                if generated_doc_path:
                    pass_request.generated_document_path = generated_doc_path

        db.session.add(pass_request)
        db.session.commit()
        flash('Заявка на пропуск успешно создана', 'success')
        return redirect(url_for('pass_requests_list'))

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating pass request: {str(e)}")
        flash(f'Ошибка при создании заявки: {str(e)}', 'error')
        return redirect(url_for('create_pass_request', request_type=request.form.get('request_type')))
# ========== ПЕРЕВАХТОВКА ==========


@app.route('/head_of_department/shift_handover')
def shift_handover_index():
    return render_template('head_of_department/shift_handover/index.html', current_time=datetime.now())


@app.route('/head_of_department/shift_handover/charter', methods=['GET', 'POST'])
def create_charter_request():
    if request.method == 'POST':
        try:
            employees = request.form.getlist('employees')

            shift_request = ShiftRequest(
                request_type='charter',
                flight_date=datetime.strptime(
                    request.form['flight_date'], '%Y-%m-%d').date() if request.form.get('flight_date') else None,
                departure_airport_id=request.form.get('departure_airport_id'),
                arrival_airport_id=request.form.get('arrival_airport_id'),
                contract_id=request.form.get('contract_id'),
                auto_delivery_from=request.form.get('auto_delivery_from'),
                auto_delivery_to=request.form.get('auto_delivery_to'),
                formed_by=request.form.get('formed_by'),
                employees=json.dumps(employees),
                status='draft'
            )

            db.session.add(shift_request)
            db.session.commit()
            flash('Заявка на чартерный рейс успешно создана', 'success')
            return redirect(url_for('shift_handover_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании заявки: {str(e)}', 'error')

    airports = Airport.query.all()
    contracts = Contract.query.all()
    employees = Employee.query.all()
    return render_template('head_of_department/shift_handover/charter.html',
                           airports=airports,
                           contracts=contracts,
                           employees=employees, current_time=datetime.now())


@app.route('/head_of_department/shift_handover/regular', methods=['GET', 'POST'])
def create_regular_request():
    if request.method == 'POST':
        try:
            employees = request.form.getlist('employees')

            shift_request = ShiftRequest(
                request_type='regular',
                flight_date=datetime.strptime(
                    request.form['flight_date'], '%Y-%m-%d').date() if request.form.get('flight_date') else None,
                departure_airport_id=request.form.get('departure_airport_id'),
                arrival_airport_id=request.form.get('arrival_airport_id'),
                flight_number=request.form.get('flight_number'),
                preliminary_cost=request.form.get('preliminary_cost'),
                formed_by=request.form.get('formed_by'),
                employees=json.dumps(employees),
                status='draft'
            )

            db.session.add(shift_request)
            db.session.commit()
            flash('Заявка на регулярный рейс успешно создана', 'success')
            return redirect(url_for('shift_handover_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании заявки: {str(e)}', 'error')

    airports = Airport.query.all()
    employees = Employee.query.all()
    return render_template('head_of_department/shift_handover/regular.html',
                           airports=airports,
                           employees=employees, current_time=datetime.now())


@app.route('/head_of_department/shift_handover/auto_delivery', methods=['GET', 'POST'])
def create_auto_delivery():
    if request.method == 'POST':
        try:
            employees = request.form.getlist('employees')

            shift_request = ShiftRequest(
                request_type='auto',
                flight_date=datetime.strptime(
                    request.form['request_date'], '%Y-%m-%d').date() if request.form.get('request_date') else None,
                contract_id=request.form.get('contract_id'),
                auto_delivery_from=request.form.get('auto_delivery_from'),
                auto_delivery_to=request.form.get('auto_delivery_to'),
                formed_by=request.form.get('formed_by'),
                employees=json.dumps(employees),
                status='draft'
            )

            db.session.add(shift_request)
            db.session.commit()
            flash('Заявка на автодоставку успешно создана', 'success')
            return redirect(url_for('shift_handover_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании заявки: {str(e)}', 'error')

    contracts = Contract.query.all()
    employees = Employee.query.all()
    return render_template('head_of_department/shift_handover/auto_delivery.html',
                           contracts=contracts,
                           employees=employees, current_time=datetime.now())

# ========== УЧЕТ ЭЛЕКТРОЭНЕРГИИ ==========


@app.route('/head_of_department/electricity')
def electricity_index():
    recent_readings = ElectricityReading.query.order_by(
        ElectricityReading.date.desc()).limit(5).all()
    return render_template('head_of_department/electricity/index.html',
                           recent_readings=recent_readings, current_time=datetime.now())


@app.route('/head_of_department/electricity/save', methods=['POST'])
def save_electricity_readings():
    try:
        reading = ElectricityReading(
            date=datetime.strptime(
                request.form['reading_date'], '%Y-%m-%d').date(),
            previous_bpo=request.form.get('previous_bpo'),
            previous_dormitory=request.form.get('previous_dormitory'),
            current_bpo=request.form.get('current_bpo'),
            current_dormitory=request.form.get('current_dormitory')
        )

        # Обработка файла Excel
        if 'excel_file' in request.files and request.files['excel_file'].filename:
            excel_file = request.files['excel_file']
            file_path = file_handler.save_document(excel_file, 'electricity')
            if file_path:
                reading.file_path = file_path

        db.session.add(reading)
        db.session.commit()
        flash('Показания электроэнергии успешно сохранены', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при сохранении показаний: {str(e)}', 'error')

    return redirect(url_for('electricity_index'))

# ========== НАРЯДЫ-ДОПУСКИ ==========


@app.route('/head_of_department/work_permit')
def work_permit_index():
    recent_permits = WorkPermit.query.order_by(
        WorkPermit.created_at.desc()).limit(5).all()
    employees = Employee.query.all()

    # Генерация следующего номера наряда
    last_permit = WorkPermit.query.order_by(WorkPermit.id.desc()).first()
    next_number = f"ШМР-{(last_permit.id + 1) if last_permit else 1:04d}"

    return render_template('head_of_department/work_permit/index.html',
                           recent_permits=recent_permits,
                           employees=employees,
                           next_permit_number=next_number, current_time=datetime.now())


@app.route('/head_of_department/work_permit/save', methods=['POST'])
def save_work_permit():
    try:
        work_permit = WorkPermit(
            number=request.form['permit_number'],
            tire_type=request.form.get('tire_type'),
            start_date=datetime.strptime(
                request.form['start_date'], '%Y-%m-%d').date() if request.form.get('start_date') else None,
            end_date=datetime.strptime(
                request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None,
            start_time=request.form.get('start_time'),
            end_time=request.form.get('end_time'),
            supervisor_id=request.form.get('supervisor_id'),
            responsible_id=request.form.get('responsible_id'),
            executor_id=request.form.get('executor_id')
        )

        # Обработка шаблона
        if 'template' in request.files and request.files['template'].filename:
            template_file = request.files['template']
            template_path = file_handler.save_template(
                template_file, 'work_permits')
            if template_path:
                work_permit.template_path = template_path

        db.session.add(work_permit)
        db.session.commit()
        flash('Наряд-допуск успешно создан', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при создании наряда-допуска: {str(e)}', 'error')

    return redirect(url_for('work_permit_index'))

# ========== КАБИНЕТ ДИСПЕТЧЕРА ==========


@app.route('/dispatcher')
def dispatcher_index():
    return render_template('dispatcher/index.html', current_time=datetime.now())


@app.route('/dispatcher/daily_requests')
def daily_requests_list():
    requests = DailyRequest.query.order_by(DailyRequest.date.desc()).all()
    return render_template('dispatcher/daily_requests.html', requests=requests, current_time=datetime.now())


@app.route('/dispatcher/daily_requests/create', methods=['POST'])
def create_daily_request():
    try:
        shift_type = request.form.get('shift_type')
        request_date = datetime.strptime(
            request.form['request_date'], '%Y-%m-%d').date()

        # Собираем данные по технике из формы
        vehicles_data = []
        vehicle_count = int(request.form.get('vehicle_count', 0))

        for i in range(1, vehicle_count + 1):
            vehicle_type = request.form.get(f'vehicle_type_{i}')
            driver_id = request.form.get(f'vehicle_driver_{i}')

            if vehicle_type and driver_id:
                vehicles_data.append({
                    'vehicle_type': vehicle_type,
                    'driver_id': int(driver_id),
                    'shifts_count': request.form.get(f'shifts_count_{i}', 0)
                })

        daily_request = DailyRequest(
            date=request_date,
            shift_type=shift_type,
            vehicles_data=json.dumps(vehicles_data)
        )

        db.session.add(daily_request)
        db.session.commit()
        flash('Суточная заявка успешно создана', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при создании заявки: {str(e)}', 'error')

    return redirect(url_for('daily_requests_list'))

# ========== КАБИНЕТ ОТ, ПБ и БДД ==========


@app.route('/safety_department')
def safety_department_index():
    # Проверка просроченных документов
    today = date.today()
    expired_employees = Employee.query.filter(
        (Employee.pass_expiry < today) |
        (Employee.medical_exam_expiry < today) |
        (Employee.psychiatric_exam_expiry < today)
    ).all()

    expired_vehicles = Vehicle.query.filter(
        (Vehicle.pass_expiry < today) |
        (Vehicle.insurance_expiry < today) |
        (Vehicle.inspection_expiry < today)
    ).all()

    return render_template('safety_department/index.html',
                           expired_employees=expired_employees,
                           expired_vehicles=expired_vehicles, current_time=datetime.now())


@app.route('/safety_department/tests')
def tests_list():
    tests = Test.query.all()
    total_results = TestResult.query.count()

    # Расчет среднего балла
    avg_score = db.session.query(db.func.avg(TestResult.score)).scalar() or 0
    average_score = round(avg_score, 1)

    return render_template('safety_department/tests/list.html',
                           tests=tests,
                           total_results=total_results,
                           average_score=average_score, current_time=datetime.now())


@app.route('/safety_department/tests/create', methods=['GET', 'POST'])
def create_test():
    if request.method == 'POST':
        try:
            test_name = request.form['test_name']
            questions_data = []

            # Обработка вопросов из формы
            question_count = int(request.form.get('question_count', 0))

            for i in range(1, question_count + 1):
                question_text = request.form.get(f'question_{i}_text')
                if question_text:
                    question = {
                        'text': question_text,
                        'multiple': bool(request.form.get(f'question_{i}_multiple')),
                        'answers': []
                    }

                    # Обработка ответов
                    answer_count = int(request.form.get(
                        f'question_{i}_answer_count', 0))
                    for j in range(1, answer_count + 1):
                        answer_text = request.form.get(
                            f'question_{i}_answer_{j}_text')
                        if answer_text:
                            answer = {
                                'text': answer_text,
                                'correct': bool(request.form.get(f'question_{i}_answer_{j}_correct'))
                            }
                            question['answers'].append(answer)

                    questions_data.append(question)

            test = Test(
                name=test_name,
                questions=json.dumps(questions_data, ensure_ascii=False)
            )

            db.session.add(test)
            db.session.commit()
            flash('Тест успешно создан', 'success')
            return redirect(url_for('tests_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании теста: {str(e)}', 'error')

    return render_template('safety_department/tests/create.html', current_time=datetime.now())


@app.route('/safety_department/tests/<int:test_id>/take', methods=['GET', 'POST'])
def take_test(test_id):
    test = Test.query.get_or_404(test_id)

    if request.method == 'POST':
        try:
            employee_name = request.form['employee_name']
            answers = {}
            score = 0
            max_score = len(json.loads(test.questions))

            # Проверка ответов
            for question in json.loads(test.questions):
                question_index = json.loads(test.questions).index(question) + 1
                if question['multiple']:
                    # Множественный выбор
                    user_answers = set(request.form.getlist(
                        f'question_{question_index}_answers'))
                    correct_answers = set(str(i) for i, answer in enumerate(
                        question['answers']) if answer['correct'])

                    if user_answers == correct_answers:
                        score += 1
                else:
                    # Одиночный выбор
                    user_answer = request.form.get(
                        f'question_{question_index}_answer')
                    if user_answer and question['answers'][int(user_answer) - 1]['correct']:
                        score += 1

                answers[str(question_index)] = user_answer if not question['multiple'] else list(
                    user_answers)

            test_result = TestResult(
                test_id=test_id,
                employee_name=employee_name,
                answers=json.dumps(answers),
                score=score,
                max_score=max_score,
                passed=score >= (max_score * 0.7)  # 70% для прохождения
            )

            db.session.add(test_result)
            db.session.commit()

            flash(f'Тест завершен. Результат: {score}/{max_score}',
                  'success' if test_result.passed else 'warning')
            return redirect(url_for('tests_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при сохранении результатов: {str(e)}', 'error')

    return render_template('safety_department/tests/take_test.html',
                           test=test, current_time=datetime.now())


@app.route('/safety_department/tests/<int:test_id>/results')
def test_results(test_id):
    test = Test.query.get_or_404(test_id)
    results = TestResult.query.filter_by(test_id=test_id).order_by(
        TestResult.created_at.desc()).all()
    return render_template('safety_department/tests/results.html',
                           test=test,
                           results=results, current_time=datetime.now())

# ========== КАБИНЕТ КЛАДОВЩИКА ==========


@app.route('/storekeeper')
def storekeeper_index():
    return render_template('storekeeper/index.html', current_time=datetime.now())


@app.route('/storekeeper/ttn/create', methods=['GET', 'POST'])
def create_ttn():
    if request.method == 'POST':
        try:
            # Генерация номера ТТН
            last_ttn = TTN.query.order_by(TTN.id.desc()).first()
            next_number = f"ТТН-{(last_ttn.id + 1) if last_ttn else 1:06d}"

            ttn = TTN(
                date=datetime.strptime(
                    request.form['date'], '%Y-%m-%d').date(),
                number=next_number,
                sender_organization=request.form.get('sender_organization'),
                receiver_organization=request.form.get(
                    'receiver_organization'),
                places_count=request.form.get('places_count'),
                cargo_weight=request.form.get('cargo_weight'),
                loading_address=request.form.get('loading_address'),
                unloading_address=request.form.get('unloading_address'),
                loading_time=request.form.get('loading_time'),
                sender_individual=request.form.get('sender_individual'),
                sender_legal=request.form.get('sender_legal'),
                carrier_individual=request.form.get('carrier_individual'),
                vehicle_info=request.form.get('vehicle_info'),
                waybill_number=request.form.get('waybill_number'),
                trailer_info=request.form.get('trailer_info')
            )

            # Обработка шаблона
            if 'template' in request.files and request.files['template'].filename:
                template_file = request.files['template']
                template_path = file_handler.save_template(
                    template_file, 'ttn')
                if template_path:
                    ttn.template_path = template_path

            db.session.add(ttn)
            db.session.commit()
            flash('ТТН успешно создана', 'success')
            return redirect(url_for('storekeeper_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании ТТН: {str(e)}', 'error')

    return render_template('storekeeper/create_ttn.html', current_time=datetime.now())


@app.route('/storekeeper/uniform/accounting')
def uniform_accounting():
    employees = Employee.query.all()
    uniform_types = UniformType.query.all()
    employee_uniforms = EmployeeUniform.query.all()

    # Статистика
    total_issued = EmployeeUniform.query.count()
    today = date.today()
    expiring_soon = EmployeeUniform.query.filter(
        EmployeeUniform.expiry_date <= today + timedelta(days=30),
        EmployeeUniform.expiry_date >= today
    ).count()

    return render_template('storekeeper/uniform_accounting.html',
                           employees=employees,
                           uniform_types=uniform_types,
                           employee_uniforms=employee_uniforms,
                           total_issued=total_issued,
                           expiring_soon=expiring_soon,
                           today=today, current_time=datetime.now())


@app.route('/storekeeper/uniform/issue', methods=['POST'])
def issue_uniform():
    try:
        employee_uniform = EmployeeUniform(
            employee_id=request.form['employee_id'],
            uniform_type_id=request.form['uniform_type_id'],
            issue_date=datetime.strptime(
                request.form['issue_date'], '%Y-%m-%d').date(),
            quantity=request.form['quantity']
        )

        # Расчет даты истечения срока
        uniform_type = UniformType.query.get(request.form['uniform_type_id'])
        if uniform_type and uniform_type.wear_period:
            from dateutil.relativedelta import relativedelta
            employee_uniform.expiry_date = employee_uniform.issue_date + \
                relativedelta(months=uniform_type.wear_period)

        db.session.add(employee_uniform)
        db.session.commit()
        flash('Спецодежда успешно выдана', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при выдаче спецодежды: {str(e)}', 'error')

    return redirect(url_for('uniform_accounting'))


@app.route('/storekeeper/uniform/norms')
def uniform_norms():
    norms = PositionUniform.query.all()
    positions = Position.query.all()
    uniform_types = UniformType.query.all()

    return render_template('storekeeper/uniform_norms.html',
                           norms=norms,
                           positions=positions,
                           uniform_types=uniform_types, current_time=datetime.now())

# ========== КАБИНЕТ МЕХАНИКА ==========


@app.route('/mechanic')
def mechanic_index():
    return render_template('mechanic/index.html', current_time=datetime.now())


@app.route('/mechanic/checklists')
def checklists_list():
    checklists = Checklist.query.all()
    forms = ChecklistForm.query.all()
    return render_template('mechanic/checklists/list.html',
                           checklists=checklists,
                           forms=forms, current_time=datetime.now())


@app.route('/mechanic/checklists/forms/create', methods=['GET', 'POST'])
def create_checklist_form():
    if request.method == 'POST':
        try:
            form = ChecklistForm(
                name=request.form['form_name'],
                form_structure=request.form.get('form_structure', '{}')
            )

            db.session.add(form)
            db.session.commit()
            flash('Форма чек-листа успешно создана', 'success')
            return redirect(url_for('checklists_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании формы: {str(e)}', 'error')

    return render_template('mechanic/checklists/create_edit_form.html', current_time=datetime.now())


@app.route('/mechanic/checklists/forms/<int:form_id>/edit', methods=['GET', 'POST'])
def edit_checklist_form(form_id):
    form = ChecklistForm.query.get_or_404(form_id)

    if request.method == 'POST':
        try:
            form.name = request.form['form_name']
            form.form_structure = request.form.get('form_structure', '{}')
            form.updated_at = datetime.utcnow()

            db.session.commit()
            flash('Форма чек-листа успешно обновлена', 'success')
            return redirect(url_for('checklists_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении формы: {str(e)}', 'error')

    return render_template('mechanic/checklists/create_edit_form.html',
                           form=form, current_time=datetime.now())


@app.route('/mechanic/checklists/fill', methods=['GET', 'POST'])
def fill_checklist():
    if request.method == 'POST':
        try:
            checklist = Checklist(
                form_id=request.form['form_id'],
                filled_data=request.form.get('filled_data', '{}'),
                created_by=request.form['filled_by']
            )

            db.session.add(checklist)
            db.session.commit()
            flash('Чек-лист успешно заполнен', 'success')
            return redirect(url_for('checklists_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при заполнении чек-листа: {str(e)}', 'error')

    forms = ChecklistForm.query.all()
    return render_template('mechanic/checklists/fill_checklist.html',
                           forms=forms, current_time=datetime.now())


@app.route('/mechanic/acceptance_acts')
def acceptance_acts_list():
    acts = AcceptanceAct.query.all()
    act_forms = AcceptanceActForm.query.all()
    return render_template('mechanic/acceptance_acts/list.html',
                           acceptance_acts=acts,
                           act_forms=act_forms, current_time=datetime.now())

# ========== API ДЛЯ СПРАВОЧНИКОВ ==========


@app.route('/api/departments', methods=['GET', 'POST'])
def api_departments():
    if request.method == 'POST':
        data = request.get_json()
        new_dept = Department(name=data['name'])
        db.session.add(new_dept)
        db.session.commit()
        return jsonify({'id': new_dept.id, 'name': new_dept.name})

    departments = Department.query.all()
    return jsonify([{'id': dept.id, 'name': dept.name} for dept in departments])


@app.route('/api/departments/<int:dept_id>', methods=['DELETE'])
def api_delete_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    db.session.delete(department)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/positions', methods=['GET', 'POST'])
def api_positions():
    if request.method == 'POST':
        data = request.get_json()
        new_position = Position(name=data['name'])
        db.session.add(new_position)
        db.session.commit()
        return jsonify({'id': new_position.id, 'name': new_position.name})

    positions = Position.query.all()
    return jsonify([{'id': pos.id, 'name': pos.name} for pos in positions])

# @app.route('/api/vehicle_types', methods=['GET', 'POST'])
# def api_vehicle_types():
#     if request.method == 'POST':
#         data = request.get_json()
#         new_type = VehicleType(name=data['name'])
#         db.session.add(new_type)
#         db.session.commit()
#         return jsonify({'id': new_type.id, 'name': new_type.name})

#     types = VehicleType.query.all()
#     return jsonify([{'id': t.id, 'name': t.name} for t in types])


@app.route('/api/employees/search')
def api_employees_search():
    query = request.args.get('q', '')
    employees = Employee.query.filter(
        (Employee.last_name.ilike(f'%{query}%')) |
        (Employee.first_name.ilike(f'%{query}%')) |
        (Employee.pass_number.ilike(f'%{query}%'))
    ).limit(10).all()

    return jsonify([{
        'id': emp.id,
        'text': f"{emp.last_name} {emp.first_name} {emp.middle_name or ''}",
        'pass_number': emp.pass_number,
        'license_categories': emp.license_categories
    } for emp in employees])


@app.route('/api/vehicles/search')
def api_vehicles_search():
    query = request.args.get('q', '')
    vehicles = Vehicle.query.filter(
        (Vehicle.license_plate.ilike(f'%{query}%')) |
        (Vehicle.brand.ilike(f'%{query}%')) |
        (Vehicle.pass_number.ilike(f'%{query}%'))
    ).limit(10).all()

    return jsonify([{
        'id': veh.id,
        'text': f"{veh.brand} ({veh.license_plate})",
        'license_plate': veh.license_plate,
        'pass_number': veh.pass_number
    } for veh in vehicles])

# ========== СТАТИЧЕСКИЕ ФАЙЛЫ ==========


@app.route('/storage/<path:filename>')
def storage_files(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ========== ОБРАБОТЧИКИ ОШИБОК ==========


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', current_time=datetime.now()), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', current_time=datetime.now()), 500

# ========== КОМАНДЫ ДЛЯ ИНИЦИАЛИЗАЦИИ ==========


@app.cli.command('init-db')
def init_db_command():
    """Инициализация базы данных с тестовыми данными"""
    db.create_all()

    # Создаем базовые справочники если их нет
    if not Department.query.first():
        departments = [
            Department(name="Основной цех"),
            Department(name="Транспортный отдел"),
            Department(name="Склад")
        ]
        db.session.add_all(departments)

    if not Position.query.first():
        positions = [
            Position(name="Водитель"),
            Position(name="Механик"),
            Position(name="Диспетчер"),
            Position(name="Кладовщик")
        ]
        db.session.add_all(positions)

    if not VehicleType.query.first():
        vehicle_types = [
            VehicleType(name="Легковой автомобиль"),
            VehicleType(name="Грузовой автомобиль"),
            VehicleType(name="Автобус"),
            VehicleType(name="Спецтехника")
        ]
        db.session.add_all(vehicle_types)

    if not VehicleCategory.query.first():
        vehicle_categories = [
            VehicleCategory(name="B"),
            VehicleCategory(name="C"),
            VehicleCategory(name="D"),
            VehicleCategory(name="E")
        ]
        db.session.add_all(vehicle_categories)

    db.session.commit()
    print("База данных инициализирована с тестовыми данными")


@app.cli.command('cleanup-files')
def cleanup_files_command():
    """Очистка старых файлов"""
    file_handler.cleanup_old_files(
        app.config['UPLOAD_FOLDER'], max_age_days=30)
    print("Очистка старых файлов завершена")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Создаем базовые справочники если их нет
        if not Department.query.first():
            basic_dept = Department(name="Основной цех")
            db.session.add(basic_dept)
            db.session.commit()

        if not Position.query.first():
            basic_position = Position(name="Водитель")
            db.session.add(basic_position)
            db.session.commit()

        if not VehicleType.query.first():
            basic_type = VehicleType(name="Легковой автомобиль")
            db.session.add(basic_type)
            db.session.commit()

        if not VehicleCategory.query.first():
            basic_category = VehicleCategory(name="B")
            db.session.add(basic_category)
            db.session.commit()

    app.run(debug=True, host='0.0.0.0')
