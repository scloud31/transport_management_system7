from . import db
from .models import *
from datetime import datetime, date
import json

class DBUtils:
    
    @staticmethod
    def get_employee_full_info(employee_id):
        """Получение полной информации о сотруднике"""
        employee = Employee.query.get(employee_id)
        if not employee:
            return None
            
        return {
            'id': employee.id,
            'full_name': f"{employee.last_name} {employee.first_name} {employee.middle_name or ''}",
            'position': employee.position.name if employee.position else '',
            'department': employee.department.name if employee.department else '',
            'passport': f"{employee.passport_series} {employee.passport_number}" if employee.passport_series else '',
            'phone': employee.phone,
            'license_categories': employee.license_categories,
            'pass_number': employee.pass_number,
            'pass_expiry': employee.pass_expiry.strftime('%d.%m.%Y') if employee.pass_expiry else '',
            'photo_url': f"/storage/{employee.photo_path}" if employee.photo_path else None
        }
    
    @staticmethod
    def get_vehicle_full_info(vehicle_id):
        """Получение полной информации о транспорте"""
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return None
            
        return {
            'id': vehicle.id,
            'type': vehicle.vehicle_type.name if vehicle.vehicle_type else '',
            'brand': vehicle.brand,
            'license_plate': vehicle.license_plate,
            'category': vehicle.vehicle_category.name if vehicle.vehicle_category else '',
            'department': vehicle.department.name if vehicle.department else '',
            'year': vehicle.manufacture_year,
            'pass_number': vehicle.pass_number,
            'pass_expiry': vehicle.pass_expiry.strftime('%d.%m.%Y') if vehicle.pass_expiry else '',
            'insurance_expiry': vehicle.insurance_expiry.strftime('%d.%m.%Y') if vehicle.insurance_expiry else '',
            'inspection_expiry': vehicle.inspection_expiry.strftime('%d.%m.%Y') if vehicle.inspection_expiry else ''
        }
    
    @staticmethod
    def get_expiring_documents(days=30):
        """Получение документов, истекающих в течение указанных дней"""
        today = date.today()
        target_date = today + timedelta(days=days)
        
        expiring_employees = Employee.query.filter(
            (Employee.pass_expiry <= target_date) & (Employee.pass_expiry >= today) |
            (Employee.medical_exam_expiry <= target_date) & (Employee.medical_exam_expiry >= today) |
            (Employee.psychiatric_exam_expiry <= target_date) & (Employee.psychiatric_exam_expiry >= today)
        ).all()
        
        expiring_vehicles = Vehicle.query.filter(
            (Vehicle.pass_expiry <= target_date) & (Vehicle.pass_expiry >= today) |
            (Vehicle.insurance_expiry <= target_date) & (Vehicle.insurance_expiry >= today) |
            (Vehicle.inspection_expiry <= target_date) & (Vehicle.inspection_expiry >= today)
        ).all()
        
        return {
            'employees': expiring_employees,
            'vehicles': expiring_vehicles
        }
    
    @staticmethod
    def get_driver_shifts_count(employee_id, date):
        """Получение количества смен водителя за период"""
        # Логика подсчета смен для диспетчера
        daily_requests = DailyRequest.query.filter(
            DailyRequest.date >= date - timedelta(days=7),
            DailyRequest.date <= date
        ).all()
        
        shift_count = 0
        for request in daily_requests:
            vehicles_data = json.loads(request.vehicles_data)
            for vehicle in vehicles_data:
                if vehicle.get('driver_id') == employee_id:
                    shift_count += 1
        
        return shift_count
    
    @staticmethod
    def get_uniform_requirements():
        """Анализ потребности в спецодежде"""
        positions = Position.query.all()
        requirements = []
        
        for position in positions:
            # Нормы для должности
            norms = PositionUniform.query.filter_by(position_id=position.id).all()
            
            # Фактически выданная спецодежда
            employees = Employee.query.filter_by(position_id=position.id).all()
            
            for norm in norms:
                total_required = len(employees) * norm.quantity
                total_issued = EmployeeUniform.query.filter(
                    EmployeeUniform.employee_id.in_([e.id for e in employees]),
                    EmployeeUniform.uniform_type_id == norm.uniform_type_id,
                    EmployeeUniform.expiry_date >= date.today()
                ).count()
                
                deficit = total_required - total_issued
                if deficit > 0:
                    requirements.append({
                        'position': position.name,
                        'uniform_type': norm.uniform_type.name,
                        'required': total_required,
                        'issued': total_issued,
                        'deficit': deficit
                    })
        
        return requirements