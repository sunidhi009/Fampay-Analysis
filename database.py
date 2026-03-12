import pandas as pd
import sqlite3

conn = sqlite3.connect('fampay.db')

pd.read_csv('users.csv').to_sql('users', conn, if_exists='replace', index=False)
pd.read_csv('transactions.csv').to_sql('transactions', conn, if_exists='replace', index=False)
pd.read_csv('funnel_events.csv').to_sql('funnel_events', conn, if_exists='replace', index=False)

conn.close()
print("✅ fampay.db created successfully!")