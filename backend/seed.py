import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Employee, RoleEnum
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./dev.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Admin
    admin = User(email='admin@novapay.com', hashed_password=get_password_hash('Admin@123'), role=RoleEnum.ADMIN)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    # Manager
    manager = User(email='manager@example.com', hashed_password=get_password_hash('manager123'), role=RoleEnum.MANAGER)
    db.add(manager)
    db.commit()
    db.refresh(manager)
    # Employee
    employee = User(email='employee@example.com', hashed_password=get_password_hash('employee123'), role=RoleEnum.EMPLOYEE)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    emp_profile = Employee(user_id=employee.id, full_name='John Doe', position='Developer', department='Engineering')
    db.add(emp_profile)
    db.commit()
    print('Seeding completed')
    db.close()

if __name__ == '__main__':
    seed()
