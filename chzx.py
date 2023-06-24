import psycopg2 
from urllib.parse import urlparse 
from config import host, user, password, db_name, port, log_pattern
import re

global connection
connection = False

def parsing_to_bd(line, cursor): 
    match = re.match(log_pattern, line) 
    if match: 
        ip_address = match.group(1) 
        date_time = match.group(4) 
        request_method = match.group(5) 
        status_code = match.group(6) 
        response_size = match.group(7) 
        referer = match.group(8) 
        user_agent = match.group(9) 
        select_query = """ 
            SELECT COUNT(*) FROM Data WHERE Data_Address_ID = %s AND Data_Date_Time = %s 
        """ 
        cursor.execute(select_query, (ip_address, date_time)) 
        count = cursor.fetchone()[0] 
         
        if count == 0: 
            insert_query = """ 
                INSERT INTO Data (Data_Address_ID, Data_Date_Time, Data_Request_Method, Data_Status_Code, Data_Response_Size, Data_Referer, Data_User_Agent) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
            """ 
            values = (ip_address, date_time, request_method, status_code, response_size, referer, user_agent) 
            cursor.execute(insert_query, values) 
            connection.commit() 
        print(ip_address,date_time,request_method,status_code,response_size,referer,user_agent)
    else: 
        print('Не удалось распарсить лог.')
        
def get_grouped_by_date_data(cursor):
    cursor.execute("""
                   SELECT CONCAT('дата: ', DATE(Data_Date_Time)), CONCAT('количество записей: ', COUNT(*)) 
                   FROM Data 
                   GROUP BY DATE(Data_Date_Time);
                   """)
    rows = cursor.fetchall()
    return print(rows)      
      
def get_grouped_by_IP(cursor):
    cursor.execute("""
                   SELECT CONCAT('IP: ', Data_Address_ID), CONCAT('количество записей: ', COUNT(*)) 
                   FROM Data 
                   GROUP BY Data_Address_ID;
                   """)
    rows = cursor.fetchall()
    return print(rows) 

def get_grouped_by_Date_Interval(cursor,start_date,end_date):
    query = """ 
                SELECT  Data_Address_ID, Data_Date_Time, Data_Request_Method, Data_Status_Code, Data_Response_Size, Data_Referer, Data_User_Agent 
                FROM Data 
                WHERE DATE(Data_Date_Time) BETWEEN %s AND %s ORDER BY Data_Date_Time ASC
            """
    values = (start_date, end_date) 
    cursor.execute(query, values)
    rows = cursor.fetchall()
    return print(rows) 

def json_grouped_by_ip(cursor):
    query = """
                SELECT 
                Data_Address_ID AS ip, 
                json_agg(row_to_json(Data)) AS data
                FROM Data 
                GROUP BY Data_Address_ID;
            """
    cursor.execute(query)
    rows = cursor.fetchall()
    arr=[]
    for row in rows:
        ip = row[0]
        data = row[1]
        arr.append(f'{ip},{data}')
    return print(arr)

def json_grouped_by_date(cursor):
    query = """
                SELECT 
                DATE(Data_Date_Time) AS date,  
                json_agg(to_json(Data)) AS data
                FROM Data 
                GROUP BY DATE(Data_Date_Time);
            """
    cursor.execute(query)
    rows = cursor.fetchall()
    arr=[]
    for row in rows:
        date = row[0]
        data = row[1]
        arr.append(f'{date},{data}')
    return print(arr)

def json_grouped_by_Date_Interval(cursor, start_date,end_date):
    query = """ 
                SELECT json_agg(to_json(Data))
                FROM Data WHERE DATE(Data_Date_Time) BETWEEN %s AND %s
                GROUP BY (Data_Address_ID, Data_Date_Time, Data_Request_Method, Data_Status_Code, Data_Response_Size, Data_Referer, Data_User_Agent) 
                ORDER BY Data_Date_Time ASC 
            """
    values = (start_date, end_date) 
    cursor.execute(query, values)
    rows = cursor.fetchall()
    return print(rows) 


try: 
    connection = psycopg2.connect( 
        host = host, 
        user = user, 
        password = password, 
        database = db_name,
        port = port
    ) 
    
    with connection.cursor() as cursor: 
        cursor.execute("SELECT version()")
        print(cursor.fetchone())
        
        with open("logs.log") as log: 
                for line in log: 
                    parsing_to_bd(line, cursor)
        
        condition = True
        
        while condition:
            
            print('\n 1. группировка логов по дате. \n 2. группировка логов по IP. \n 3. фильтрация логов по промежутку дат. \n 4. группировка логов по IP и вывод в формате JSON. \n 5. группировка логов по дате и вывод в формате JSON. \n 6. фильтрация логов по промежутку дат и вывод в формате JSON.')
            print('введите число, чтобы выбрать функцию.')
            answer = int(input())
            if(answer == 1):
                get_grouped_by_date_data(cursor)
                
            if(answer == 2):
                get_grouped_by_IP(cursor)
                
            if(answer == 3):
                start_date = input('формат даты: YYYY-MM-DD \n назначте началную дату: ')
                end_date = input('назначте конечную дату: ')
                get_grouped_by_Date_Interval(cursor,start_date,end_date)
                
            if(answer == 4):
                json_grouped_by_ip(cursor)
                
            if(answer == 5):
                json_grouped_by_date(cursor)
                
            if(answer == 6):
                start_date = input('формат даты: YYYY-MM-DD \n назначте началную дату: ')
                end_date = input('назначте конечную дату: ')
                json_grouped_by_Date_Interval(cursor,start_date,end_date)
                
            if(input('если хотите завершить программу введите n, если хотите продолжить, нажмите любую другую кнопку\n')=='n'):
                condition = False
         
except Exception as __ex: 
    print(__ex) 
finally: 
    if connection: 
        connection.close() 
        print('Postgre connection has been closed')