import mysql.connector

# MySQL 기본 연결 설정 (데이터베이스를 지정하지 않고 접속)
base_config = {
    "host": "localhost",   # MySQL 서버 주소 (로컬)
    "user": "root",        # MySQL 계정
    "password": "1234"     # MySQL 비밀번호
}

# 사용할 데이터베이스 이름
DB_NAME = "gasanalysis"

def init_db():
    """데이터베이스 생성"""
    conn = mysql.connector.connect(**base_config)  # DB 없이 연결
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET utf8mb4")
        conn.commit()
        print(f"Database {DB_NAME} created successfully")
    except mysql.connector.Error as e:
        if e.errno == 1007:
            print(f"Database {DB_NAME} already exists")
        else:
            raise e
    finally:
        conn.close()

# 커넥션 반환하는 함수
def get_conn():
    return mysql.connector.connect(database=DB_NAME, **base_config)

def create_table():
    """테이블 생성"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
                    CREATE TABLE gas_station_prices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    gas_id VARCHAR(20) NOT NULL UNIQUE,
                    region VARCHAR(30) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    address VARCHAR(200) NOT NULL,
                    brand VARCHAR(50) NOT NULL,
                    self_type VARCHAR(10) NOT NULL,
                    premium_gasoline INT NOT NULL,
                    gasoline INT NOT NULL,
                    diesel INT NOT NULL,
                    kerosene INT NOT NULL)
                    """)
        conn.commit()
        print("Table 'gas_station_prices' created successfully")
    except mysql.connector.Error as e:
        if e.errno == 1064:
            print("Syntax error in SQL query")
        elif e.errno == 1050:
            print(f"Table 'gas_station_prices' already exists")
        else:
            raise e
    finally:
        conn.close()

def insert_data(data):
    """데이터 삽입"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO gas_station_prices 
            (gas_id, region, name, address, brand, self_type, 
            premium_gasoline, gasoline, diesel, kerosene) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        conn.commit()
        print(f"Data inserted successfully for gas_id: {data[0]}")
    except mysql.connector.Error as e:
        raise e
    finally:
        conn.close()

def get_data(sort_by='gas_id', order='asc', page=1, per_page=20, keyword='', column='gas_id'):
    """데이터 조회 (페이징, 정렬, 검색 지원)"""
    conn = get_conn()
    cur = conn.cursor()
    
    # 허용된 칼럼 검증
    allowed_columns = ['gas_id', 'region', 'name', 'address', 'brand', 
                        'self_type', 'premium_gasoline', 'gasoline', 'diesel', 'kerosene']
    if sort_by not in allowed_columns:
        sort_by = 'gas_id'
    if column not in allowed_columns:
        column = 'gas_id'
    if order not in ['asc', 'desc']:
        order = 'asc'
    
    # LIMIT과 OFFSET 계산
    offset = (page - 1) * per_page
    
    # 유종 칼럼으로 정렬 시 0보다 큰 값만 조회
    fuel_columns = ['premium_gasoline', 'gasoline', 'diesel', 'kerosene']
    fuel_filter = f"{sort_by} > 0" if sort_by in fuel_columns else ""
    
    if keyword:
        # 검색 조건 + 유종 필터
        where_clause = f"{column} LIKE %s"
        if fuel_filter:
            where_clause += f" AND {fuel_filter}"
        
        query = f"""
            SELECT gas_id, region, name, address, brand, self_type, 
            premium_gasoline, gasoline, diesel, kerosene 
            FROM gas_station_prices
            WHERE {where_clause}
            ORDER BY {sort_by} {order}
            LIMIT {per_page} OFFSET {offset}
        """
        cur.execute(query, (f'%{keyword}%',))
    else:
        # 유종 필터만
        if fuel_filter:
            query = f"""
                SELECT gas_id, region, name, address, brand, self_type, 
                premium_gasoline, gasoline, diesel, kerosene 
                FROM gas_station_prices
                WHERE {fuel_filter}
                ORDER BY {sort_by} {order}
                LIMIT {per_page} OFFSET {offset}
            """
        else:
            query = f"""
                SELECT gas_id, region, name, address, brand, self_type, 
                premium_gasoline, gasoline, diesel, kerosene 
                FROM gas_station_prices
                ORDER BY {sort_by} {order}
                LIMIT {per_page} OFFSET {offset}
            """
        cur.execute(query)
    
    rows = cur.fetchall()
    conn.close()
    return rows

def get_total_count(keyword='', column='gas_id', sort_by='gas_id'):
    """전체 데이터 개수 조회 (검색 조건 반영)"""
    conn = get_conn()
    cur = conn.cursor()
    
    # 허용된 칼럼 검증
    allowed_columns = ['gas_id', 'region', 'name', 'address', 'brand', 
                        'self_type', 'premium_gasoline', 'gasoline', 'diesel', 'kerosene']
    if column not in allowed_columns:
        column = 'gas_id'
    if sort_by not in allowed_columns:
        sort_by = 'gas_id'
    
    # 유종 칼럼으로 정렬 시 0보다 큰 값만 조회
    fuel_columns = ['premium_gasoline', 'gasoline', 'diesel', 'kerosene']
    fuel_filter = f"{sort_by} > 0" if sort_by in fuel_columns else ""
    
    if keyword:
        where_clause = f"{column} LIKE %s"
        if fuel_filter:
            where_clause += f" AND {fuel_filter}"
        query = f"SELECT COUNT(*) FROM gas_station_prices WHERE {where_clause}"
        cur.execute(query, (f'%{keyword}%',))
    else:
        if fuel_filter:
            query = f"SELECT COUNT(*) FROM gas_station_prices WHERE {fuel_filter}"
        else:
            query = "SELECT COUNT(*) FROM gas_station_prices"
        cur.execute(query)
    
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_all_rows():
    """모든 데이터를 rows(튜플 리스트)로 반환"""
    conn = get_conn()
    cur = conn.cursor()
    query = """
        SELECT gas_id, region, name, address, brand, self_type, 
        premium_gasoline, gasoline, diesel, kerosene 
        FROM gas_station_prices
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    create_table()