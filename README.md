# Tugas 6 Studi Kasus dengan Python

|                   |                        |
|-------------------|------------------------|
| **Nama**          | [isi nama Anda]        |
| **NPM**           | [isi NPM Anda]         |
| **Program Studi** | [isi program studi]    |
| **Universitas**   | [isi universitas]      |

Repositori ini berisi 6 studi kasus yang dibuat dari 6 materi kuliah praktisi. Setiap studi kasus ada di folder sendiri dan hanya terdiri dari **1 file Python** (`main.py`). Semua program hanya memakai library bawaan Python, jadi **tidak perlu install apa pun**.

## Struktur Folder

```
studikasus/
├── README.md
├── 01_data_analytics_ai/main.py
├── 02_hpc_infrastructure/main.py
├── 03_gis_career/main.py
├── 04_machine_learning/main.py
├── 05_hci_data_visualization/main.py
└── 06_deforestation_satellite_ai/main.py
```

## Cara Menjalankan

Pastikan Python 3.8 atau lebih baru sudah terpasang, lalu jalankan dari folder utama:

```
python 01_data_analytics_ai/main.py
python 02_hpc_infrastructure/main.py
python 03_gis_career/main.py
python 04_machine_learning/main.py
python 05_hci_data_visualization/main.py
python 06_deforestation_satellite_ai/main.py
```

Studi kasus 5 bersifat interaktif. Untuk melihat alurnya tanpa mengetik, jalankan `python 05_hci_data_visualization/main.py --demo`.

> Semua data di repositori ini adalah **data contoh (fiktif)** yang dibuat untuk latihan.

---

## 1. Make Sense of Data with Analysis and AI

**Folder:** `01_data_analytics_ai`

**Kasus:** PT Maju Bersama (distributor fiktif): pendapatan naik, tetapi laba turun, piutang naik, dan arus kas operasional melemah.

**Yang dilakukan program:**

1. Menerjemahkan pertanyaan luas ("Bagaimana kinerja perusahaan?") menjadi pertanyaan analitik yang terukur.
2. Memeriksa kualitas data faktur: membuang duplikat dan nilai kosong, lalu melaporkan perubahan jumlah baris.
3. **Deskriptif:** menghitung perubahan, rata-rata, median, dan standar deviasi, serta margin laba.
4. **Diagnostik:** mencari pelanggan yang paling menyumbang piutang belum dibayar.
5. **Prediktif:** memperkirakan piutang dan kas bulan berikutnya dengan **regresi linear**.
6. **Preskriptif:** menyarankan penurunan batas kredit untuk pelanggan berisiko.

**Konsep:** empat jenis analitik, kualitas data (*garbage in, garbage out*), regresi linear, keputusan berbasis data.

---

## 2. Bridging Global Infrastructure to Address Local Challenges with HPC

**Folder:** `02_hpc_infrastructure`

**Kasus:** Simulasi Monte Carlo peluang episode polusi udara (PM2.5) di 6 wilayah pada musim kemarau.

**Yang dilakukan program:**

1. Membagi pekerjaan menjadi banyak *job* kecil, mirip skrip batch pada HPC.
2. Menjalankan 240.000 simulasi (6 wilayah x 40.000 x 30 hari).
3. Membandingkan waktu **serial** (1 core) dengan **paralel** (`multiprocessing`).
4. Menampilkan **speedup** dan memastikan hasil serial sama dengan paralel.
5. Memberi status risiko TINGGI / SEDANG / RENDAH per wilayah.

**Konsep:** komputasi paralel, Monte Carlo, speedup, masalah lokal yang dijawab dengan infrastruktur komputasi.

---

## 3. Career and Competition in the Industrial Era with GIS

**Folder:** `03_gis_career`

**Kasus:** Perencanaan lokasi usaha, salah satu penerapan GIS di materi: memilih lokasi gerai baru di Kota Bengkulu.

**Yang dilakukan program:**

1. Menyimpan data permukiman, gerai pesaing, dan calon lokasi beserta koordinatnya.
2. Menghitung jarak di permukaan bumi dengan **rumus Haversine**.
3. Menghitung jumlah penduduk dalam radius pasar 3 km.
4. Menentukan arah pesaing terdekat dan memberi **skor** (60% penduduk, 40% jarak ke pesaing).
5. Merekomendasikan lokasi terbaik lengkap dengan link Google Maps.

**Konsep:** data spasial, koordinat geografis, analisis radius, data spasial sebagai bukti pendukung keputusan.

---

## 4. Introduction to Machine Learning

**Folder:** `04_machine_learning`

**Kasus:** Memprediksi faktur yang akan **terlambat** dibayar.

**Yang dilakukan program:**

1. Membagi data menjadi data latih (70%) dan data uji (30%), lalu melakukan standardisasi.
2. Membuat **regresi logistik** dari nol dengan *gradient descent*.
3. Mengevaluasi dengan akurasi, precision, recall, F1-score, dan *confusion matrix*.
4. Menunjukkan **jebakan akurasi** pada data tidak seimbang dibanding baseline "selalu tepat waktu".
5. Mendemonstrasikan **data leakage** dan memprediksi faktur baru.

**Konsep:** supervised learning, klasifikasi, evaluasi model, data tidak seimbang, data leakage.

---

## 5. Human-Computer Interaction & Data Visualization

**Folder:** `05_hci_data_visualization`

**Kasus:** Dashboard kualitas udara (PM2.5) berbasis menu interaktif di terminal.

**Fitur:**

- `[1]` Ringkasan semua kota (grafik batang)
- `[2]` Tren satu kota (filter)
- `[3]` Rincian data satu kota
- `[4]` Tambah bacaan baru
- `[5]` Hapus bacaan terakhir, dengan konfirmasi
- `[0]` Keluar

**Prinsip HCI yang diterapkan:**

- **Visibilitas status sistem**, dengan pesan `[OK]` saat berhasil dan `[!]` saat terjadi kesalahan.
- **Konsistensi**, sehingga menu dan istilah sama di semua layar.
- **Pencegahan kesalahan**, dengan konfirmasi `y/n` sebelum menghapus dan validasi angka 0 sampai 500.
- **Bantuan memperbaiki kesalahan**, karena pesan galat memberi contoh input yang benar.
- **Pola dashboard:** ringkasan lebih dulu, lalu filter, lalu rincian.
- **Visualisasi sederhana** tanpa dekorasi berlebihan (*chartjunk*).

**Konsep:** desain interaksi, usability, heuristik Nielsen, visualisasi data.

---

## 6. Attributing Direct Drivers to Deforestation Alerts with Satellite Imagery and AI

**Folder:** `06_deforestation_satellite_ai`

**Kasus:** Mendeteksi hilangnya hutan dari citra satelit simulasi, lalu menduga penyebab langsungnya.

**Yang dilakukan program:**

1. Membuat citra 30x30 piksel (1 piksel = 30 m x 30 m) sebelum dan sesudah, lengkap dengan **awan**.
2. Memakai penurunan **NDVI** (optik) untuk piksel cerah dan penurunan hamburan balik **radar** untuk piksel berawan.
3. Menggabungkan piksel alert yang bersebelahan menjadi area dengan algoritma **flood fill**.
4. Mengekstrak fitur tiap area: luas (ha), kerapatan bentuk, rasio panjang/lebar, NDVI, dan persentase awan.
5. Mengklasifikasikan penyebab dengan aturan, lengkap dengan **tingkat keyakinan**:

| Penyebab              | Ciri-ciri                                   |
|-----------------------|---------------------------------------------|
| Pembangunan jalan     | Area memanjang seperti garis                |
| Kebakaran             | NDVI sangat rendah (lahan gosong)           |
| Pertanian skala besar | Area luas dan berbentuk kotak teratur       |
| Penebangan selektif   | Petak kecil di tengah hutan                 |
| Tidak pasti           | Area kecil dan hampir tertutup awan penuh   |

**Konsep:** penginderaan jauh, NDVI, optik vs radar, deteksi perubahan, klasifikasi dengan tingkat keyakinan.

> Catatan: klasifikasi di sini berbasis aturan, bukan CNN seperti pada penelitian di materi. Hasil asli tetap memerlukan verifikasi lapangan.
