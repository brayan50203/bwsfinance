import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print("=== DADOS DOS INVESTIMENTOS ===")
rows = cursor.execute('SELECT id, name, amount, current_value, quantity FROM investments').fetchall()
print(f"{'ID':<5} | {'Nome':<15} | {'Amount':>12} | {'Current_Value':>15} | {'Quantity':>10}")
print("-" * 75)
for row in rows:
    print(f"{row[0]:<5} | {row[1]:<15} | {row[2]:>12.2f} | {row[3]:>15.2f} | {row[4] or 0:>10.2f}")

conn.close()
