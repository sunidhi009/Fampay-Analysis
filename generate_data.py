import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
N = 5000

users = pd.DataFrame({
    'user_id': [f'U{str(i).zfill(4)}' for i in range(1, N+1)],
    'age': np.random.choice(
        [13,14,15,16,17,18,19,20,21,22,23,24,25],
        size=N,
        p=[0.05,0.07,0.08,0.09,0.10,0.12,0.11,0.10,0.09,0.07,0.06,0.04,0.02]
    ),
    'city_tier': np.random.choice(
        ['Tier 1', 'Tier 2', 'Tier 3'], N, p=[0.4, 0.35, 0.25]
    ),
    'signup_date': [
        datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        for _ in range(N)
    ],
    'card_activated': np.random.choice([1, 0], N, p=[0.65, 0.35]),
    'upi_linked': np.random.choice([1, 0], N, p=[0.70, 0.30]),
    'referral_used': np.random.choice([1, 0], N, p=[0.40, 0.60]),
})

transactions = []
for _, user in users.iterrows():
    if user['card_activated'] == 0:
        continue
    num_txns = np.random.randint(0, 25)
    for _ in range(num_txns):
        txn_date = user['signup_date'] + timedelta(days=random.randint(1, 180))
        transactions.append({
            'txn_id': f"T{random.randint(100000, 999999)}",
            'user_id': user['user_id'],
            'txn_date': txn_date,
            'txn_type': random.choice(['UPI', 'FamCard', 'QR']),
            'category': random.choice([
                'Food', 'Shopping', 'Entertainment',
                'Transport', 'Education', 'Gaming'
            ]),
            'amount': round(np.random.exponential(scale=350), 2),
            'status': np.random.choice(
                ['success', 'failed', 'pending'],
                p=[0.85, 0.10, 0.05]
            )
        })

funnel_events = []
stages = ['app_downloaded','registered','kyc_completed',
          'card_activated','first_transaction']
for _, user in users.iterrows():
    completed = True
    for i, stage in enumerate(stages):
        drop_probs = [0.05, 0.15, 0.25, 0.35, 0.45]
        if not completed:
            break
        funnel_events.append({
            'user_id': user['user_id'],
            'stage': stage,
            'event_date': user['signup_date'] + timedelta(days=i)
        })
        if random.random() < drop_probs[i]:
            completed = False

users.to_csv('users.csv', index=False)
pd.DataFrame(transactions).to_csv('transactions.csv', index=False)
pd.DataFrame(funnel_events).to_csv('funnel_events.csv', index=False)

print(f"✅ Generated {len(users)} users")
print(f"✅ Generated {len(transactions)} transactions")
print(f"✅ Generated {len(funnel_events)} funnel events")