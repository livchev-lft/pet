import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from enum import Enum as PyEnum


Base = declarative_base()


class Status(PyEnum):
    NEW = "Новая"
    WAITING = "Ожидает подтверждения"
    DIAGNOSTIC = "На диагностике"
    REPAIR = "В ремонте"
    READY = "Готово"
    REJECTED = "Отклонена"
    COMPLETED = "Завершена"


class Role(PyEnum):
    diagnostic = "диагностик"
    admin = "админ"
    mechanic = "механик"
    superadmin = "админ"


class Priority(PyEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1


class Client(Base):
    __tablename__ = 'clients'
    telegram_id = Column(Integer, primary_key=True)
    username = Column(String(50))
    name = Column(String(100))
    phone = Column(String(20))
    registration_date = Column(DateTime, default=datetime.now)

    cars = relationship("Car", back_populates="client")
    applications = relationship("Application", back_populates="client")


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.telegram_id'))
    brand = Column(String(50))
    model = Column(String(50))
    number = Column(String(20))
    vin = Column(String(17), unique=True)
    year = Column(Integer)

    client = relationship("Client", back_populates="cars")
    applications = relationship("Application", back_populates="car")


class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.telegram_id'))
    car_id = Column(Integer, ForeignKey('cars.id'))
    date = Column(DateTime, default=datetime.now)
    problem_description = Column(Text)  # Описание проблемы клиентом
    admin_comment = Column(Text)  # Комментарий администратора
    diagnostic_report = Column(Text)  # Заключение диагноста
    mechanic_report = Column(Text)  # Отчёт механика
    status = Column(sqlalchemy.Enum(Status))
    priority = Column(sqlalchemy.Enum(Priority))
    diag_id = Column(Integer, ForeignKey('users.id'))
    mechanic_id = Column(Integer, ForeignKey('users.id'))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    update = Column(DateTime, onupdate=datetime.now)

    client = relationship("Client", back_populates="applications")
    car = relationship("Car", back_populates="applications")
    diagnostic = relationship("User", foreign_keys=[diag_id], back_populates="diagnostics")
    mechanic = relationship("User", foreign_keys=[mechanic_id], back_populates="repairs")
    payments = relationship("Payment", back_populates="application")
    participants = relationship("ApplicationUser", back_populates="application")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    role = Column(sqlalchemy.Enum(Role))

    diagnostics = relationship("Application", foreign_keys="[Application.diag_id]", back_populates="diagnostic")
    repairs = relationship("Application", foreign_keys="[Application.mechanic_id]", back_populates="mechanic")
    assigned_applications = relationship("ApplicationUser", back_populates="user")


class ApplicationUser(Base):
    __tablename__ = 'application_users'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'), primary_key=True)
    role = Column(sqlalchemy.Enum(Role))
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    user = relationship("User", back_populates="assigned_applications")
    application = relationship("Application", back_populates="participants")


class Payment(Base):
    __tablename__ = 'payments'
    application_id = Column(Integer, ForeignKey('applications.id'), primary_key=True)
    price = Column(Integer)
    payment_method = Column(String(50))
    time = Column(DateTime, default=datetime.now)

    application = relationship("Application", back_populates="payments")