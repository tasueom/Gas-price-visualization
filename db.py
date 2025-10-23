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

if __name__ == "__main__":
    init_db()
    create_table()