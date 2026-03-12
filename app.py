import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="FamPay Product Analytics",
    layout="wide",
    page_icon="💳",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1100px;
    }
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.1rem !important; }
    .stMetric { background-color: #1e1e2e; padding: 8px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    users  = pd.read_csv('users.csv')
    txns   = pd.read_csv('transactions.csv')
    funnel = pd.read_csv('funnel_events.csv')
    users['signup_date'] = pd.to_datetime(users['signup_date'])
    txns['txn_date']     = pd.to_datetime(txns['txn_date'])
    return users, txns, funnel

users, txns, funnel = load_data()

# ── HEADER ──────────────────────────────────────────────
st.title("💳 FamPay Product Analytics Dashboard")
st.caption("Youth UPI & Payments Platform — Simulated Data Analysis")

# ── KPI CARDS ────────────────────────────────────────────
st.subheader("📊 Key Metrics")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Users",     f"{len(users):,}")
k2.metric("Card Activated",  f"{users['card_activated'].sum():,}")
k3.metric("UPI Linked",      f"{users['upi_linked'].sum():,}")
k4.metric("Transactions",    f"{len(txns):,}")
sr = round(txns[txns['status']=='success'].shape[0]*100/len(txns),1)
k5.metric("Success Rate",    f"{sr}%")

st.divider()

# ── ROW 1 : FUNNEL + CITY TIER ────────────────────────────
c1, c2 = st.columns([1.6, 1])

with c1:
    st.subheader("🔽 Onboarding Funnel")
    stages = ['app_downloaded','registered','kyc_completed',
              'card_activated','first_transaction']
    fcounts = funnel.groupby('stage')['user_id'].nunique().reindex(stages)

    fig, ax = plt.subplots(figsize=(5.5, 2.8))
    colors  = ['#4F8EF7','#5B9BF8','#6CA8F9','#7DB5FA','#FF6B6B']
    bars    = ax.bar(stages, fcounts.values, color=colors, edgecolor='white')
    for b, v in zip(bars, fcounts.values):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+25,
                f'{v:,}', ha='center', fontsize=7.5, fontweight='bold')
    ax.set_ylim(0, max(fcounts.values)*1.18)
    ax.set_ylabel('Users', fontsize=8)
    ax.tick_params(axis='x', labelsize=7)
    ax.tick_params(axis='y', labelsize=7)
    plt.xticks(rotation=22)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)

    fdf = pd.DataFrame({
        'Stage': stages,
        'Users': fcounts.values,
        '% Remaining': (fcounts.values/fcounts.values[0]*100).round(1)
    })
    st.dataframe(fdf, use_container_width=True, hide_index=True)

with c2:
    st.subheader("🏙️ City Tier Activation")
    city = users.groupby('city_tier').agg(
        Total=('user_id','count'),
        Activated=('card_activated','sum')
    ).reset_index()
    city['Rate %'] = (city['Activated']/city['Total']*100).round(1)

    fig2, ax2 = plt.subplots(figsize=(3.5, 2.8))
    b2 = ax2.bar(city['city_tier'], city['Rate %'],
                 color=['#4F8EF7','#6CA8F9','#FF6B6B'], width=0.45)
    for b, v in zip(b2, city['Rate %']):
        ax2.text(b.get_x()+b.get_width()/2, b.get_height()+0.4,
                 f'{v}%', ha='center', fontsize=8, fontweight='bold')
    ax2.set_ylim(0, 82)
    ax2.set_ylabel('Activation %', fontsize=8)
    ax2.tick_params(labelsize=8)
    plt.tight_layout()
    st.pyplot(fig2, use_container_width=False)

    st.dataframe(city[['city_tier','Total','Activated','Rate %']],
                 use_container_width=True, hide_index=True)

st.divider()

# ── ROW 2 : COHORT HEATMAP ────────────────────────────────
st.subheader("👥 Cohort Retention Analysis (D1 / D7 / D30)")

merged = txns[txns['status']=='success'].merge(
    users[['user_id','signup_date']], on='user_id')
merged['days'] = (merged['txn_date'] - merged['signup_date']).dt.days
merged['cohort'] = merged['signup_date'].dt.to_period('M').astype(str)
csizes = users.groupby(
    users['signup_date'].dt.to_period('M').astype(str))['user_id'].nunique()

def ret(d):
    return merged[merged['days']<=d].groupby('cohort')['user_id'].nunique()

cdf = pd.DataFrame({
    'Size': csizes, 'D1': ret(1), 'D7': ret(7), 'D30': ret(30)
}).fillna(0)
cpct = cdf[['D1','D7','D30']].div(cdf['Size'], axis=0)*100

fig3, ax3 = plt.subplots(figsize=(5, 1.5))
sns.heatmap(cpct.round(1), annot=True, fmt='.1f', cmap='Blues',
            ax=ax3, linewidths=0.2, annot_kws={"size": 4})
ax3.set_title('Retention Rate (%) by Signup Cohort', fontsize=8, fontweight='bold')
ax3.tick_params(labelsize=6)
plt.tight_layout()
st.pyplot(fig3, use_container_width=False)

st.divider()

# ── ROW 3 : PAYMENT + AGE GROUP ──────────────────────────
c3, c4 = st.columns([1, 1.6])
 
with c3:
    st.subheader("💸 Payment Method Split")
    pay = txns.groupby('txn_type').agg(
        Txns=('txn_id','count'),
        Avg=('amount','mean'),
        Fail=('status', lambda x: (x=='failed').mean()*100)
    ).round(2).reset_index()
    pay.columns = ['Type','Transactions','Avg ₹','Fail %']
    st.dataframe(pay, use_container_width=True, hide_index=True)
 
    fig4, ax4 = plt.subplots(figsize=(3.5, 3))
    ax4.pie(pay['Transactions'], labels=pay['Type'],
            autopct='%1.1f%%',
            colors=['#4F8EF7','#FF6B6B','#6CA8F9'],
            textprops={'fontsize': 8})
    plt.tight_layout()
    st.pyplot(fig4, use_container_width=False)
 
with c4:
    st.subheader("🎯 Spending by Age Group & Category")
    m2 = txns[txns['status']=='success'].merge(
        users[['user_id','age']], on='user_id')
    m2['age_group'] = pd.cut(m2['age'], bins=[12,15,18,21,25],
                              labels=['13-15','16-18','19-21','22-25'])
    cage = m2.groupby(['age_group','category'],
                      observed=True)['txn_id'].count().unstack().fillna(0)
 
    fig5, ax5 = plt.subplots(figsize=(5.5, 3))
    cage.plot(kind='bar', ax=ax5, colormap='tab10',
              edgecolor='white', width=0.65)
    ax5.set_ylabel('Transactions', fontsize=8)
    ax5.set_xlabel('Age Group', fontsize=8)
    ax5.tick_params(axis='x', labelsize=8, rotation=0)
    ax5.tick_params(axis='y', labelsize=8)
    plt.legend(title='Category', fontsize=7, title_fontsize=7,
               bbox_to_anchor=(1.01,1))
    plt.tight_layout()
    st.pyplot(fig5, use_container_width=False)
 
st.divider()

# --- A/B TEST ---
st.subheader("🧪 A/B Test Design: KYC Completion Nudge")
st.markdown("""
**Problem:** 25% of users drop off at KYC → Card Activation stage.

**Hypothesis:** Adding a progress bar + ₹50 cashback reward during 
KYC will increase completion rate by 10%+.

| | Control Group | Treatment Group |
|---|---|---|
| **Experience** | Current KYC flow | KYC with progress bar + ₹50 cashback |
| **Users** | 1,000 new signups | 1,000 new signups |
| **Duration** | 14 days | 14 days |
| **Primary Metric** | KYC completion rate | KYC completion rate |
| **Significance** | 95% confidence | 95% confidence |

**Decision rule:** If completion rate improves ≥10% with p < 0.05 → ship to 100% users.
""")

st.divider()
st.caption("Built by Sunidhi Choudhary | M.Tech CS, IIIT Guwahati")

