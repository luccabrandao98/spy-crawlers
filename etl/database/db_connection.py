import os
from sqlalchemy import create_engine, VARCHAR, Float, Date, text

def aws_rds_connection():
    username = os.environ['AWS_RDS_USER']
    password = os.environ['AWS_RDS_KEY']
    database = 'spy'
    host = os.environ['AWS_RDS_HOST']

    # Create a connection string
    connection_string = f'postgresql://{username}:{password}@{host}/{database}'

    # Create the engine
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

aws_rds_connection()