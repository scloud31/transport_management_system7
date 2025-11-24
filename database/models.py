from . import db
from datetime import datetime
import json


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Position(db.Model):
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VehicleType(db.Model):
    __tablename__ = 'vehicle_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VehicleCategory(db.Model):
    __tablename__ = 'vehicle_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))
    passport_series = db.Column(db.String(4))
    passport_number = db.Column(db.String(6))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    has_driver_license = db.Column(db.Boolean, default=False)
    license_categories = db.Column(db.String(100))
    pass_number = db.Column(db.String(50))
    pass_expiry = db.Column(db.Date)
    medical_exam_expiry = db.Column(db.Date)
    medical_exam_not_required = db.Column(db.Boolean, default=False)
    psychiatric_exam_expiry = db.Column(db.Date)
    psychiatric_exam_not_required = db.Column(db.Boolean, default=False)
    clothing_size = db.Column(db.String(10))
    shoe_size = db.Column(db.String(10))
    height = db.Column(db.String(10))
    photo_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = db.relationship('Department', backref='employees')
    position = db.relationship('Position', backref='employees')
    city = db.relationship('City', backref='employees')

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}"

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey('vehicle_types.id'))
    brand = db.Column(db.String(100), nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    vehicle_category_id = db.Column(db.Integer, db.ForeignKey('vehicle_categories.id'))
    manufacture_year = db.Column(db.Integer)
    pass_number = db.Column(db.String(50))
    pass_expiry = db.Column(db.Date)
    insurance_expiry = db.Column(db.Date)
    inspection_expiry = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle_type = db.relationship('VehicleType', backref='vehicles')
    vehicle_category = db.relationship('VehicleCategory', backref='vehicles')
    department = db.relationship('Department', backref='vehicles')

# Справочники для заявок на пропуска
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(300))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    customer = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrganizationINN(db.Model):
    __tablename__ = 'organization_inns'
    id = db.Column(db.Integer, primary_key=True)
    inn = db.Column(db.String(12), nullable=False, unique=True)
    organization_name = db.Column(db.String(300), nullable=False)
    contact_person = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgreementPerson(db.Model):
    __tablename__ = 'agreement_persons'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(300))
    position = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PassRequest(db.Model):
    __tablename__ = 'pass_requests'
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(50), nullable=False)
    post_ids = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    inn_id = db.Column(db.Integer, db.ForeignKey('organization_inns.id'))
    purpose = db.Column(db.Text)
    formed_by = db.Column(db.String(200), nullable=False)
    agreement_person_id = db.Column(db.Integer, db.ForeignKey('agreement_persons.id'))
    is_one_time = db.Column(db.Boolean, default=False)
    employee_ids = db.Column(db.Text)
    vehicle_ids = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    template_path = db.Column(db.String(500))
    generated_document_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contract = db.relationship('Contract', backref='pass_requests')
    organization_inn = db.relationship('OrganizationINN', backref='pass_requests')
    agreement_person = db.relationship('AgreementPerson', backref='pass_requests')

# Модели для перевахтовки
class Airport(db.Model):
    __tablename__ = 'airports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ShiftRequest(db.Model):
    __tablename__ = 'shift_requests'
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(20), nullable=False)  # charter, regular, auto
    flight_date = db.Column(db.Date)
    departure_airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'))
    arrival_airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'))
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    flight_number = db.Column(db.String(20))
    preliminary_cost = db.Column(db.String(100))
    auto_delivery_from = db.Column(db.String(200))
    auto_delivery_to = db.Column(db.String(200))
    formed_by = db.Column(db.String(200))
    employees = db.Column(db.Text)  # JSON список ID сотрудников
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contract = db.relationship('Contract', backref='shift_requests')
    departure_airport = db.relationship('Airport', foreign_keys=[departure_airport_id], backref='departure_shift_requests')
    arrival_airport = db.relationship('Airport', foreign_keys=[arrival_airport_id], backref='arrival_shift_requests')

# Модели для учета электроэнергии
class ElectricityReading(db.Model):
    __tablename__ = 'electricity_readings'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    previous_bpo = db.Column(db.String(20))
    previous_dormitory = db.Column(db.String(20))
    current_bpo = db.Column(db.String(20))
    current_dormitory = db.Column(db.String(20))
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Модели для нарядов-допусков
class WorkPermit(db.Model):
    __tablename__ = 'work_permits'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False)
    tire_type = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    responsible_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    template_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    supervisor = db.relationship('Employee', foreign_keys=[supervisor_id], backref='supervised_permits')
    responsible = db.relationship('Employee', foreign_keys=[responsible_id], backref='responsible_permits')
    executor = db.relationship('Employee', foreign_keys=[executor_id], backref='executed_permits')

# Модели для диспетчера
class DailyRequest(db.Model):
    __tablename__ = 'daily_requests'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    shift_type = db.Column(db.String(10))  # day, night
    vehicles_data = db.Column(db.Text)  # JSON данные по технике
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Модели для отдела безопасности
class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    questions = db.Column(db.Text)  # JSON структура вопросов
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestResult(db.Model):
    __tablename__ = 'test_results'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))
    employee_name = db.Column(db.String(200), nullable=False)
    answers = db.Column(db.Text)  # JSON ответов
    score = db.Column(db.Integer)
    max_score = db.Column(db.Integer)
    passed = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    test = db.relationship('Test', backref='results')

# Модели для кладовщика
class TTN(db.Model):
    __tablename__ = 'ttns'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    number = db.Column(db.String(50), nullable=False)
    sender_organization = db.Column(db.String(300))
    receiver_organization = db.Column(db.String(300))
    places_count = db.Column(db.String(20))
    cargo_weight = db.Column(db.String(20))
    loading_address = db.Column(db.String(300))
    unloading_address = db.Column(db.String(300))
    loading_time = db.Column(db.String(10))
    sender_individual = db.Column(db.String(200))
    sender_legal = db.Column(db.String(200))
    carrier_individual = db.Column(db.String(200))
    vehicle_info = db.Column(db.String(200))
    waybill_number = db.Column(db.String(50))
    trailer_info = db.Column(db.String(200))
    template_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UniformType(db.Model):
    __tablename__ = 'uniform_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    wear_period = db.Column(db.Integer)  # срок носки в месяцах
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EmployeeUniform(db.Model):
    __tablename__ = 'employee_uniforms'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    uniform_type_id = db.Column(db.Integer, db.ForeignKey('uniform_types.id'))
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', backref='uniforms')
    uniform_type = db.relationship('UniformType', backref='employee_uniforms')

class PositionUniform(db.Model):
    __tablename__ = 'position_uniforms'
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))
    uniform_type_id = db.Column(db.Integer, db.ForeignKey('uniform_types.id'))
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    position = db.relationship('Position', backref='uniform_norms')
    uniform_type = db.relationship('UniformType', backref='position_norms')

# Модели для механика
class ChecklistForm(db.Model):
    __tablename__ = 'checklist_forms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    form_structure = db.Column(db.Text)  # JSON структура формы
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Checklist(db.Model):
    __tablename__ = 'checklists'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('checklist_forms.id'))
    filled_data = db.Column(db.Text)  # JSON заполненных данных
    created_by = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    form = db.relationship('ChecklistForm', backref='checklists')

class AcceptanceActForm(db.Model):
    __tablename__ = 'acceptance_act_forms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    act_type = db.Column(db.String(50))
    form_structure = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AcceptanceAct(db.Model):
    __tablename__ = 'acceptance_acts'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('acceptance_act_forms.id'))
    filled_data = db.Column(db.Text)
    created_by = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    form = db.relationship('AcceptanceActForm', backref='acceptance_acts')