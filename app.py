import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from scipy import stats
from PIL import Image

st.set_page_config(layout="wide")


# --- Pengaturan Halaman ---
with st.container():
    col1, col2, col3, col4, col5, col6 = st.columns([0.15, 0.14, 0.15, 0.1, 0.2, 2])

    with col5:
        try:
            image_advancing = Image.open("advancing_bg.png")
            st.image(image_advancing, width=300)
        except FileNotFoundError:
            st.warning("File gambar 'advancing.png' tidak ditemukan.")

    with col4:
        try:
            image_stats = Image.open("stat_bg.png")
            st.image(image_stats, width=300)
        except FileNotFoundError:
            st.warning("File gambar 'stat_bg.png' tidak ditemukan.")

    with col3:
        try:
            image_asiin = Image.open("asiin_bg.png")
            st.image(image_asiin, width=300)
        except FileNotFoundError:
            st.warning("File gambar 'asiin_bg.png' tidak ditemukan.")

    with col2:
        try:
            image_zona = Image.open("zona.png")
            st.image(image_zona, width=300)
        except FileNotFoundError:
            st.warning("File gambar 'zona.png' tidak ditemukan.")

    with col1:
        try:
            image_sig = Image.open("sig_bg.png")
            st.image(image_sig, width=300)
        except FileNotFoundError:
            st.warning("File gambar 'sig_bg.png' tidak ditemukan.")

st.title("Dashboard Analisis Reliabilitas Mesin")
st.markdown("### Kerja Praktik PT.Semen Indonesia (Persero) Tbk. Pabrik Tuban")
st.markdown("---")

# --- Inisialisasi Session State ---
if 'data_manual' not in st.session_state:
    st.session_state.data_manual = pd.DataFrame(columns=['komponen', 'waktu_kerusakan', 'waktu_sistem_berjalan_kembali', 'penyebab_kerusakan'])

# --- Tab untuk Input Data ---
tab1, tab2 = st.tabs(["Unggah File", "Input Manual"])

with tab1:
    st.header("Input: Unggah Data Kerusakan dari File")
    uploaded_file = st.file_uploader("Pilih file CSV atau Excel", type=["csv", "xlsx"])

with tab2:
    st.header("Input: Masukkan Data Kerusakan Secara Manual")
    with st.form(key='data_form'):
        col1, col2 = st.columns(2)
        with col1:
            komponen = st.text_input("Nama Komponen", placeholder="contoh: Sistem, Komponen A")
        with col2:
            waktu_kerusakan = st.date_input("Tanggal Kerusakan")
            waktu_jam_kerusakan = st.time_input("Waktu Kerusakan")
        
        col3, col4 = st.columns(2)
        with col3:
            waktu_berjalan_kembali = st.date_input("Tanggal Sistem Berjalan Kembali", help="Diinput setelah perbaikan selesai.")
        with col4:
            waktu_jam_berjalan_kembali = st.time_input("Waktu Sistem Berjalan Kembali")
        
        penyebab = st.text_area("Penyebab Kerusakan", placeholder="contoh: Keausan, Overheating")
        
        submit_button = st.form_submit_button(label='Tambah Data')

    if submit_button and komponen and waktu_kerusakan and waktu_jam_kerusakan and waktu_berjalan_kembali and waktu_jam_berjalan_kembali:
        waktu_kerusakan_lengkap = datetime.combine(waktu_kerusakan, waktu_jam_kerusakan)
        waktu_berjalan_kembali_lengkap = datetime.combine(waktu_berjalan_kembali, waktu_jam_berjalan_kembali)
        
        new_data = {
            'komponen': komponen, 
            'waktu_kerusakan': waktu_kerusakan_lengkap, 
            'waktu_sistem_berjalan_kembali': waktu_berjalan_kembali_lengkap, 
            'penyebab_kerusakan': penyebab
        }
        
        temp_df = pd.DataFrame([new_data])
        st.session_state.data_manual = pd.concat([st.session_state.data_manual, temp_df], ignore_index=True)
        
        st.session_state.data_manual = st.session_state.data_manual.sort_values(
            by='waktu_kerusakan', 
            ignore_index=True
        )
        st.success("Data berhasil ditambahkan secara manual!")

# --- Pemilihan Sumber Data ---
st.markdown("---")
st.header("Tampilan Data")
df_final = None
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        if 'waktu_kerusakan' not in df.columns and 'tanggal_kerusakan' in df.columns:
            df['waktu_kerusakan'] = pd.to_datetime(df['tanggal_kerusakan'].astype(str) + ' ' + df['jam_kerusakan'].astype(str), errors='coerce')
            df['waktu_sistem_berjalan_kembali'] = pd.to_datetime(df['tanggal_sistem_berjalan_kembali'].astype(str) + ' ' + df['jam_sistem_berjalan_kembali'].astype(str), errors='coerce')
            df = df.drop(columns=['tanggal_kerusakan', 'jam_kerusakan', 'tanggal_sistem_berjalan_kembali', 'jam_sistem_berjalan_kembali'], errors='ignore')
        elif 'waktu_kerusakan' in df.columns:
            df['waktu_kerusakan'] = pd.to_datetime(df['waktu_kerusakan'], errors='coerce')
            df['waktu_sistem_berjalan_kembali'] = pd.to_datetime(df['waktu_sistem_berjalan_kembali'], errors='coerce')
        else:
            st.error("Format kolom tidak dikenali. Pastikan memiliki kolom 'waktu_kerusakan' atau 'tanggal_kerusakan' dan 'jam_kerusakan'.")
            st.stop()
        
        df = df.dropna(subset=['waktu_kerusakan', 'waktu_sistem_berjalan_kembali'])
        df = df.sort_values(by='waktu_kerusakan', ignore_index=True)
        st.write("Data Berhasil Diunggah:")
        st.dataframe(df)
        df_final = df
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file. Pastikan format kolom sudah benar. Error: {e}")
        st.stop()
elif not st.session_state.data_manual.empty:
    st.write("Data Manual Saat Ini:")
    
    st.session_state.data_manual = st.session_state.data_manual.sort_values(
        by='waktu_kerusakan', 
        ignore_index=True
    )
    
    df_display = st.session_state.data_manual.copy()
    
    col_header_1, col_header_2, col_header_3, col_header_4, col_header_5, col_header_6 = st.columns([0.5, 2, 2, 2, 2, 1])
    col_header_1.write("**No**")
    col_header_2.write("**Komponen**")
    col_header_3.write("**Waktu Kerusakan**")
    col_header_4.write("**Waktu Berjalan Kembali**")
    col_header_5.write("**Penyebab**")
    col_header_6.write("**Aksi**")
    st.markdown("---")
    
    for i, row in df_display.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 2, 2, 2, 1])
        
        with col1:
            st.write(i+1)
        with col2:
            st.write(row['komponen'])
        with col3:
            st.write(row['waktu_kerusakan'].strftime("%Y-%m-%d %H:%M:%S"))
        with col4:
            st.write(row['waktu_sistem_berjalan_kembali'].strftime("%Y-%m-%d %H:%M:%S"))
        with col5:
            st.write(row['penyebab_kerusakan'])
        with col6:
            if st.button("Hapus", key=f"delete_btn_{i}"):
                st.session_state.data_manual.drop(i, inplace=True)
                st.session_state.data_manual.reset_index(drop=True, inplace=True)
                st.rerun()
    
    df_final = st.session_state.data_manual.copy()
    if df_final.empty:
        st.info("Belum ada data yang dimasukkan.")
else:
    st.info("Silakan unggah atau input data untuk melihat tampilan data.")
    df_final = None

# --- Bagian Analisis Reliabilitas (Template Tampilan Hasil) ---
st.markdown("---")
st.header("Hasil: Analisis Reliabilitas")


if df_final is not None and len(df_final) > 1:
    
    def calculate_reliability_metrics(data, component_name, dist_name):
        data = data.sort_values(by='waktu_kerusakan', ignore_index=True)
        data['uptime'] = (data['waktu_kerusakan'] - data['waktu_sistem_berjalan_kembali'].shift(1)).dt.total_seconds() / (60*60)
        tbf_data = data['uptime'].dropna().loc[data['uptime'] > 0]

        if tbf_data.empty or len(tbf_data) < 2:
            return None, None, None, None, None, None
        
        mtbf = tbf_data.mean()
        max_tbf = tbf_data.max()
        
        if dist_name == 'Lognormal':
            params = stats.lognorm.fit(tbf_data, floc=0)
            dist = stats.lognorm(*params)
        elif dist_name == 'Gamma':
            params = stats.gamma.fit(tbf_data, floc=0)
            dist = stats.gamma(*params)
        elif dist_name == 'Lognormal 3P':
            params = stats.lognorm.fit(tbf_data)
            dist = stats.lognorm(*params)
        elif dist_name == 'Normal':
            params = stats.norm.fit(tbf_data)
            dist = stats.norm(*params)
        elif dist_name == 'Eksponensial':
            params = stats.expon.fit(tbf_data, floc=0)
            dist = stats.expon(*params)
        
        t_values = np.linspace(0, max_tbf * 1.5, 100)
        reliability_values = 1 - dist.cdf(t_values)
        
        maintenance_times = {}
        for level in [0.9, 0.8, 0.7, 0.6]:
            try:
                time_needed = dist.ppf(1 - level)
                maintenance_times[int(level*100)] = time_needed if time_needed > 0 else 0
            except ValueError:
                maintenance_times[int(level*100)] = np.nan
        
        current_reliability = dist.sf(max_tbf)
        
        reliability_df = pd.DataFrame({
            'Waktu (Jam)': t_values,
            'Reliabilitas': reliability_values
        })
        return mtbf, reliability_df, maintenance_times, dist, current_reliability, tbf_data.to_frame(name='Uptime (Jam)')

    def find_best_distribution(data):
        dist_names = ['Lognormal', 'Gamma', 'Eksponensial', 'Normal']
        best_dist = None
        best_aic = np.inf
        
        for name in dist_names:
            if name == 'Lognormal':
                params = stats.lognorm.fit(data, floc=0)
                dist = stats.lognorm(*params)
            elif name == 'Gamma':
                params = stats.gamma.fit(data, floc=0)
                dist = stats.gamma(*params)
            elif name == 'Normal':
                params = stats.norm.fit(data)
                dist = stats.norm(*params)
            elif name == 'Eksponensial':
                params = stats.expon.fit(data, floc=0)
                dist = stats.expon(*params)
            
            try:
                loglik = np.sum(np.log(dist.pdf(data[data > 0])))
                k = len(params)
                aic = 2*k - 2*loglik
                if aic < best_aic:
                    best_aic = aic
                    best_dist = name
            except Exception:
                continue
        
        return best_dist, best_aic

    components = ['Sistem Keseluruhan'] + list(df_final['komponen'].unique())
    selected_component = st.selectbox("Pilih Komponen:", components)

    st.subheader(f"Hasil Analisis untuk: {selected_component}")
    if selected_component == 'Sistem Keseluruhan':
        data_to_analyze = df_final
    else:
        data_to_analyze = df_final[df_final['komponen'] == selected_component]
    
    if len(data_to_analyze) > 2:
        tbf_data = (data_to_analyze['waktu_kerusakan'] - data_to_analyze['waktu_sistem_berjalan_kembali'].shift(1)).dt.total_seconds() / (60*60)
        tbf_data = tbf_data.dropna().loc[tbf_data > 0]

        best_dist_name, best_aic_value = find_best_distribution(tbf_data)
        if best_dist_name:
            st.info(f"Distribusi yang paling cocok adalah: **{best_dist_name}** (AIC: {best_aic_value:.2f})")
            selected_dist = st.selectbox(
                "Atau, pilih distribusi lain:",
                options=['Eksponensial', 'Normal', 'Lognormal', 'Gamma', 'Lognormal 3P'],
                index=['Eksponensial', 'Normal', 'Lognormal', 'Gamma', 'Lognormal 3P'].index(best_dist_name)
            )
        else:
            st.warning("Tidak dapat menemukan distribusi yang cocok. Silakan pilih secara manual.")
            selected_dist = st.selectbox(
                "Pilih distribusi untuk analisis:",
                options=['Eksponensial', 'Normal', 'Lognormal', 'Gamma', 'Lognormal 3P']
            )

        mtbf, reliability_df, maintenance_times, dist, current_reliability, uptime_df = calculate_reliability_metrics(data_to_analyze, selected_component, selected_dist)

        if mtbf is not None:
            col_mtbf, col_rel = st.columns(2)
            with col_mtbf:
                st.subheader("MTBF")
                st.metric(label=f"MTBF ({selected_dist})", value=f"{mtbf:.2f} Jam")
            with col_rel:
                st.subheader("Reliability Sekarang")
                st.metric(label=f"Pada Waktu Maks. Uptime", value=f"{current_reliability*100:.2f}%")

            st.subheader("Waktu Sistem Berjalan (Uptime) antar Kegagalan")
            st.dataframe(uptime_df)

            st.subheader("Grafik Fungsi Reliabilitas")
            st.write(f"Grafik ini berdasarkan asumsi distribusi: **{selected_dist}**")
            fig = px.line(reliability_df, x='Waktu (Jam)', y='Reliabilitas',
                          title=f'Fungsi Reliabilitas untuk {selected_component}')
            fig.add_scatter(x=[tbf_data.max()], y=[current_reliability], mode='markers', name='Reliability Sekarang',
                            marker=dict(color='red', size=10))
            st.plotly_chart(fig)

            st.subheader("Saran Waktu Maintenance")
            maintenance_table = pd.DataFrame(maintenance_times.items(), columns=['Target Reliabilitas (%)', 'Waktu Maintenance (Jam)'])
            st.dataframe(maintenance_table)
        else:
            st.info("Diperlukan minimal 3 kejadian kerusakan untuk melakukan analisis. Silakan masukkan data lebih lanjut.")
    else:
        st.info("Diperlukan minimal 3 kejadian kerusakan untuk melakukan analisis distribusi.")
else:
    # Konten hasil analisis yang akan terlihat jika data belum diunggah
    st.subheader("MTBF (Mean Time Between Failures)")
    st.write("Rata-rata waktu berjalannya mesin antar kegagalan.")
    st.markdown("---")
    st.subheader("Reliability Sekarang")
    st.write("Probabilitas bahwa mesin akan beroperasi tanpa gagal pada waktu saat ini.")
    st.markdown("---")
    st.subheader("Grafik  Fungsi Reliabilitas")
    st.write("Grafik yang menunjukkan probabilitas keberhasilan mesin seiring berjalannya waktu.")
    st.markdown("---")
    st.subheader("Saran Waktu Maintenance")
    st.write("Tabel yang berisi rekomendasi jadwal pemeliharaan berdasarkan target reliabilitas.")