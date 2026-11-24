import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Kemiskinan Indonesia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5f8a 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 20px rgba(30, 58, 95, 0.3);
    }
    .main-header h1 { margin: 0; font-weight: 700; font-size: 2.2rem; }
    .main-header p { margin: 0.5rem 0 0; opacity: 0.9; font-size: 1.1rem; }
    
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e8eef4;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.1); }
    .kpi-label { font-size: 0.85rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #1e3a5f; line-height: 1.2; }
    .kpi-delta { font-size: 0.8rem; font-weight: 500; margin-top: 0.5rem; }
    .kpi-positive { color: #059669; }
    .kpi-negative { color: #dc2626; }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e3a5f;
        margin: 2rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e8eef4;
    }
    
    .metric-row { display: flex; gap: 1rem; flex-wrap: wrap; }
    .metric-col { flex: 1; min-width: 200px; }
    
    .insight-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 4px solid #0284c7;
        padding: 1rem 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
    }
    .insight-title { font-weight: 600; color: #0369a1; margin-bottom: 0.5rem; }
    
    .dataframe-container { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        background: #f8fafc;
        border-radius: 8px;
        font-weight: 500;
        color: #475569;
        border: 1px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] {
        background: #1e3a5f;
        color: white;
        border-color: #1e3a5f;
    }
    
    .sidebar-content { padding: 1rem 0; }
    .filter-section { margin-bottom: 1.5rem; }
    .filter-label { font-weight: 600; color: #334155; margin-bottom: 0.5rem; display: block; }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5f8a 100%);
        color: white;
        border: none;
        font-weight: 500;
    }
    .stDownloadButton > button:hover { box-shadow: 0 4px 16px rgba(30, 58, 95, 0.4); }
    
    .footer { text-align: center; color: #94a3b8; padding: 2rem; font-size: 0.85rem; }
</style>
"""

@st.cache_data
def load_data():
    df = pd.read_csv(
        'Klasifikasi Tingkat Kemiskinan di Indonesia - Copy.csv',
        sep=';',
        encoding='utf-8'
    )
    df = df.dropna(subset=['Provinsi'])
    df = df[df['Provinsi'].str.strip() != '']
    
    numeric_cols = [
        'Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)',
        'Rata-rata Lama Sekolah Penduduk 15+ (Tahun)',
        'Indeks Pembangunan Manusia',
        'Umur Harapan Hidup (Tahun)',
        'Persentase rumah tangga yang memiliki akses terhadap sanitasi layak',
        'Persentase rumah tangga yang memiliki akses terhadap air minum layak',
        'Tingkat Pengangguran Terbuka',
        'Tingkat Partisipasi Angkatan Kerja'
    ]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '.'), errors='coerce')
    
    df['Klasifikasi Kemiskinan'] = df['Klasifikasi Kemiskinan'].astype(int)
    df['Klasifikasi Label'] = df['Klasifikasi Kemiskinan'].map({0: 'Non-Miskin', 1: 'Miskin'})
    
    return df

def format_number(val, prefix="", suffix=""):
    if pd.isna(val):
        return "N/A"
    if val >= 1e9:
        return f"{prefix}{val/1e9:.2f}B{suffix}"
    elif val >= 1e6:
        return f"{prefix}{val/1e6:.2f}M{suffix}"
    elif val >= 1e3:
        return f"{prefix}{val/1e3:.1f}K{suffix}"
    return f"{prefix}{val:,.0f}{suffix}"

def create_kpi_card(label, value, delta=None, delta_label=""):
    delta_html = ""
    if delta is not None:
        cls = "kpi-positive" if delta >= 0 else "kpi-negative"
        sign = "+" if delta >= 0 else ""
        delta_html = f'<div class="kpi-delta {cls}">{sign}{delta:.1f}% {delta_label}</div>'
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    df = load_data()
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard Klasifikasi Tingkat Kemiskinan Indonesia</h1>
        <p>Analisis Komprehensif Indikator Kemiskinan & Pembangunan Manusia per Kabupaten/Kota (514 Wilayah)</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("### 🎛️ Filter & Kontrol")
        
        provinsi_options = ['Semua'] + sorted(df['Provinsi'].unique().tolist())
        selected_provinsi = st.selectbox("📍 Provinsi", provinsi_options, key="filter_prov")
        
        if selected_provinsi != 'Semua':
            kab_options = ['Semua'] + sorted(df[df['Provinsi'] == selected_provinsi]['Kab/Kota'].unique().tolist())
            selected_kab = st.selectbox("🏙️ Kabupaten/Kota", kab_options, key="filter_kab")
        else:
            selected_kab = 'Semua'
        
        klasifikasi_options = ['Semua', 'Miskin (1)', 'Non-Miskin (0)']
        selected_klasifikasi = st.selectbox("🏷️ Klasifikasi Kemiskinan", klasifikasi_options, key="filter_klas")
        
        p0_range = st.slider(
            "📊 Rentang Persentase Penduduk Miskin (P0)",
            float(df['Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)'].min()),
            float(df['Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)'].max()),
            (float(df['Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)'].min()),
             float(df['Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)'].max())),
            key="filter_p0"
        )
        
        ipm_range = st.slider(
            "📈 Rentang Indeks Pembangunan Manusia (IPM)",
            float(df['Indeks Pembangunan Manusia'].min()),
            float(df['Indeks Pembangunan Manusia'].max()),
            (float(df['Indeks Pembangunan Manusia'].min()),
             float(df['Indeks Pembangunan Manusia'].max())),
            key="filter_ipm"
        )
        
        st.markdown("---")
        st.markdown("### 📥 Unduh Data")
        
        filtered_df = df.copy()
        if selected_provinsi != 'Semua':
            filtered_df = filtered_df[filtered_df['Provinsi'] == selected_provinsi]
        if selected_kab != 'Semua':
            filtered_df = filtered_df[filtered_df['Kab/Kota'] == selected_kab]
        if selected_klasifikasi == 'Miskin (1)':
            filtered_df = filtered_df[filtered_df['Klasifikasi Kemiskinan'] == 1]
        elif selected_klasifikasi == 'Non-Miskin (0)':
            filtered_df = filtered_df[filtered_df['Klasifikasi Kemiskinan'] == 0]
        filtered_df = filtered_df[
            (filtered_df['Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)'] >= p0_range[0]) &
            (filtered_df['Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)'] <= p0_range[1]) &
            (filtered_df['Indeks Pembangunan Manusia'] >= ipm_range[0]) &
            (filtered_df['Indeks Pembangunan Manusia'] <= ipm_range[1])
        ]
        
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📄 Download CSV",
            csv,
            f"kemiskinan_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            use_container_width=True
        )
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Data Kemiskinan')
        st.download_button(
            "📊 Download Excel",
            excel_buffer.getvalue(),
            f"kemiskinan_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Overview & KPI",
        "🗺️ Analisis Wilayah",
        "📊 Distribusi & Statistik",
        "🔗 Korelasi & Heatmap",
        "🏆 Ranking Top/Bottom",
        "🔍 Eksplorasi Data",
        "💡 Smart Insights"
    ])
    
    with tab1:
        st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
        
        # Column name mapping for robustness
        COL_MAP = {
            'P0': 'Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)',
            'LamaSekolah': 'Rata-rata Lama Sekolah Penduduk 15+ (Tahun)',
            'Pengeluaran': 'Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)',
            'IPM': 'Indeks Pembangunan Manusia',
            'UmurHarapan': 'Umur Harapan Hidup (Tahun)',
            'Sanitasi': 'Persentase rumah tangga yang memiliki akses terhadap sanitasi layak',
            'AirMinum': 'Persentase rumah tangga yang memiliki akses terhadap air minum layak',
            'Pengangguran': 'Tingkat Pengangguran Terbuka',
            'Partisipasi': 'Tingkat Partisipasi Angkatan Kerja',
            'PDRB': 'PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)',
            'Klasifikasi': 'Klasifikasi Kemiskinan',
        }
        
        # Helper to safely get column
        def col(key):
            return COL_MAP.get(key, key)
        
        # Prov stats column mapping (shortened names used in groupby agg)
        PROV_STATS_MAP = {
            'P0': 'Rata_P0',
            'IPM': 'Rata_IPM',
            'Pengeluaran': 'Rata_Pengeluaran',
            'UmurHarapan': 'Rata_UmurHarapan',
            'Pengangguran': 'Rata_Pengangguran',
            'Partisipasi': 'Rata_Partisipasi',
            'Sanitasi': 'Rata_Sanitasi',
            'AirMinum': 'Rata_AirMinum',
            'LamaSekolah': 'Rata_LamaSekolah',
            'PDRB': 'Total_PDRB',
            'PctMiskin': 'Pct_Miskin',
        }
        
        def pcol(key):
            return PROV_STATS_MAP.get(key, key)
        
        # Numeric indicators using mapped names
        numeric_keys = ['P0', 'LamaSekolah', 'Pengeluaran', 'IPM', 'UmurHarapan', 
                        'Sanitasi', 'AirMinum', 'Pengangguran', 'Partisipasi', 'PDRB']
        numeric_indicators = [col(k) for k in numeric_keys]
        
        total_wilayah = len(filtered_df)
        avg_p0 = filtered_df[col('P0')].mean()
        avg_ipm = filtered_df[col('IPM')].mean()
        avg_pengeluaran = filtered_df[col('Pengeluaran')].mean()
        avg_umur_harapan = filtered_df[col('UmurHarapan')].mean()
        pct_miskin = (filtered_df[col('Klasifikasi')].sum() / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        avg_pengangguran = filtered_df[col('Pengangguran')].mean()
        avg_partisipasi = filtered_df[col('Partisipasi')].mean()
        avg_sanitasi = filtered_df[col('Sanitasi')].mean()
        avg_air_minum = filtered_df[col('AirMinum')].mean()
        avg_lama_sekolah = filtered_df[col('LamaSekolah')].mean()
        total_pdrb = filtered_df[col('PDRB')].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_kpi_card("Total Wilayah", f"{total_wilayah:,}"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Rata-rata P0 (Kemiskinan)", f"{avg_p0:.2f}%"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_kpi_card("Rata-rata IPM", f"{avg_ipm:.2f}"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_kpi_card("% Wilayah Miskin", f"{pct_miskin:.1f}%"), unsafe_allow_html=True)
        
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.markdown(create_kpi_card("Rata-rata Pengeluaran/Th", f"Rp {avg_pengeluaran:,.0f}K"), unsafe_allow_html=True)
        with col6:
            st.markdown(create_kpi_card("Rata-rata Umur Harapan", f"{avg_umur_harapan:.1f} Th"), unsafe_allow_html=True)
        with col7:
            st.markdown(create_kpi_card("Rata-rata Pengangguran", f"{avg_pengangguran:.2f}%"), unsafe_allow_html=True)
        with col8:
            st.markdown(create_kpi_card("Total PDRB", format_number(total_pdrb, "Rp ")), unsafe_allow_html=True)
        
        col9, col10, col11, col12 = st.columns(4)
        with col9:
            st.markdown(create_kpi_card("Partisipasi Angkatan Kerja", f"{avg_partisipasi:.1f}%"), unsafe_allow_html=True)
        with col10:
            st.markdown(create_kpi_card("Akses Sanitasi Layak", f"{avg_sanitasi:.1f}%"), unsafe_allow_html=True)
        with col11:
            st.markdown(create_kpi_card("Akses Air Minum Layak", f"{avg_air_minum:.1f}%"), unsafe_allow_html=True)
        with col12:
            st.markdown(create_kpi_card("Rata-rata Lama Sekolah", f"{avg_lama_sekolah:.1f} Th"), unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">📈 Distribusi Kelas Kemiskinan</div>', unsafe_allow_html=True)
        klas_counts = filtered_df['Klasifikasi Label'].value_counts().reset_index()
        klas_counts.columns = ['Klasifikasi', 'Jumlah']
        fig_pie = px.pie(
            klas_counts, values='Jumlah', names='Klasifikasi',
            color='Klasifikasi',
            color_discrete_map={'Miskin': '#dc2626', 'Non-Miskin': '#059669'},
            hole=0.45
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
        fig_pie.update_layout(height=350, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown('<div class="section-header">📦 Box Plot: P0 per Provinsi</div>', unsafe_allow_html=True)
        prov_order = filtered_df.groupby('Provinsi')[col('P0')].median().sort_values(ascending=False).index
        fig_box = px.box(
            filtered_df, x='Provinsi', y=col('P0'),
            color='Klasifikasi Label',
            color_discrete_map={'Miskin': '#dc2626', 'Non-Miskin': '#059669'},
            category_orders={'Provinsi': list(prov_order)},
            points='outliers'
        )
        fig_box.update_layout(height=500, xaxis_tickangle=-45, xaxis_title="", yaxis_title="P0 (%)")
        st.plotly_chart(fig_box, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-header">🗺️ Perbandingan Antar Provinsi</div>', unsafe_allow_html=True)
        
        prov_stats = filtered_df.groupby('Provinsi').agg(
            Rata_P0=(col('P0'), 'mean'),
            Rata_IPM=(col('IPM'), 'mean'),
            Rata_Pengeluaran=(col('Pengeluaran'), 'mean'),
            Rata_UmurHarapan=(col('UmurHarapan'), 'mean'),
            Rata_Pengangguran=(col('Pengangguran'), 'mean'),
            Rata_Partisipasi=(col('Partisipasi'), 'mean'),
            Rata_Sanitasi=(col('Sanitasi'), 'mean'),
            Rata_AirMinum=(col('AirMinum'), 'mean'),
            Rata_LamaSekolah=(col('LamaSekolah'), 'mean'),
            Total_PDRB=(col('PDRB'), 'sum'),
            Jumlah_Wilayah=('Kab/Kota', 'count'),
            Pct_Miskin=(col('Klasifikasi'), 'mean')
        ).reset_index()
        prov_stats['Pct_Miskin'] = prov_stats['Pct_Miskin'] * 100
        
        metric_option = st.selectbox(
            "Pilih Metrik untuk Perbandingan",
            [pcol('P0'), pcol('IPM'), pcol('Pengeluaran'), pcol('UmurHarapan'), 
             pcol('Pengangguran'), pcol('Partisipasi'), pcol('Sanitasi'), pcol('AirMinum'),
             pcol('LamaSekolah'), pcol('PDRB'), pcol('PctMiskin')],
            format_func=lambda x: {
                pcol('P0'): 'Rata-rata P0 (Kemiskinan %)',
                pcol('IPM'): 'Rata-rata IPM',
                pcol('Pengeluaran'): 'Rata-rata Pengeluaran per Kapita (Ribu Rupiah)',
                pcol('UmurHarapan'): 'Rata-rata Umur Harapan Hidup (Tahun)',
                pcol('Pengangguran'): 'Rata-rata Tingkat Pengangguran (%)',
                pcol('Partisipasi'): 'Rata-rata Partisipasi Angkatan Kerja (%)',
                pcol('Sanitasi'): 'Rata-rata Akses Sanitasi Layak (%)',
                pcol('AirMinum'): 'Rata-rata Akses Air Minum Layak (%)',
                pcol('LamaSekolah'): 'Rata-rata Lama Sekolah (Tahun)',
                pcol('PDRB'): 'Total PDRB (Rupiah)',
                pcol('PctMiskin'): 'Persentase Wilayah Miskin (%)'
            }[x]
        )
        
        ascending = metric_option in [pcol('P0'), pcol('Pengangguran'), pcol('PctMiskin')]
        prov_sorted = prov_stats.sort_values(metric_option, ascending=ascending)
        
        fig_bar = px.bar(
            prov_sorted, x=metric_option, y='Provinsi', orientation='h',
            color=metric_option,
            color_continuous_scale='RdYlGn_r' if ascending else 'RdYlGn',
            text=metric_option,
            hover_data=['Jumlah_Wilayah']
        )
        fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_bar.update_layout(height=700, yaxis={'categoryorder': 'total ascending'}, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown('<div class="section-header">📍 Scatter: P0 vs IPM per Provinsi</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            filtered_df, x=col('IPM'), 
            y=col('P0'),
            color='Provinsi', size=col('Pengeluaran'),
            hover_data=['Kab/Kota', 'Klasifikasi Label', col('UmurHarapan')],
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_scatter.update_layout(height=600)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.markdown('<div class="section-header">📋 Tabel Ringkasan per Provinsi</div>', unsafe_allow_html=True)
        display_cols = ['Provinsi', 'Jumlah_Wilayah', pcol('P0'), pcol('IPM'), pcol('Pengeluaran'), 
                        pcol('UmurHarapan'), pcol('Pengangguran'), pcol('Partisipasi'), 
                        pcol('Sanitasi'), pcol('AirMinum'), pcol('LamaSekolah'), pcol('PDRB'), pcol('PctMiskin')]
        st.dataframe(
            prov_stats[display_cols].style.format({
                pcol('P0'): '{:.2f}', pcol('IPM'): '{:.2f}', pcol('Pengeluaran'): '{:,.0f}',
                pcol('UmurHarapan'): '{:.1f}', pcol('Pengangguran'): '{:.2f}', pcol('Partisipasi'): '{:.1f}',
                pcol('Sanitasi'): '{:.1f}', pcol('AirMinum'): '{:.1f}', pcol('LamaSekolah'): '{:.1f}',
                pcol('PDRB'): lambda x: f'Rp {x:,.0f}', pcol('PctMiskin'): '{:.1f}%'
            }).background_gradient(subset=[pcol('P0')], cmap='RdYlGn_r')
            .background_gradient(subset=[pcol('IPM'), pcol('Pengeluaran'), pcol('UmurHarapan'), 
                                         pcol('Sanitasi'), pcol('AirMinum'), pcol('LamaSekolah')], cmap='RdYlGn'),
            use_container_width=True, height=500
        )
    
    with tab3:
        st.markdown('<div class="section-header">📊 Distribusi Indikator Utama</div>', unsafe_allow_html=True)
        
        hist_col_options = {col(k): col(k) for k in numeric_keys}
        hist_col = st.selectbox(
            "Pilih Indikator untuk Histogram",
            list(hist_col_options.values())
        )
        
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            fig_hist = px.histogram(
                filtered_df, x=hist_col, nbins=30, color='Klasifikasi Label',
                color_discrete_map={'Miskin': '#dc2626', 'Non-Miskin': '#059669'},
                marginal='box', opacity=0.7
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col_h2:
            fig_violin = px.violin(
                filtered_df, x='Klasifikasi Label', y=hist_col, color='Klasifikasi Label',
                color_discrete_map={'Miskin': '#dc2626', 'Non-Miskin': '#059669'},
                box=True, points='outliers'
            )
            fig_violin.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_violin, use_container_width=True)
        
        st.markdown('<div class="section-header">📈 Statistik Deskriptif</div>', unsafe_allow_html=True)
        
        # numeric_indicators already defined above using col() mapping
        
        desc_stats = filtered_df[numeric_indicators].describe().T
        desc_stats = desc_stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        desc_stats.columns = ['Count', 'Mean', 'Std', 'Min', 'Q1', 'Median', 'Q3', 'Max']
        
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            st.dataframe(
                desc_stats.style.format({
                    'Count': '{:.0f}', 'Mean': '{:.2f}', 'Std': '{:.2f}',
                    'Min': '{:.2f}', 'Q1': '{:.2f}', 'Median': '{:.2f}', 'Q3': '{:.2f}', 'Max': '{:.2f}'
                }).background_gradient(cmap='RdYlGn'),
                use_container_width=True
            )
        
        with col_s2:
            st.markdown("**Statistik per Kelas Kemiskinan**")
            for klas in [0, 1]:
                label = 'Non-Miskin' if klas == 0 else 'Miskin'
                sub = filtered_df[filtered_df['Klasifikasi Kemiskinan'] == klas]
                st.markdown(f"**{label} (n={len(sub)})**")
                mini_stats = sub[numeric_indicators].mean().to_frame('Mean').round(2)
                st.dataframe(mini_stats.style.background_gradient(cmap='RdYlGn'), use_container_width=True)
        
        st.markdown('<div class="section-header">🔄 Pairplot Indikator Kunci</div>', unsafe_allow_html=True)
        pair_cols = st.multiselect(
            "Pilih Indikator (max 5)",
            numeric_indicators,
            default=[col('P0'), col('IPM'), col('Pengeluaran'), col('UmurHarapan'), col('LamaSekolah')],
            max_selections=5
        )
        
        if len(pair_cols) >= 2:
            fig_pair = px.scatter_matrix(
                filtered_df, dimensions=pair_cols, color='Klasifikasi Label',
                color_discrete_map={'Miskin': '#dc2626', 'Non-Miskin': '#059669'},
                opacity=0.6
            )
            fig_pair.update_layout(height=700)
            st.plotly_chart(fig_pair, use_container_width=True)
    
    with tab4:
        st.markdown('<div class="section-header">🔗 Heatmap Korelasi Indikator</div>', unsafe_allow_html=True)
        
        corr_df = filtered_df[numeric_indicators].corr()
        
        fig_heat = px.imshow(
            corr_df,
            text_auto='.2f',
            aspect='auto',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1,
            labels=dict(x="", y="", color="Korelasi")
        )
        fig_heat.update_layout(height=700, xaxis_tickangle=-45)
        st.plotly_chart(fig_heat, use_container_width=True)
        
        st.markdown('<div class="section-header">📋 Matriks Korelasi Detail</div>', unsafe_allow_html=True)
        st.dataframe(
            corr_df.style.format('{:.3f}').background_gradient(cmap='RdBu_r', vmin=-1, vmax=1),
            use_container_width=True
        )
        
        st.markdown('<div class="section-header">🎯 Korelasi Terkuat dengan P0 (Kemiskinan)</div>', unsafe_allow_html=True)
        p0_col_name = col('P0')
        p0_corr = corr_df[p0_col_name].drop(p0_col_name).sort_values(key=abs, ascending=False)
        
        fig_corr_bar = px.bar(
            x=p0_corr.values, y=p0_corr.index, orientation='h',
            color=p0_corr.values, color_continuous_scale='RdBu_r',
            color_continuous_midpoint=0,
            labels={'x': 'Koefisien Korelasi', 'y': 'Indikator'}
        )
        fig_corr_bar.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_corr_bar, use_container_width=True)
    
    with tab5:
        st.markdown('<div class="section-header">🏆 Ranking Top & Bottom</div>', unsafe_allow_html=True)
        
        rank_col = st.selectbox(
            "Pilih Indikator untuk Ranking",
            numeric_indicators,
            format_func=lambda x: x
        )
        
        ascending = rank_col in [col('P0'), col('Pengangguran')]
        
        top_n = st.slider("Jumlah Top/Bottom", 5, 50, 15)
        
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            st.markdown(f"**Top {top_n} (Terbaik)**")
            top_df = filtered_df.nlargest(top_n, rank_col) if not ascending else filtered_df.nsmallest(top_n, rank_col)
            fig_top = px.bar(
                top_df.sort_values(rank_col, ascending=ascending),
                x=rank_col, y='Kab/Kota', orientation='h',
                color='Provinsi', text=rank_col,
                hover_data=['Klasifikasi Label']
            )
            fig_top.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_top.update_layout(height=max(400, top_n * 25), yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col_r2:
            st.markdown(f"**Bottom {top_n} (Terburuk)**")
            bottom_df = filtered_df.nsmallest(top_n, rank_col) if not ascending else filtered_df.nlargest(top_n, rank_col)
            fig_bottom = px.bar(
                bottom_df.sort_values(rank_col, ascending=not ascending),
                x=rank_col, y='Kab/Kota', orientation='h',
                color='Provinsi', text=rank_col,
                hover_data=['Klasifikasi Label']
            )
            fig_bottom.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_bottom.update_layout(height=max(400, top_n * 25), yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bottom, use_container_width=True)
        
        st.markdown('<div class="section-header">🏅 Top 10 Provinsi per Indikator</div>', unsafe_allow_html=True)
        
        # Map original indicator names to prov_stats column names
        ind_to_pcol = {
            col('P0'): pcol('P0'),
            col('LamaSekolah'): pcol('LamaSekolah'),
            col('Pengeluaran'): pcol('Pengeluaran'),
            col('IPM'): pcol('IPM'),
            col('UmurHarapan'): pcol('UmurHarapan'),
            col('Sanitasi'): pcol('Sanitasi'),
            col('AirMinum'): pcol('AirMinum'),
            col('Pengangguran'): pcol('Pengangguran'),
            col('Partisipasi'): pcol('Partisipasi'),
            col('PDRB'): pcol('PDRB'),
        }
        
        prov_rank_data = []
        for ind in numeric_indicators:
            pcol_name = ind_to_pcol.get(ind)
            if pcol_name is None or pcol_name not in prov_stats.columns:
                continue
            asc = ind in [col('P0'), col('Pengangguran')]
            if not asc:
                top_prov = prov_stats.nlargest(10, pcol_name)
            else:
                top_prov = prov_stats.nsmallest(10, pcol_name)
            for _, row in top_prov.iterrows():
                prov_rank_data.append({
                    'Indikator': ind,
                    'Provinsi': row['Provinsi'],
                    'Nilai': row[pcol_name]
                })
        
        st.dataframe(pd.DataFrame(prov_rank_data), use_container_width=True, height=400)
    
    with tab6:
        st.markdown('<div class="section-header">🔍 Eksplorasi Data Interaktif</div>', unsafe_allow_html=True)
        
        col_search1, col_search2 = st.columns([3, 1])
        with col_search1:
            search_term = st.text_input("🔎 Cari Kabupaten/Kota atau Provinsi", placeholder="Ketik nama wilayah...")
        with col_search2:
            default_cols = ['Provinsi', 'Kab/Kota', col('P0'), col('IPM'), col('Pengeluaran'),
                           col('UmurHarapan'), col('Pengangguran'), 'Klasifikasi Label']
            show_cols = st.multiselect(
                "Tampilkan Kolom",
                filtered_df.columns.tolist(),
                default=default_cols
            )
        
        display_df = filtered_df.copy()
        if search_term:
            mask = (display_df['Provinsi'].str.contains(search_term, case=False, na=False) | 
                    display_df['Kab/Kota'].str.contains(search_term, case=False, na=False))
            display_df = display_df[mask]
        
        st.markdown(f"**Menampilkan {len(display_df)} dari {len(filtered_df)} wilayah**")
        
        if show_cols:
            style_dict = {
                col('P0'): '{:.2f}',
                col('LamaSekolah'): '{:.2f}',
                col('Pengeluaran'): '{:,.0f}',
                col('IPM'): '{:.2f}',
                col('UmurHarapan'): '{:.2f}',
                col('Sanitasi'): '{:.2f}',
                col('AirMinum'): '{:.2f}',
                col('Pengangguran'): '{:.2f}',
                col('Partisipasi'): '{:.2f}',
                col('PDRB'): lambda x: f'Rp {x:,.0f}',
            }
            # Only apply styles for columns that are actually in show_cols
            style_dict = {k: v for k, v in style_dict.items() if k in show_cols}
            
            bg_cols_p0 = [col('P0')] if col('P0') in show_cols else []
            bg_cols_good = [c for c in [col('IPM'), col('Pengeluaran'), col('UmurHarapan')] if c in show_cols]
            
            st.dataframe(
                display_df[show_cols].style.format(style_dict)
                .background_gradient(subset=bg_cols_p0, cmap='RdYlGn_r')
                .background_gradient(subset=bg_cols_good, cmap='RdYlGn'),
                use_container_width=True, height=500
            )
        
        st.markdown('<div class="section-header">📊 Profil Wilayah Terpilih</div>', unsafe_allow_html=True)
        
        selected_wilayah = st.selectbox(
            "Pilih Kabupaten/Kota untuk Detail",
            [''] + sorted(filtered_df['Kab/Kota'].unique().tolist())
        )
        
        if selected_wilayah:
            row = filtered_df[filtered_df['Kab/Kota'] == selected_wilayah].iloc[0]
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                st.markdown(f"### {selected_wilayah}, {row['Provinsi']}")
                st.markdown(f"**Klasifikasi: {'🔴 Miskin' if row[col('Klasifikasi')] == 1 else '🟢 Non-Miskin'}**")
                
                radar_indicators = [
                    ('P0 (Kemiskinan %)', row[col('P0')], 0, 50, True),
                    ('IPM', row[col('IPM')], 40, 90, False),
                    ('Pengeluaran/Th (Ribu)', row[col('Pengeluaran')], 3000, 25000, False),
                    ('Umur Harapan (Th)', row[col('UmurHarapan')], 55, 78, False),
                    ('Lama Sekolah (Th)', row[col('LamaSekolah')], 3, 13, False),
                    ('Sanitasi (%)', row[col('Sanitasi')], 0, 100, False),
                    ('Air Minum (%)', row[col('AirMinum')], 0, 100, False),
                    ('Pengangguran (%)', row[col('Pengangguran')], 0, 15, True),
                ]
                
                fig_radar = go.Figure()
                
                values = []
                labels = []
                for label, val, min_v, max_v, invert in radar_indicators:
                    if pd.notna(val):
                        norm = (val - min_v) / (max_v - min_v) * 100
                        if invert:
                            norm = 100 - norm
                        values.append(max(0, min(100, norm)))
                        labels.append(label)
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values, theta=labels, fill='toself',
                    name=selected_wilayah, line_color='#1e3a5f', fillcolor='rgba(30, 58, 95, 0.2)'
                ))
                
                avg_values = []
                for label, _, min_v, max_v, invert in radar_indicators:
                    col_name = {
                        'P0 (Kemiskinan %)': col('P0'),
                        'IPM': col('IPM'),
                        'Pengeluaran/Th (Ribu)': col('Pengeluaran'),
                        'Umur Harapan (Th)': col('UmurHarapan'),
                        'Lama Sekolah (Th)': col('LamaSekolah'),
                        'Sanitasi (%)': col('Sanitasi'),
                        'Air Minum (%)': col('AirMinum'),
                        'Pengangguran (%)': col('Pengangguran'),
                    }[label]
                    avg_val = filtered_df[col_name].mean()
                    norm = (avg_val - min_v) / (max_v - min_v) * 100
                    if invert:
                        norm = 100 - norm
                    avg_values.append(max(0, min(100, norm)))
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=avg_values, theta=labels, fill='toself',
                    name='Rata-rata Nasional', line_color='#dc2626', fillcolor='rgba(220, 38, 38, 0.1)'
                ))
                
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    height=500, showlegend=True
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col_p2:
                st.markdown("#### 📋 Detail Indikator")
                detail_data = {
                    'Indikator': [
                        'P0 - Persentase Penduduk Miskin (%)',
                        'IPM - Indeks Pembangunan Manusia',
                        'Pengeluaran per Kapita (Ribu Rupiah/Th)',
                        'Umur Harapan Hidup (Tahun)',
                        'Lama Sekolah Penduduk 15+ (Tahun)',
                        'Akses Sanitasi Layak (%)',
                        'Akses Air Minum Layak (%)',
                        'Tingkat Pengangguran Terbuka (%)',
                        'Tingkat Partisipasi Angkatan Kerja (%)',
                        'PDRB (Rupiah)'
                    ],
                    'Nilai': [
                        f"{row[col('P0')]:.2f}",
                        f"{row[col('IPM')]:.2f}",
                        f"{row[col('Pengeluaran')]:,.0f}",
                        f"{row[col('UmurHarapan')]:.2f}",
                        f"{row[col('LamaSekolah')]:.2f}",
                        f"{row[col('Sanitasi')]:.2f}",
                        f"{row[col('AirMinum')]:.2f}",
                        f"{row[col('Pengangguran')]:.2f}",
                        f"{row[col('Partisipasi')]:.2f}",
                        f"Rp {row[col('PDRB')]:,.0f}"
                    ],
                    'Rata-rata Nasional': [
                        f"{filtered_df[col('P0')].mean():.2f}",
                        f"{filtered_df[col('IPM')].mean():.2f}",
                        f"{filtered_df[col('Pengeluaran')].mean():,.0f}",
                        f"{filtered_df[col('UmurHarapan')].mean():.2f}",
                        f"{filtered_df[col('LamaSekolah')].mean():.2f}",
                        f"{filtered_df[col('Sanitasi')].mean():.2f}",
                        f"{filtered_df[col('AirMinum')].mean():.2f}",
                        f"{filtered_df[col('Pengangguran')].mean():.2f}",
                        f"{filtered_df[col('Partisipasi')].mean():.2f}",
                        f"Rp {filtered_df[col('PDRB')].mean():,.0f}"
                    ]
                }
                st.dataframe(pd.DataFrame(detail_data), use_container_width=True, hide_index=True)
    
    with tab7:
        st.markdown('<div class="section-header">💡 Smart Insights Otomatis</div>', unsafe_allow_html=True)
        
        insights = []
        
        p0_col = col('P0')
        ipm_col = col('IPM')
        pengeluaran_col = col('Pengeluaran')
        umur_harapan_col = col('UmurHarapan')
        lama_sekolah_col = col('LamaSekolah')
        sanitasi_col = col('Sanitasi')
        air_minum_col = col('AirMinum')
        pengangguran_col = col('Pengangguran')
        partisipasi_col = col('Partisipasi')
        pdrb_col = col('PDRB')
        klasifikasi_col = col('Klasifikasi')
        
        highest_p0 = filtered_df.loc[filtered_df[p0_col].idxmax()]
        lowest_p0 = filtered_df.loc[filtered_df[p0_col].idxmin()]
        insights.append(f"**Kemiskinan Tertinggi:** {highest_p0['Kab/Kota']}, {highest_p0['Provinsi']} dengan P0 = {highest_p0[p0_col]:.2f}%")
        insights.append(f"**Kemiskinan Terendah:** {lowest_p0['Kab/Kota']}, {lowest_p0['Provinsi']} dengan P0 = {lowest_p0[p0_col]:.2f}%")
        
        highest_ipm = filtered_df.loc[filtered_df[ipm_col].idxmax()]
        lowest_ipm = filtered_df.loc[filtered_df[ipm_col].idxmin()]
        insights.append(f"**IPM Tertinggi:** {highest_ipm['Kab/Kota']}, {highest_ipm['Provinsi']} dengan IPM = {highest_ipm[ipm_col]:.2f}")
        insights.append(f"**IPM Terendah:** {lowest_ipm['Kab/Kota']}, {lowest_ipm['Provinsi']} dengan IPM = {lowest_ipm[ipm_col]:.2f}")
        
        p0_corr = corr_df[p0_col].drop(p0_col).sort_values(key=abs, ascending=False)
        top_pos = p0_corr[p0_corr > 0].head(3)
        top_neg = p0_corr[p0_corr < 0].head(3)
        
        if len(top_pos) > 0:
            insights.append(f"**Faktor Positif Korelasi dengan Kemiskinan:** {', '.join([f'{idx} ({val:.3f})' for idx, val in top_pos.items()])}")
        if len(top_neg) > 0:
            insights.append(f"**Faktor Negatif Korelasi (Protektif):** {', '.join([f'{idx} ({val:.3f})' for idx, val in top_neg.items()])}")
        
        prov_miskin = filtered_df[filtered_df[klasifikasi_col] == 1].groupby('Provinsi').size().sort_values(ascending=False)
        if len(prov_miskin) > 0:
            insights.append(f"**Provinsi dengan Wilayah Miskin Terbanyak:** {prov_miskin.index[0]} ({prov_miskin.iloc[0]} wilayah)")
        
        p0_by_prov = filtered_df.groupby('Provinsi')[p0_col].mean().sort_values(ascending=False)
        insights.append(f"**Provinsi Rata-rata P0 Tertinggi:** {p0_by_prov.index[0]} ({p0_by_prov.iloc[0]:.2f}%)")
        insights.append(f"**Provinsi Rata-rata P0 Terendah:** {p0_by_prov.index[-1]} ({p0_by_prov.iloc[-1]:.2f}%)")
        
        high_pengangguran = filtered_df.nlargest(3, pengangguran_col)
        insights.append("**Pengangguran Tertinggi:** " + ", ".join([f"{r['Kab/Kota']} ({r[pengangguran_col]:.1f}%)" for _, r in high_pengangguran.iterrows()]))
        
        low_sanitasi = filtered_df.nsmallest(3, sanitasi_col)
        insights.append("**Akses Sanitasi Terendah:** " + ", ".join([f"{r['Kab/Kota']} ({r[sanitasi_col]:.1f}%)" for _, r in low_sanitasi.iterrows()]))
        
        for i, insight in enumerate(insights):
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">Insight #{i+1}</div>
                <div>{insight}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">📋 Rekomendasi Kebijakan</div>', unsafe_allow_html=True)
        
        recommendations = [
            ("🎯 **Targetkan Intervensi di Wilayah P0 Tertinggi**",
             f"Fokus program pengentasan kemiskinan di {highest_p0['Kab/Kota']}, {highest_p0['Provinsi']} dan wilayah serupa dengan P0 > {filtered_df[p0_col].quantile(0.75):.1f}%"),
            ("📚 **Tingkatkan Akses Pendidikan**",
             f"Rata-rata lama sekolah nasional {avg_lama_sekolah:.1f} tahun. Korelasi negatif kuat dengan kemiskinan menunjukkan investasi pendidikan berdampak jangka panjang."),
            ("🏥 **Perbaiki Akses Sanitasi & Air Minum**",
             f"Masih ada wilayah dengan akses sanitasi < 50% dan air minum < 60%. Prioritaskan infrastruktur dasar di {low_sanitasi.iloc[0]['Kab/Kota']} dan sejenisnya."),
            ("💼 **Kurangi Pengangguran Muda**",
             f"Tingkat pengangguran rata-rata {avg_pengangguran:.1f}%. Program pelatihan keterampilan dan penciptaan lapangan kerja diperlukan di wilayah dengan pengangguran > {filtered_df[pengangguran_col].quantile(0.75):.1f}%."),
            ("💰 **Tingkatkan Pengeluaran per Kapita**",
             f"Wilayah dengan pengeluaran per kapita rendah (< {filtered_df[pengeluaran_col].quantile(0.25):.0f} ribu) memerlukan stimulan ekonomi lokal dan pemberdayaan UMKM."),
            ("📊 **Monitoring Berbasis Data**",
             "Gunakan dashboard ini untuk pemantauan berkala (triwulanan/tahunan) perkembangan indikator kemiskinan per kabupaten/kota.")
        ]
        
        for title, desc in recommendations:
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">{title}</div>
                <div>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="footer">
        Dashboard Klasifikasi Tingkat Kemiskinan Indonesia • Data: BPS & Kementerian PPN/Bappenas<br>
        Dibangun dengan Streamlit & Plotly • Update Terakhir: {}
    </div>
    """.format(datetime.now().strftime('%d %B %Y')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()