from app import app, db
from database.models import *

def init_database():
    with app.app_context():
        try:
            # Пытаемся удалить таблицы если они существуют
            db.drop_all()
            print("Старые таблицы удалены")
        except Exception as e:
            print(f"Ошибка при удалении таблиц: {e}")
            print("Продолжаем создание новых таблиц...")
        
        # Создаем все таблицы
        db.create_all()
        print("Созданы новые таблицы базы данных")
        
        # Создаем базовые справочники
        if not Department.query.first():
            departments = [
                Department(name="Основной цех"),
                Department(name="Транспортный отдел"),
                Department(name="Склад"),
                Department(name="Отдел безопасности")
            ]
            db.session.add_all(departments)
            print("Созданы подразделения")
        
        if not Position.query.first():
            positions = [
                Position(name="Водитель"),
                Position(name="Механик"),
                Position(name="Диспетчер"),
                Position(name="Кладовщик"),
                Position(name="Начальник отдела"),
                Position(name="Специалист по безопасности")
            ]
            db.session.add_all(positions)
            print("Созданы должности")
        
        if not VehicleType.query.first():
            vehicle_types = [
                VehicleType(name="Легковой автомобиль"),
                VehicleType(name="Грузовой автомобиль"),
                VehicleType(name="Автобус"),
                VehicleType(name="Спецтехника")
            ]
            db.session.add_all(vehicle_types)
            print("Созданы типы транспорта")
        
        if not VehicleCategory.query.first():
            vehicle_categories = [
                VehicleCategory(name="B"),
                VehicleCategory(name="C"),
                VehicleCategory(name="D"),
                VehicleCategory(name="E")
            ]
            db.session.add_all(vehicle_categories)
            print("Созданы категории транспорта")
        
        if not City.query.first():
            cities = [
                City(name="Москва"),
                City(name="Санкт-Петербург"),
                City(name="Новосибирск"),
                City(name="Екатеринбург")
            ]
            db.session.add_all(cities)
            print("Созданы города")
        
        # Добавляем согласующих лиц
        if not AgreementPerson.query.first():
            agreement_persons = [
                AgreementPerson(
                    full_name="Иванов Иван Иванович",
                    organization="ООО 'Транспортная компания'",
                    position="Начальник отдела безопасности"
                ),
                AgreementPerson(
                    full_name="Петров Петр Петрович",
                    organization="АО 'Промышленный комплекс'",
                    position="Главный инженер"
                )
            ]
            db.session.add_all(agreement_persons)
            print("Созданы согласующие лица")
        
        # Добавляем посты
        if not Post.query.first():
            posts = [
                Post(name="Пост №1 - Главный въезд", description="Основной контрольно-пропускной пункт"),
                Post(name="Пост №2 - Северный въезд", description="Северный КПП"),
                Post(name="Пост №3 - Южный въезд", description="Южный КПП"),
                Post(name="Пост №4 - Складская зона", description="КПП складской территории")
            ]
            db.session.add_all(posts)
            print("Созданы посты")
        
        # Добавляем договоры
        if not Contract.query.first():
            from datetime import date as date_class
            contracts = [
                Contract(
                    number="ДГ-001/2024",
                    name="Договор на транспортные услуги",
                    start_date=date_class(2024, 1, 15),
                    end_date=date_class(2024, 12, 31),
                    customer="ООО 'Промышленная компания'"
                ),
                Contract(
                    number="ДГ-002/2024", 
                    name="Договор подряда",
                    start_date=date_class(2024, 3, 1),
                    end_date=date_class(2024, 11, 30),
                    customer="АО 'Строительный комплекс'"
                )
            ]
            db.session.add_all(contracts)
            print("Созданы договоры")
        
        # Добавляем ИНН организаций
        if not OrganizationINN.query.first():
            inns = [
                OrganizationINN(
                    inn="1234567890",
                    organization_name="ООО 'Транспортная компания'",
                    contact_person="Иванов Иван Иванович",
                    phone="+7 (495) 123-45-67",
                    email="transport@mail.ru"
                ),
                OrganizationINN(
                    inn="0987654321", 
                    organization_name="АО 'Промышленный комплекс'",
                    contact_person="Петров Петр Петрович",
                    phone="+7 (495) 765-43-21", 
                    email="industry@mail.ru"
                )
            ]
            db.session.add_all(inns)
            print("Созданы ИНН организаций")
        
        # Добавляем аэропорты
        if not Airport.query.first():
            airports = [
                Airport(name="Шереметьево (SVO)", code="SVO"),
                Airport(name="Домодедово (DME)", code="DME"),
                Airport(name="Внуково (VKO)", code="VKO"),
                Airport(name="Пулково (LED)", code="LED")
            ]
            db.session.add_all(airports)
            print("Созданы аэропорты")
        
        # Добавляем типы спецодежды
        if not UniformType.query.first():
            uniform_types = [
                UniformType(name="Костюм рабочий", wear_period=12),
                UniformType(name="Куртка утепленная", wear_period=24),
                UniformType(name="Ботинки защитные", wear_period=12),
                UniformType(name="Перчатки", wear_period=3),
                UniformType(name="Каска", wear_period=36)
            ]
            db.session.add_all(uniform_types)
            print("Созданы типы спецодежды")
        
        db.session.commit()
        print("База данных успешно инициализирована!")

if __name__ == '__main__':
    init_database()