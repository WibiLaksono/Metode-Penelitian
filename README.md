# 🧠 Auto Screening RAG – Metode Penelitian

> **Automasi Screening dan Data Extraction** untuk penelitian berbasis *Systematic Literature Review (SLR)* menggunakan sumber data **Crossref** dan **Unpaywall**.  
> Program ini membantu mencari, memfilter, dan mengekstrak artikel *Open Access* secara otomatis berdasarkan **topik, tahun, dan pertanyaan riset (Research Question)**.

---

## 🚀 Fitur Utama

✅ Pencarian otomatis melalui **Crossref API**  
✅ Pemeriksaan akses penuh (*Open Access*) dengan **Unpaywall API**  
✅ Unduh PDF & ekstraksi teks otomatis  
✅ *Rule-based* + *Semantic screening* (menggunakan model **SentenceTransformer**)  
✅ Ekspor hasil ke **CSV** dan **BibTeX**  
✅ Visualisasi *PRISMA Flow Diagram*  
✅ Ringkasan otomatis per artikel (metode, temuan utama, dan full summary)

---

## 📁 Struktur Proyek

```
AUTO-SCREENING/
│
├── auto_screening_rag.py               # Main script (jalankan file ini)
├── requirements.txt                    # Daftar dependency
├── README.md                           # Dokumentasi ini
│
├── screening_output/                   # Folder hasil output Crossref + Unpaywall
│   ├── pdfs/                           # PDF hasil unduhan
│   ├── screening_log.csv               # Log hasil screening
│   ├── extracted_data.csv              # Data hasil ekstraksi teks
│   ├── search_results.bib              # Daftar artikel (.bib)
│   └── prisma_flow.png                 # Diagram PRISMA otomatis
│
└── screening_output_ieee/              # (opsional) hasil dari IEEE API bila aktif
```

---

## 🧩 Persiapan Lingkungan

### 1️⃣ Clone Repository
```bash
git clone https://github.com/WibiLaksono/Metode-Penelitian.git
cd Metode-Penelitian/AUTO-SCREENING
```

### 2️⃣ Buat Virtual Environment (disarankan)
```bash
python -m venv venv
```

Aktifkan environment:

- **Windows**
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux**
  ```bash
  source venv/bin/activate
  ```

### 3️⃣ Instal Dependensi
Pastikan Python ≥ 3.9 sudah terinstal.

```bash
pip install -r requirements.txt
```

📦 Isi `requirements.txt`:
```txt
requests>=2.31.0
bibtexparser>=1.4.0
pandas>=2.2.0
tqdm>=4.66.1
pdfminer.six>=20221105
sentence-transformers>=2.7.0
matplotlib>=3.8.0
torch>=2.0.0
numpy>=1.25.0
```

---

## ⚙️ Konfigurasi

Buka file `auto_screening_rag.py`, lalu sesuaikan bagian `CONFIG` di awal file:

```python
CONFIG = {
    "mailto": "your_email@example.com",      # Emailmu (untuk API Crossref & Unpaywall)
    "unpaywall_email": "your_email@example.com",
    "query": '"retrieval augmented generation" OR "document chunking"',
    "filters": {
        "from_pub_date": 2018,               # Tahun mulai
        "until_pub_date": 2025,              # Tahun akhir
    },
    "max_results": 200,                      # Jumlah artikel maksimum
    "similarity_threshold": 0.55,            # Ambang kemiripan semantik
    "download_pdfs": True                    # Unduh PDF OA otomatis
}
```

---

## ▶️ Menjalankan Program

Setelah environment dan dependensi siap, jalankan:

```bash
python auto_screening_rag.py
```

---

## 🧾 Proses yang Dilakukan

1. **Pencarian artikel di Crossref**
   - Berdasarkan query dan tahun yang ditentukan
   - Menampilkan jumlah total hasil pencarian

2. **Pembersihan data duplikat**

3. **Cek Open Access (OA) via Unpaywall**
   - Hanya artikel dengan akses penuh (PDF) yang diproses lebih lanjut

4. **Unduh dan ekstrak teks PDF**

5. **Screening otomatis**
   - Rule-based: berdasarkan keyword tertentu
   - Semantic-based: membandingkan dengan *Research Questions*

6. **Pembuatan output**
   - `screening_log.csv` → seluruh hasil dengan status Include/Exclude
   - `extracted_data.csv` → data detail artikel yang di-*include*
   - `prisma_flow.png` → visualisasi proses penyaringan

---

## 📊 Contoh Output (terminal)

```
🔍 Searching Crossref for query: "retrieval augmented generation" OR "document chunking"
  → Retrieved 200 items
✅ Total retrieved from Crossref: 195
🧹 Removing duplicates...
✅ 190 unique records (removed 5 duplicates)

📄 Checking open access + screening papers...
Processing: 100%|██████████| 190/190 [00:55<00:00,  3.44it/s]

📊 Screening completed:
  Total unique records     : 190
  With full text available : 64
  Included after screening : 24
✅ Saved outputs to folder: /path/to/AUTO-SCREENING/screening_output
```

---

## 📂 Hasil Output

| File | Deskripsi |
|------|------------|
| `screening_log.csv` | Log lengkap setiap artikel, OA status, keputusan screening |
| `extracted_data.csv` | Ringkasan metode, temuan, dan snippet full text |
| `search_results.bib` | Daftar referensi artikel untuk Zotero / Mendeley |
| `pdfs/` | Folder PDF hasil unduhan |
| `prisma_flow.png` | Diagram PRISMA otomatis untuk laporan SLR |

---

## 💡 Tips Penggunaan

- Gunakan **query** yang lebih spesifik untuk hasil lebih relevan.  
  Contoh:
  ```python
  "retrieval augmented generation" AND "text segmentation"
  ```
- Gunakan **threshold similarity** lebih tinggi (`0.65–0.75`) untuk penyaringan ketat.
- Jika ingin menambahkan sumber lain (IEEE, EuropePMC, dsb), tambahkan fungsi serupa di bagian awal script.
- Untuk mempercepat, jalankan di mesin dengan GPU (Torch akan otomatis mendeteksi).

---

## 🧠 Tentang Proyek Ini

Proyek ini dikembangkan untuk mendukung tugas **Metode Penelitian (Metopen)**, Universitas Gadjah Mada,  
oleh **Wibi Laksono Wijaya**, dengan tujuan mempercepat proses *Systematic Literature Review* secara otomatis menggunakan kombinasi **Rule-based** dan **Semantic Similarity Filtering**.

---

## 🖋️ Lisensi

Lisensi: **MIT License**

Kamu bebas menggunakan, memodifikasi, dan membagikan ulang dengan mencantumkan atribusi yang sesuai.

---

### 📬 Kontak

- **Author:** Wibi Laksono Wijaya  
- **Email:** wibilaksonowijaya@mail.ugm.ac.id  
- **GitHub:** [@WibiLaksono](https://github.com/WibiLaksono)

---

> “Automating the tedious, so you can focus on the insightful.”
