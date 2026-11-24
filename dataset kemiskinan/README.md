# Dashboard Klasifikasi Tingkat Kemiskinan Indonesia

Aplikasi Streamlit interaktif untuk analisis komprehensif indikator kemiskinan dan pembangunan manusia di 514 kabupaten/kota di 34 provinsi Indonesia.

## 📊 Fitur Utama

| Tab | Deskripsi |
|-----|-----------|
| **📈 Overview & KPI** | 12 kartu KPI, distribusi klasifikasi kemiskinan, box plot P0 per provinsi |
| **🗺️ Analisis Wilayah** | Perbandingan provinsi (11 metrik), scatter P0 vs IPM, tabel ringkasan |
| **📊 Distribusi & Statistik** | Histogram + violin plot, statistik deskriptif, pairplot 5 indikator |
| **🔗 Korelasi & Heatmap** | Heatmap korelasi lengkap, korelasi terkuat dengan P0 |
| **🏆 Ranking Top/Bottom** | Ranking kabupaten/kota & provinsi per indikator |
| **🔍 Eksplorasi Data** | Pencarian/filter tabel, radar chart profil wilayah vs nasional |
| **💡 Smart Insights** | 10 insight otomatis + 6 rekomendasi kebijakan berbasis data |

## 📁 Struktur Project

```
dataset kemiskinan/
├── dashboard_kemiskinan.py      # Aplikasi Streamlit utama
├── MULAI_DASHBOARD.bat          # Launcher Windows (double-click)
├── requirements.txt             # Dependencies Python
├── Klasifikasi Tingkat Kemiskinan di Indonesia - Copy.csv  # Dataset asli
└── README.md                    # File ini
```

## 🚀 Cara Menjalankan

### Opsi 1: Launcher Windows (Paling Mudah)
Double-click file **`MULAI_DASHBOARD.bat`** — akan otomatis:
- Memeriksa Python & dependencies
- Menginstall package yang hilang
- Menjalankan server Streamlit di `http://localhost:8501`
- Membuka browser otomatis

### Opsi 2: Command Line (Manual)
```cmd
cd "C:\Users\OT\OneDrive\Documents\dataset kemiskinan"

:: Install dependencies (hanya sekali)
pip install -r requirements.txt

:: Jalankan dashboard
streamlit run dashboard_kemiskinan.py
```

### Opsi 3: PowerShell
```powershell
Set-Location "C:\Users\OT\OneDrive\Documents\dataset kemiskinan"
pip install -r requirements.txt
streamlit run dashboard_kemiskinan.py
```

## 📋 Requirements

- **Python 3.10+** (tested on Python 3.14)
- **Windows 10/11** (untuk file `.bat`)

Dependencies (auto-install via `requirements.txt`):
- `streamlit>=1.30.0`
- `pandas>=2.0.0`
- `plotly>=5.15.0`
- `numpy>=1.24.0`
- `scikit-learn>=1.3.0`
- `openpyxl>=3.1.0`
- `xlsxwriter>=3.1.0`
- `matplotlib>=3.7.0`

## 📊 Dataset

**Sumber:** BPS & Kementerian PPN/Bappenas  
**File:** `Klasifikasi Tingkat Kemiskinan di Indonesia - Copy.csv`  
**Cakupan:** 514 kabupaten/kota × 34 provinsi  
**Periode:** Data terbaru tersedia  

**Kolom Utama:**
| Kolom | Deskripsi |
|-------|-----------|
| `Provinsi` | Nama provinsi |
| `Kab/Kota` | Nama kabupaten/kota |
| `Persentase Penduduk Miskin (P0)` | % penduduk miskin per kab/kota |
| `Indeks Pembangunan Manusia (IPM)` | Skor IPM (0-100) |
| `Pengeluaran per Kapita` | Ribu Rupiah/orang/tahun |
| `Umur Harapan Hidup` | Tahun |
| `Rata-rata Lama Sekolah` | Tahun (penduduk 15+) |
| `Tingkat Pengangguran Terbuka` | % |
| `Tingkat Partisipasi Angkatan Kerja` | % |
| `Akses Sanitasi Layak` | % rumah tangga |
| `Akses Air Minum Layak` | % rumah tangga |
| `PDRB` | Rupiah (harga konstan) |
| `Klasifikasi Kemiskinan` | 0=Non-Miskin, 1=Miskin |

## 🎛️ Filter Interaktif (Sidebar)

- **Provinsi** — Pilih provinsi tertentu atau "Semua"
- **Kabupaten/Kota** — Filter kab/kota dalam provinsi terpilih
- **Klasifikasi** — Miskin (1) / Non-Miskin (0) / Semua
- **Rentang P0** — Slider persentase kemiskinan
- **Rentang IPM** — Slider indeks pembangunan manusia

## 📥 Export Data

- **CSV** — Download data terfilter sebagai CSV
- **Excel** — Download data terfilter sebagai Excel (.xlsx)

## 🔧 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `Python not found` | Install Python dari [python.org](https://python.org), centang "Add to PATH" |
| `ModuleNotFoundError` | Jalankan `pip install -r requirements.txt` |
| `Port 8501 in use` | Tutup instance Streamlit lain, atau ganti port: `streamlit run dashboard_kemiskinan.py --server.port 8502` |
| `Encoding error` | Pastikan file CSV menggunakan encoding UTF-8 (sudah benar) |
| Dashboard kosong | Cek filter sidebar — reset ke "Semua" |

## 🖥️ Screenshot Preview

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Dashboard Klasifikasi Tingkat Kemiskinan Indonesia       │
├─────────────────────────────────────────────────────────────┤
│  [Sidebar: Filter Provinsi, Kab/Kota, Klasifikasi, P0, IPM] │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────────┤
│Total │Avg   │Avg   │%     │Avg   │Avg   │Avg   │Total       │
│Wilayah│P0   │IPM   │Miskin│Pengelu│Umur  │Pengangg│PDRB        │
├──────┼──────┼──────┼──────┼──────┼──────┼──────┼────────────┤
│ 514  │12.27%│69.93 │12.1% │Rp10.3M│70.2 │5.32% │Rp11.3T     │
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴────────────┘
│  📈 Pie Chart    │  📦 Box Plot P0 per Provinsi               │
├──────────────────┴───────────────────────────────────────────┤
│  Tabs: Overview | Wilayah | Distribusi | Korelasi | Ranking  │
└─────────────────────────────────────────────────────────────┘
```

## 📝 Catatan Pengembangan

- **Column Mapping System** — Menggunakan `COL_MAP` & `PROV_STATS_MAP` untuk ketahanan terhadap perubahan nama kolom
- **Error Handling** — Validasi kolom sebelum akses, fallback graceful jika kolom tidak ada
- **Performance** — `@st.cache_data` pada loading CSV, filtering efisien
- **Responsive** — Layout adaptif, chart interaktif Plotly (zoom, pan, hover)

## 📄 Lisensi

Internal use — Data dari BPS/Kemendagri. Dashboard untuk keperluan analisis dan presentasi.

## 👨‍💻 Support

Jika ada error atau fitur yang diminta:
1. Cek tab **Console** browser (F12) untuk error JavaScript
2. Cek terminal tempat Streamlit dijalankan untuk error Python
3. Pastikan dataset CSV tidak corrupt dan path benar

---

**Versi:** 1.0  
**Update:** November 2024  
**Dibangun dengan:** Streamlit 1.66 + Plotly 7.1 + Pandas 3.0