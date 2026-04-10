import psycopg

# DB_URI = "postgresql://postgres:123123@192.168.0.60:5442/langgraph"

conn = psycopg.connect(
    host="localhost",  # 或 127.0.0.1
    port=5432,        # 显式指定端口
    dbname="postgres",
    user="postgres",
    password="123123",
    connect_timeout=5  # 避免因网络问题卡死
)

print(conn)