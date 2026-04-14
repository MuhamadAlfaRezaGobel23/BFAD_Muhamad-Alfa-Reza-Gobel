import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

st.title("Dashboard Belajar Fundamental Analisis Data")

st.markdown("""
Dashboard ini merupakan hasil analisis data dari kelas **Fundamental Analisis Data**
menggunakan **Bike Sharing Dataset**.

### Pertanyaan Analisis:
- **Pertanyaan 1:**  
  Kapan waktu dengan jumlah penyewaan sepeda (cnt) tertinggi berdasarkan jam (hr), sehingga dapat digunakan untuk mengoptimalkan distribusi dan ketersediaan sepeda?

- **Pertanyaan 2:**  
  Bagaimana kondisi cuaca (weathersit) mempengaruhi jumlah penyewaan sepeda (cnt) pada berbagai jam?
""")

# LOAD DATA
data = pd.read_csv("main_data.csv")

if "instant" in data.columns:
    data = data.drop(columns=["instant"])

data["day_type"] = data["weekday"].apply(lambda x: "Weekend" if x in [0, 6] else "Weekday")

# SIDEBAR FILTER (DIGABUNG)
st.sidebar.header("Filter Data")

selected_day_type = st.sidebar.multiselect(
    "Pilih Tipe Hari (Pertanyaan 1)",
    options=["Weekday", "Weekend"],
    default=["Weekday", "Weekend"]
)

selected_weather = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca (Pertanyaan 2 & Analisis Lanjutan)",
    options=data["weathersit"].dropna().unique(),
    default=data["weathersit"].dropna().unique()
)

# OVERVIEW
st.header("Overview Data")

col1, col2, col3 = st.columns(3)

col1.metric("Total Data", data.shape[0])
col2.metric("Rata-rata Penyewaan", f"{int(data['cnt'].mean())} unit")
col3.metric("Maksimum Penyewaan", f"{int(data['cnt'].max())} unit")

# PERTANYAAN 1
st.header("Pertanyaan 1: Top 10 Jam Penyewaan")

data_q1 = data[data["day_type"].isin(selected_day_type)]

jam_agg = data_q1.groupby("hr")["cnt"].mean().reset_index()
top10 = jam_agg.sort_values("cnt", ascending=False).head(10)
top10 = top10.sort_values("cnt", ascending=False)

top10["hr"] = top10["hr"].apply(lambda x: f"{int(x):02d}.00")

colors = ["red" if i == 0 else "blue" if i in [1,2] else "lightblue" for i in range(len(top10))]

fig, ax = plt.subplots(figsize=(10,6))

sns.barplot(
    data=top10,
    x="cnt",
    y="hr",
    palette=colors,
    ax=ax
)

ax.set_title("Top 10 Jam dengan Penyewaan Sepeda Tertinggi")
ax.set_xlabel("Rata-rata Penyewaan")
ax.set_ylabel("Jam")

plt.tight_layout()
st.pyplot(fig)

# INSIGHT PERTANYAAN 1 (TIDAK DIUBAH SAMA SEKALI)
st.subheader("Insight Pertanyaan 1")

st.markdown("""
<div style="text-align: justify; background-color: white; padding: 15px; border-radius: 10px;">

Berdasarkan hasil visualisasi tersebut, terlihat bahwa waktu dengan jumlah penyewaan sepeda tertinggi terjadi pada pukul 17.00 sebagai puncak utama, diikuti oleh pukul 18.00 dan 08.00, serta didukung oleh jam 16.00 dan 19.00 sebagai periode dengan permintaan tinggi. Hal ini menunjukkan bahwa penggunaan sepeda sangat terkonsentrasi pada waktu sore hari dan pagi hari.

Kondisi ini mengindikasikan bahwa sepeda paling banyak digunakan pada saat jam pulang kerja dan berangkat kerja (commuting). Oleh karena itu, periode antara pukul 16.00–19.00 dan sekitar pukul 08.00 merupakan waktu kritis dengan permintaan tertinggi yang perlu menjadi fokus utama dalam pengelolaan dan distribusi ketersediaan sepeda.

</div>
""", unsafe_allow_html=True)

# PERTANYAAN 2 (VISUALISASI 1)
st.header("Pertanyaan 2: Pola Penyewaan Berdasarkan Cuaca & Jam")

data_q2 = data[data["weathersit"].isin(selected_weather)]

pivot_weather = data_q2.pivot_table(
    values="cnt",
    index="hr",
    columns="weathersit",
    aggfunc="mean"
).reset_index()

pivot_weather = pivot_weather.melt(
    id_vars="hr",
    var_name="weathersit",
    value_name="cnt"
)

pivot_weather["hr"] = pivot_weather["hr"].apply(lambda x: f"{int(x):02d}.00")

pivot_weather["hr"] = pd.Categorical(
    pivot_weather["hr"],
    categories=[f"{i:02d}.00" for i in range(24)],
    ordered=True
)

fig, ax = plt.subplots(figsize=(12,6))

sns.lineplot(
    data=pivot_weather,
    x="hr",
    y="cnt",
    hue="weathersit",
    errorbar=None,
    ax=ax
)

ax.set_title("Pola Penyewaan Berdasarkan Jam dan Kondisi Cuaca")
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Penyewaan")

plt.xticks(rotation=45)
ax.legend(title="Cuaca", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
st.pyplot(fig)

# INSIGHT PERTANYAAN 2 (TIDAK DIUBAH)
st.subheader("Insight Pertanyaan 2")

st.markdown("""
<div style="text-align: justify; background-color: white; padding: 15px; border-radius: 10px;">

Kondisi cuaca memiliki pengaruh yang signifikan terhadap jumlah penyewaan sepeda, di mana cuaca cerah menghasilkan jumlah penyewaan tertinggi di hampir semua jam, diikuti oleh cuaca berawan dengan pola yang mirip namun sedikit lebih rendah. Sebaliknya, hujan atau salju ringan hingga lebat menyebabkan penurunan drastis, bahkan pada cuaca ekstrem jumlah penyewaan cenderung sangat rendah sepanjang hari. Meskipun demikian, pola jam sibuk seperti pagi (08.00) dan sore (17.00–18.00) tetap muncul pada semua kondisi cuaca, menunjukkan bahwa cuaca tidak mengubah waktu puncak penggunaan, tetapi hanya memengaruhi besarnya volume penyewaan.
""", unsafe_allow_html=True)

# ANALISIS LANJUTAN (IPYNB VERSION)
st.header("Analisis Lanjutan: Rata-rata Penyewaan Berdasarkan Cluster Waktu")

cluster_order = [
    "Pagi (06.00-09.00)",
    "Siang (10.00-15.00)",
    "Sore (16.00-19.00)",
    "Malam (20.00-05.00)"
]

fig, ax = plt.subplots(figsize=(8,5))

sns.barplot(
    data=data_q2,
    x="cluster_waktu",
    y="cnt",
    estimator="mean",
    order=cluster_order,
    ax=ax
)

ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Waktu")
ax.set_xlabel("Kategori Waktu")
ax.set_ylabel("Rata-rata Penyewaan")

plt.xticks(rotation=20)
plt.tight_layout()
st.pyplot(fig)

# SUMMARY (TIDAK DIKURANGI SAMA SEKALI)
st.header("Insight Summary")

st.info(
    """
    - Penyewaan sepeda paling tinggi terjadi pada jam sibuk sore (sekitar 16.00–19.00) dengan puncaknya pukul 17.00, diikuti oleh jam sibuk pagi (sekitar 08.00). Hal ini menunjukkan bahwa penggunaan sepeda didominasi oleh aktivitas komuter (berangkat dan pulang kerja/sekolah), sehingga waktu kritis permintaan terjadi pada dua periode utama tersebut.
    
    - Kondisi cuaca memiliki pengaruh yang signifikan terhadap jumlah penyewaan sepeda, di mana cuaca cerah menghasilkan jumlah penyewaan tertinggi, sedangkan cuaca buruk seperti hujan atau salju menyebabkan penurunan tajam. Namun, pada jam sibuk (pagi dan sore), penggunaan sepeda tetap terjadi meskipun cuaca kurang baik, yang menunjukkan bahwa faktor kebutuhan aktivitas rutin masih menjadi pendorong utama penggunaan.
    
    - Hasil clustering waktu menunjukkan bahwa secara keseluruhan Jam Sibuk Sore memiliki rata-rata penyewaan tertinggi, diikuti oleh Siang Hari yang cenderung stabil, sementara Malam Hari menjadi periode dengan permintaan terendah. Namun, jika dilihat berdasarkan kondisi cuaca, pola ini sedikit berubah karena pada cuaca tertentu seperti kondisi berawan, Jam Sibuk Pagi dapat meningkat dan bahkan melampaui Siang Hari, yang menunjukkan bahwa penggunaan sepeda pada pagi hari lebih sensitif terhadap cuaca dibandingkan waktu lainnya. Secara umum, hal ini menegaskan bahwa pola penyewaan sepeda tidak hanya dipengaruhi oleh waktu, tetapi juga sangat bergantung pada kondisi cuaca.
    """
)
