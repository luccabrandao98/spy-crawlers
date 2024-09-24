import os
from sqlalchemy import create_engine

class AWSDatabase():

    def __init__(self, username, password, database, host):
        self.username = username
        self.password = password
        self.database = database
        self.host = host

    def connection(self):
        connection_string = f'postgresql://{self.username}:{self.password}@{self.host}/{self.database}'
        engine = create_engine(connection_string)

        # Test the connection
        try:
            connection = engine.connect()
            print("Connection successful!")
        except Exception as e:
            print(f"Connection failed! Error: {e}")

        # Close the connection
        engine.dispose()
        return connection