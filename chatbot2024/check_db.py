import sqlite3
import os

db_path = 'QA.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    print(f'数据库中的表: {tables}')
    
    # 检查每个表的内容
    for table_name in tables:
        table = table_name[0]
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'\n表 {table} 有 {count} 条记录')
        
        # 显示前3条记录
        if count > 0:
            cursor.execute(f'SELECT * FROM {table} LIMIT 3')
            rows = cursor.fetchall()
            print(f'前3条记录示例:')
            for row in rows:
                print(row)
    
    conn.close()
else:
    print('数据库文件不存在')