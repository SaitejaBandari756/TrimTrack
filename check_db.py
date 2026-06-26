import sqlite3
import time

time.sleep(2)  

conn = sqlite3.connect('urlshortener.db')
cursor = conn.execute("SELECT short_code, click_count FROM urls WHERE short_code = 'oh6LdIkOsM'")
print("URL:", cursor.fetchall())

cursor2 = conn.execute("SELECT COUNT(*) FROM analytics WHERE short_code = 'oh6LdIkOsM'")
print("Analytics rows:", cursor2.fetchone()[0])

cursor3 = conn.execute("SELECT * FROM analytics WHERE short_code = 'oh6LdIkOsM'")
for row in cursor3.fetchall():
    print("  Analytics entry:", row)

conn.close()
