# app/database/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Путь к БД внутри папки database
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "repair_requests.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаём БД, если не существует
db_just_created = not os.path.exists(DB_PATH)
if db_just_created:
    Base.metadata.create_all(bind=engine)
    # Импортируем данные при создании новой БД
    try:
        from scripts.import_data import import_all_data
        import_all_data(engine)
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать данные: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка при импорте данных: {e}")