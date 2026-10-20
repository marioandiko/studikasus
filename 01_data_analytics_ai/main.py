"""
Studi Kasus 1 - Make Sense of Data with Analysis and AI

Kasus : PT Maju Bersama (distributor fiktif). Pendapatan naik, tetapi laba
        turun, piutang naik, dan arus kas operasional melemah.
Alur  : pertanyaan -> cek kualitas data -> deskriptif -> diagnostik
        -> prediktif (regresi linear) -> preskriptif.
Hanya memakai library bawaan Python.
"""

import random
import statistics

BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
         "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

# Data bulanan (juta rupiah) - data contoh (fiktif)
PENDAPATAN = [820, 840, 865, 890, 930, 960, 1000, 1040, 1090, 1130, 1180, 1230]
LABA_BERSIH = [95, 94, 92, 90, 86, 83, 80, 76, 72, 68, 64, 60]
PIUTANG = [210, 220, 240, 262, 290, 320, 355, 392, 430, 475, 520, 570]
KAS_OPERASIONAL = [70, 68, 64, 60, 55, 50, 44, 38, 33, 27, 22, 16]

# Pelanggan: (nama, peluang telat bayar, rata-rata nilai faktur dalam juta)
PELANGGAN = [
    ("Toko Sinar", 0.10, 12), ("CV Berkah", 0.15, 18),
    ("UD Makmur", 0.20, 10), ("PT Harapan", 0.65, 40),
    ("Toko Jaya", 0.30, 15), ("CV Mitra", 0.70, 35),
]


def garis(judul):
    print("\n" + "=" * 62)
    print(judul)
    print("=" * 62)


def buat_faktur():
    """Membuat data faktur contoh, sengaja diberi duplikat dan nilai kosong."""
    rnd = random.Random(11)
    faktur = []
    for i in range(1, 121):
        nama, p_telat, rata = rnd.choice(PELANGGAN)
        telat = rnd.random() < p_telat
        faktur.append({
            "id": f"INV-{i:03d}",
            "pelanggan": nama,
            "nilai": round(rnd.uniform(0.6, 1.4) * rata, 1),
            "telat": telat,
            "belum_dibayar": telat and rnd.random() < 0.7,
        })
    faktur.append(dict(faktur[3]))            # duplikat
    faktur.append({"id": "INV-999", "pelanggan": "CV Mitra",
                   "nilai": None, "telat": True, "belum_dibayar": True})
    return faktur


def regresi_linear(y):
    """Mengembalikan (kemiringan, titik potong) dengan x = 1..n."""
    n = len(y)
    x = list(range(1, n + 1))
    mx, my = sum(x) / n, sum(y) / n
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / \
        sum((xi - mx) ** 2 for xi in x)
    return b, my - b * mx


def persen(awal, akhir):
    return (akhir - awal) / awal * 100


def main():
    garis("1. PERTANYAAN BISNIS")
    print('Pertanyaan luas : "Bagaimana kinerja perusahaan?"')
    print("Pertanyaan analitik yang terukur:")
    print("  a. Mengapa laba turun padahal pendapatan naik?")
    print("  b. Pelanggan mana yang paling menyumbang kenaikan piutang?")
    print("  c. Berapa perkiraan piutang bulan depan?")

    garis("2. KUALITAS DATA (garbage in, garbage out)")
    faktur = buat_faktur()
    print(f"Jumlah baris faktur awal   : {len(faktur)}")
    terlihat, bersih, duplikat, kosong = set(), [], 0, 0
    for f in faktur:
        if f["id"] in terlihat:
            duplikat += 1
            continue
        terlihat.add(f["id"])
        if f["nilai"] is None:
            kosong += 1
            continue
        bersih.append(f)
    print(f"Duplikat dibuang           : {duplikat}")
    print(f"Nilai kosong dibuang       : {kosong}")
    print(f"Jumlah baris setelah bersih: {len(bersih)}")

    garis("3. DESKRIPTIF - apa yang terjadi?")
    seri = [("Pendapatan", PENDAPATAN), ("Laba bersih", LABA_BERSIH),
            ("Piutang", PIUTANG), ("Kas operasional", KAS_OPERASIONAL)]
    print(f"{'Metrik':<17}{'Jan':>7}{'Des':>7}{'Perubahan':>11}{'Rata2':>9}"
          f"{'Median':>9}{'Std':>8}")
    for nama, data in seri:
        print(f"{nama:<17}{data[0]:>7}{data[-1]:>7}"
              f"{persen(data[0], data[-1]):>10.1f}%"
              f"{statistics.mean(data):>9.1f}{statistics.median(data):>9.1f}"
              f"{statistics.pstdev(data):>8.1f}")
    margin_awal = LABA_BERSIH[0] / PENDAPATAN[0] * 100
    margin_akhir = LABA_BERSIH[-1] / PENDAPATAN[-1] * 100
    print(f"\nMargin laba bersih turun dari {margin_awal:.1f}% menjadi "
          f"{margin_akhir:.1f}%.")
    print("Catatan: angka ini baru SINYAL. Penyebabnya belum diketahui.")

    garis("4. DIAGNOSTIK - mengapa terjadi?")
    belum = [f for f in bersih if f["belum_dibayar"]]
    total_belum = sum(f["nilai"] for f in belum)
    kontribusi = {}
    jumlah_faktur = {}
    jumlah_telat = {}
    for f in bersih:
        jumlah_faktur[f["pelanggan"]] = jumlah_faktur.get(f["pelanggan"], 0) + 1
        jumlah_telat[f["pelanggan"]] = jumlah_telat.get(f["pelanggan"], 0) + f["telat"]
    for f in belum:
        kontribusi[f["pelanggan"]] = kontribusi.get(f["pelanggan"], 0) + f["nilai"]
    print(f"Total faktur belum dibayar: Rp {total_belum:.1f} juta\n")
    print(f"{'Pelanggan':<14}{'Belum bayar':>13}{'Porsi':>8}{'% telat':>9}")
    urut = sorted(kontribusi.items(), key=lambda kv: kv[1], reverse=True)
    for nama, nilai in urut:
        telat_pct = jumlah_telat[nama] / jumlah_faktur[nama] * 100
        print(f"{nama:<14}{nilai:>13.1f}{nilai / total_belum * 100:>7.1f}%"
              f"{telat_pct:>8.0f}%")

    garis("5. PREDIKTIF - apa yang mungkin terjadi? (regresi linear)")
    b, a = regresi_linear(PIUTANG)
    prediksi = a + b * 13
    print(f"Tren piutang naik rata-rata Rp {b:.1f} juta per bulan.")
    print(f"Perkiraan piutang bulan ke-13 (Jan tahun depan): Rp {prediksi:.0f} juta")
    b2, a2 = regresi_linear(KAS_OPERASIONAL)
    kas13 = a2 + b2 * 13
    print(f"Perkiraan kas operasional bulan ke-13        : Rp {kas13:.0f} juta")
    print("Catatan: model sederhana, hanya garis tren. Tidak memuat musim/"
          "kebijakan baru.")

    garis("6. PRESKRIPTIF - apa yang sebaiknya dilakukan?")
    ada = False
    for nama, nilai in urut:
        porsi = nilai / total_belum * 100
        telat_pct = jumlah_telat[nama] / jumlah_faktur[nama] * 100
        if porsi >= 20 and telat_pct >= 50:
            ada = True
            print(f"- {nama}: porsi {porsi:.0f}% dan telat {telat_pct:.0f}% "
                  "-> turunkan batas kredit dan tagih lebih awal.")
    if not ada:
        print("- Tidak ada pelanggan yang melewati ambang risiko.")
    if kas13 < 10:
        print("- Kas operasional hampir habis: prioritaskan penagihan "
              "sebelum menambah stok.")
    print("\nKeputusan akhir tetap membutuhkan pengetahuan bisnis "
          "(mis. alasan diskon atau kontrak khusus).")


if __name__ == "__main__":
    main()
