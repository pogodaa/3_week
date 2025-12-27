# # scripts/import_data.py
# import pandas as pd
# from sqlalchemy.orm import sessionmaker
# from app.database.database import engine
# from app.models import User, RepairRequest as Request, Comment  # ← исправлено!

# Session = sessionmaker(bind=engine)
# session = Session()

# # Добавляем админа с userID = 0
# admin_exists = session.query(User).filter(User.login == "admin").first()
# if not admin_exists:
#     admin = User(
#         userID=0,  # ← именно 0, как ты просил
#         fio="Администратор Системы",
#         phone="88005553535",
#         login="admin",
#         password="admin",
#         type="Админ"
#     )
#     session.add(admin)
#     session.commit()

# def import_users():
#     df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Пользователи/inputDataUsers.xlsx")
#     for _, row in df.iterrows():
#         user = User(
#             userID=row["userID"],
#             fio=row["fio"],
#             phone=row["phone"],
#             login=row["login"],
#             password=row["password"],
#             type=row["type"]
#         )
#         session.merge(user)

# def import_requests():
#     df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Заявки/inputDataRequests.xlsx")
#     for _, row in df.iterrows():
#         req = Request(  # ← теперь это RepairRequest, но с псевдонимом Request
#             requestID=row["requestID"],
#             startDate=str(row["startDate"]),
#             climateTechType=row["climateTechType"],
#             climateTechModel=row["climateTechModel"],
#             problemDescryption=row["problemDescryption"],
#             requestStatus=row["requestStatus"],
#             completionDate=str(row["completionDate"]) if pd.notna(row["completionDate"]) else None,
#             repairParts=row["repairParts"] if pd.notna(row["repairParts"]) else None,
#             masterID=int(row["masterID"]) if pd.notna(row["masterID"]) else None,
#             clientID=int(row["clientID"])
#         )
#         session.merge(req)

# def import_comments():
#     df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Комментарии/inputDataComments.xlsx")
#     for _, row in df.iterrows():
#         comment = Comment(
#             commentID=row["commentID"],
#             message=row["message"],
#             masterID=row["masterID"],
#             requestID=row["requestID"]
#         )
#         session.merge(comment)

# if __name__ == "__main__":
#     import_users()
#     import_requests()
#     import_comments()
#     session.commit()
#     session.close()
#     print("✅ Данные успешно импортированы в SQLite")

# scripts/import_data.py
import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.models import User, RepairRequest as Request, Comment

def get_base_path():
    """Получает путь к корню проекта."""
    # Получаем путь к текущему файлу (scripts/import_data.py)
    current_file = os.path.abspath(__file__)
    # Поднимаемся на два уровня вверх (scripts -> корень проекта)
    project_root = os.path.dirname(os.path.dirname(current_file))
    return os.path.join(project_root, "docs_MAIN", "src", "Ресурсы", "import_БытСервис")

def create_admin(session):
    """Создаёт администратора, если его ещё нет."""
    admin_exists = session.query(User).filter(User.login == "admin").first()
    if not admin_exists:
        admin = User(
            userID=0,
            fio="Администратор Системы",
            phone="88005553535",
            login="admin",
            password="admin",
            type="Админ"
        )
        session.add(admin)
        session.commit()
        return True
    return False

def import_users(session, base_path=None):
    """Импортирует пользователей из Excel файла."""
    if base_path is None:
        base_path = get_base_path()
    users_path = os.path.join(base_path, "Пользователи", "inputDataUsers.xlsx")
    if not os.path.exists(users_path):
        print(f"⚠️ Файл не найден: {users_path}")
        return
    
    df = pd.read_excel(users_path)
    for _, row in df.iterrows():
        user = User(
            userID=row["userID"],
            fio=row["fio"],
            phone=row["phone"],
            login=row["login"],
            password=row["password"],
            type=row["type"]
        )
        session.merge(user)
    print(f"✅ Импортировано пользователей: {len(df)}")

def import_requests(session, base_path=None):
    """Импортирует заявки из Excel файла."""
    if base_path is None:
        base_path = get_base_path()
    requests_path = os.path.join(base_path, "Заявки", "inputDataRequests.xlsx")
    if not os.path.exists(requests_path):
        print(f"⚠️ Файл не найден: {requests_path}")
        return
    
    df = pd.read_excel(requests_path)
    for _, row in df.iterrows():
        # Поддержка разных названий полей: homeTechType/homeTechModel, applianceType/applianceModel, climateTechType/climateTechModel
        appliance_type = row.get("homeTechType") or row.get("applianceType") or row.get("climateTechType", "")
        appliance_model = row.get("homeTechModel") or row.get("applianceModel") or row.get("climateTechModel", "")
        
        req = Request(
            requestID=row["requestID"],
            startDate=str(row["startDate"]),
            applianceType=appliance_type,
            applianceModel=appliance_model,
            problemDescryption=row["problemDescryption"],
            requestStatus=row["requestStatus"],
            completionDate=str(row["completionDate"]) if pd.notna(row["completionDate"]) else None,
            repairParts=row["repairParts"] if pd.notna(row["repairParts"]) else None,
            masterID=int(row["masterID"]) if pd.notna(row["masterID"]) else None,
            clientID=int(row["clientID"])
        )
        session.merge(req)
    print(f"✅ Импортировано заявок: {len(df)}")

def import_comments(session, base_path=None):
    """Импортирует комментарии из Excel файла."""
    if base_path is None:
        base_path = get_base_path()
    comments_path = os.path.join(base_path, "Комментарии", "inputDataComments.xlsx")
    if not os.path.exists(comments_path):
        print(f"⚠️ Файл не найден: {comments_path}")
        return
    
    requests_path = os.path.join(base_path, "Заявки", "inputDataRequests.xlsx")
    if not os.path.exists(requests_path):
        print(f"⚠️ Файл не найден: {requests_path}")
        return
    
    df = pd.read_excel(comments_path)
    # Загрузим заявки в словарь для быстрого доступа
    requests_df = pd.read_excel(requests_path)
    request_dates = dict(zip(requests_df["requestID"], requests_df["startDate"]))
    
    for _, row in df.iterrows():
        # Получаем дату создания заявки
        request_id = row["requestID"]
        comment_date = str(request_dates.get(request_id, pd.Timestamp.today().strftime("%Y-%m-%d")))
        
        comment = Comment(
            commentID=row["commentID"],
            message=row["message"],
            masterID=row["masterID"],
            requestID=request_id,
            created_at=comment_date
        )
        session.merge(comment)
    print(f"✅ Импортировано комментариев: {len(df)}")

def import_all_data(engine, base_path=None):
    """Импортирует все данные из Excel файлов в базу данных."""
    if base_path is None:
        base_path = get_base_path()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Создаём администратора
        create_admin(session)
        
        # Импортируем данные
        import_users(session, base_path)
        import_requests(session, base_path)
        import_comments(session, base_path)
        
        session.commit()
        print("✅ Все данные успешно импортированы в SQLite")
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка при импорте данных: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    from app.database.database import engine
    import_all_data(engine)