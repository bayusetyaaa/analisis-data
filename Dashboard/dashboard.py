import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st 
from babel.numbers import format_currency
import os

sns.set(style='dark')

all_df = pd.read_csv("Dashboard/all_data.csv")
all_df['dteday'] = pd.to_datetime(all_df['dteday'])

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    start_date, end_date = st.sidebar.date_input(
        label='Pilih Rentang Waktu',
        min_value=all_df['dteday'].min().date(),
        max_value=all_df['dteday'].max().date(),
        value=[all_df['dteday'].min().date(), all_df['dteday'].max().date()]
    )


    hour_range = st.sidebar.slider(
        "Pilih Rentang Jam",
        min_value=0,
        max_value=23,
        value=(0, 23)
    )


    filtered_df = all_df[
        (all_df['dteday'] >= pd.to_datetime(start_date)) &
        (all_df['dteday'] <= pd.to_datetime(end_date)) &
        (all_df['hr'] >= hour_range[0]) &
        (all_df['hr'] <= hour_range[1])
    ]


st.title("Dashboard")
st.markdown("### Analisis Penggunaan Sepeda Berdasarkan Musim, Cuaca & Waktu")


total_rides = filtered_df['cnt_y'].sum()
avg_temp = round(filtered_df['temp_y'].mean() * 41, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Total Pengguna", value=f"{total_rides:,}")
col2.metric("Rata-rata Suhu (°C)", value=f"{avg_temp}°C")


busiest_hour = filtered_df.groupby('hr')['cnt_y'].mean().idxmax()
col3.metric("Jam Tersibuk", value=f"{busiest_hour}:00")


st.subheader("Tren Penggunaan Sepeda")

tab1, tab2 = st.tabs(["Tren Harian", "Tren Per Jam"])

with tab1:

    daily_data = filtered_df.groupby('dteday')['cnt_y'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=daily_data['dteday'], y=daily_data['cnt_y'], marker='o', color='#007BFF')
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Jumlah Pengguna")
    ax.set_title("Tren Jumlah Pengguna Sepeda Harian")
    st.pyplot(fig)

with tab2:

    hourly_data = filtered_df.groupby('hr')['cnt_y'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=hourly_data['hr'], y=hourly_data['cnt_y'], marker='o', color='#FF5733')
    ax.set_xlabel("Jam")
    ax.set_ylabel("Rata-rata Pengguna")
    ax.set_title("Rata-rata Penggunaan Sepeda per Jam")
    ax.set_xticks(range(0, 24))
    st.pyplot(fig)

st.subheader("Pengguna Casual vs Registered")
fig, ax = plt.subplots(figsize=(10, 5))
casual_sum = filtered_df['casual_y'].sum()
registered_sum = filtered_df['registered_y'].sum()
labels = ['Casual', 'Registered']
values = [casual_sum, registered_sum]
colors = ['#FF6F61', '#6B5B95']
ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, wedgeprops={'edgecolor': 'black'})
ax.set_title("Distribusi Pengguna Sepeda")
st.pyplot(fig)



st.subheader("Analisis Pertanyaan Bisnis")
st.markdown("#### performa penyewaan dalam beberapa bulan terakhir")

latest_year = all_df["dteday"].dt.year.max()
filtered_df = all_df[all_df["dteday"].dt.year == latest_year]

monthly_df = filtered_df.resample(rule='ME', on='dteday').agg({
    "instant_y": "nunique",
    "cnt_x": "sum"
})
month_labels = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
}

monthly_df.index = monthly_df.index.strftime('%B')
monthly_df = monthly_df.reset_index()
monthly_df.rename(
    columns={"dteday": "bulan"},
    inplace=True)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    monthly_df["bulan"],
    monthly_df["cnt_x"],
    marker='o',
    linewidth=3,
    color='#72BCD9'
)
ax.set_title("Penyewaan Beberapa bulan terakhir", loc="center", fontsize=20)
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(fig)


st.markdown("#### Pengaruh musim cuaca terhadap jumlah peminjam sepeda")

# Kelompokkan data berdasarkan musim
all_df["dteday"] = pd.to_datetime(all_df["dteday"])
all_df["temp_celsius"] = all_df["temp_y"] * 41
all_df["humidity_percent"] = all_df["hum_y"] * 100
all_df["windspeed_kmh"] = all_df["windspeed_y"] * 67

# Kelompokkan data berdasarkan musim
season_names = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}
filtered_df['season_name'] = filtered_df['season_y'].map(season_names)

# Buat subplots 2x2
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Barplot Musim
sns.barplot(
    y="cnt_y",
    x="season_name",
    data=filtered_df,
    palette="viridis",
    hue="season_y",
    ax=axes[0, 0]
)
axes[0, 0].set_title("Berdasarkan Musim", fontsize=12)
axes[0, 0].set_xlabel(None)
axes[0, 0].set_ylabel(None)

# Scatter plot Suhu
sns.scatterplot(x=all_df["temp_celsius"], y=all_df["cnt_y"], alpha=0.5, color="blue", ax=axes[0, 1])
axes[0, 1].set_title("Berdasarkan Suhu", fontsize=12)
axes[0, 1].set_xlabel("Suhu (°C)")
axes[0, 1].set_ylabel("Jumlah Penyewa")
axes[0, 1].grid(True)

# Scatter plot Kelembapan
sns.scatterplot(x=all_df["humidity_percent"], y=all_df["cnt_y"], alpha=0.5, color="red", ax=axes[1, 0])
axes[1, 0].set_title("Berdasarkan Kelembapan", fontsize=12)
axes[1, 0].set_xlabel("Kelembapan (%)")
axes[1, 0].set_ylabel("Jumlah Penyewa")
axes[1, 0].grid(True)

# Scatter plot Kecepatan Angin
sns.scatterplot(x=all_df["windspeed_kmh"], y=all_df["cnt_y"], alpha=0.5, color="green", ax=axes[1, 1])
axes[1, 1].set_title("Berdasarkan Kecepatan Angin", fontsize=12)
axes[1, 1].set_xlabel("Kecepatan Angin (km/jam)")
axes[1, 1].set_ylabel("Jumlah Penyewa")
axes[1, 1].grid(True)
st.pyplot(fig)

st.subheader("🕒 Analisis Berdasarkan Hari dan Jam")


day_names = {0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 4: "Kamis", 5: "Jumat", 6: "Sabtu"}
filtered_df['day_name'] = filtered_df['weekday_y'].map(day_names)


heatmap_data = filtered_df.pivot_table(
    index='hr',
    columns='day_name',
    values='cnt_y',
    aggfunc='mean'
)

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap="YlGnBu", annot=False, fmt=".0f", ax=ax)
ax.set_title("Pola Penggunaan Sepeda Berdasarkan Hari dan Jam")
ax.set_xlabel("Hari")
ax.set_ylabel("Jam")
st.pyplot(fig)

st.caption("🚀 Dashboard dibuat dengan Streamlit")
