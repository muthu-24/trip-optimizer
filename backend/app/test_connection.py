from sqlalchemy import text

try:
    from app.database import engine
except ImportError:
    from database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print("Result:", result.scalar())

except Exception as error:
    print("Database connection failed!")
    print("Error:", error)