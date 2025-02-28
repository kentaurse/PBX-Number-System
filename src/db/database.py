import mysql.connector
from datetime import datetime
from config.config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = None
        
    async def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            print("Database connected successfully")
        except mysql.connector.Error as e:
            print(f"Database connection failed: {e}")
            raise
            
    async def disconnect(self):
        if self.connection:
            self.connection.close()
            
    async def save_call_data(self, call_data):
        if not self.connection:
            await self.connect()
            
        cursor = self.connection.cursor()
        try:
            sql = """
                INSERT INTO incoming_calls 
                (timestamp, caller_number, called_number, pbx_type) 
                VALUES (%s, %s, %s, %s)
            """
            values = (
                call_data.get('timestamp', datetime.now()),
                call_data.get('caller_number'),
                call_data.get('called_number'),
                call_data.get('pbx_type')
            )
            cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Failed to save call data: {e}")
            self.connection.rollback()
        finally:
            cursor.close() 