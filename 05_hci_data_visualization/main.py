"""
Studi Kasus 5 - Human-Computer Interaction & Data Visualization

Kasus : Dashboard kualitas udara (PM2.5) di terminal.
Pola  : ringkasan dulu -> filter -> rincian sesuai permintaan.
Heuristik Nielsen yang diterapkan:
  - Visibilitas status sistem : pesan [OK] / [!] setelah setiap aksi
  - Konsistensi               : menu dan istilah sama di semua layar
  - Pencegahan kesalahan      : konfirmasi y/n sebelum menghapus
  - Kontrol pengguna          : 0 selalu untuk kembali/keluar
  - Bantuan memperbaiki salah : pesan kesalahan menyebut cara memperbaiki
Visualisasi: grafik batang untuk membandingkan kategori, grafik tren untuk
waktu; tanpa dekorasi berlebihan (tidak ada efek 3D / bayangan).
Mode demo otomatis: python main.py --demo
Hanya memakai library bawaan Python.
"""

import sys

AMBANG = 55  # ug/m3, ditandai [!] bila dilewati

# kota -> daftar bacaan harian PM2.5
DATA = {
    "Bengkulu": [28, 31, 35, 42, 58, 61, 49],
    "Curup": [22, 25, 27, 30, 33, 29, 26],
    "Mukomuko": [40, 47, 52, 63, 70, 66, 58],
    "Manna": [30, 34, 33, 39, 45, 41, 37],
}

LEBAR_BAR = 30


def ok(pesan):
    print(f"[OK] {pesan}")


def salah(pesan):
    print(f"[!] {pesan}")


def baca(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return "0"


def bar(nilai, maks):
    panjang = round(nilai / maks * LEBAR_BAR) if maks else 0
    return "#" * panjang


def menu():
    print("\n" + "=" * 52)
    print(" DASHBOARD KUALITAS UDARA (PM2.5, ug/m3)")
    print("=" * 52)
    print(" [1] Ringkasan semua kota")
    print(" [2] Tren satu kota (filter)")
    print(" [3] Rincian data satu kota")
    print(" [4] Tambah bacaan baru")
    print(" [5] Hapus bacaan terakhir")
    print(" [0] Keluar")


def pilih_kota():
    daftar = list(DATA)
    print("Pilih kota:")
    for i, k in enumerate(daftar, 1):
        print(f"  {i}. {k}")
    print("  0. Kembali")
    while True:
        s = baca("Nomor kota: ")
        if s == "0":
            return None
        if s.isdigit() and 1 <= int(s) <= len(daftar):
            return daftar[int(s) - 1]
        salah(f"Masukkan angka 1-{len(daftar)}, atau 0 untuk kembali.")


def ringkasan():
    print("\nRATA-RATA PM2.5 PER KOTA (batang untuk membandingkan kategori)")
    rata = {k: sum(v) / len(v) for k, v in DATA.items() if v}
    if not rata:
        salah("Belum ada data. Pilih [4] untuk menambah bacaan.")
        return
    maks = max(rata.values())
    for kota, r in sorted(rata.items(), key=lambda kv: kv[1], reverse=True):
        tanda = "  [!] di atas ambang" if r > AMBANG else ""
        print(f"{kota:<10}{r:6.1f} | {bar(r, maks)}{tanda}")
    print(f"\nAmbang aman contoh: {AMBANG} ug/m3. Pilih [2] atau [3] untuk detail.")


def tren():
    kota = pilih_kota()
    if kota is None:
        return
    v = DATA[kota]
    if not v:
        salah(f"{kota} belum punya data. Pilih [4] untuk menambah.")
        return
    print(f"\nTREN {kota.upper()} (hari ke-1 sampai ke-{len(v)})")
    maks = max(max(v), AMBANG)
    for i, nilai in enumerate(v, 1):
        tanda = " [!]" if nilai > AMBANG else ""
        print(f"Hari {i:>2} {nilai:>4} | {bar(nilai, maks)}{tanda}")
    arah = v[-1] - v[0]
    kata = "naik" if arah > 0 else "turun" if arah < 0 else "stabil"
    print(f"\nDari hari ke-1 ke hari ke-{len(v)}: {kata} ({arah:+d}).")


def rincian():
    kota = pilih_kota()
    if kota is None:
        return
    v = DATA[kota]
    if not v:
        salah(f"{kota} belum punya data.")
        return
    urut = sorted(v)
    median = urut[len(urut) // 2] if len(urut) % 2 else \
        (urut[len(urut) // 2 - 1] + urut[len(urut) // 2]) / 2
    print(f"\nRINCIAN {kota.upper()}")
    print(f"  Jumlah bacaan : {len(v)}")
    print(f"  Minimum       : {min(v)}")
    print(f"  Maksimum      : {max(v)}")
    print(f"  Rata-rata     : {sum(v) / len(v):.1f}")
    print(f"  Median        : {median}")
    print(f"  Hari > ambang : {sum(1 for x in v if x > AMBANG)}")


def ambil_angka(prompt):
    while True:
        s = baca(prompt)
        if s == "":
            salah("Kolom tidak boleh kosong. Ketik angka 0-500, atau 'b' untuk batal.")
            continue
        if s.lower() == "b":
            return None
        try:
            n = float(s)
        except ValueError:
            salah("Itu bukan angka. Contoh yang benar: 48 atau 52.5.")
            continue
        if not 0 <= n <= 500:
            salah("Nilai harus antara 0 dan 500.")
            continue
        return n


def tambah():
    kota = pilih_kota()
    if kota is None:
        return
    n = ambil_angka(f"PM2.5 baru untuk {kota} (b = batal): ")
    if n is None:
        ok("Dibatalkan. Tidak ada data yang diubah.")
        return
    DATA[kota].append(round(n, 1) if n % 1 else int(n))
    ok(f"Bacaan {n:g} ditambahkan ke {kota}.")


def hapus():
    kota = pilih_kota()
    if kota is None:
        return
    if not DATA[kota]:
        salah(f"{kota} tidak punya data untuk dihapus.")
        return
    terakhir = DATA[kota][-1]
    jawab = baca(f"Hapus bacaan terakhir {kota} ({terakhir})? (y/n): ").lower()
    if jawab == "y":
        DATA[kota].pop()
        ok("Bacaan terakhir dihapus.")
    else:
        ok("Dibatalkan. Data tetap utuh.")


AKSI = {"1": ringkasan, "2": tren, "3": rincian, "4": tambah, "5": hapus}


def demo():
    """Menampilkan alur ringkasan -> filter -> rincian tanpa input."""
    print("MODE DEMO: ringkasan -> filter -> rincian")
    ringkasan()
    v = DATA["Mukomuko"]
    print("\nTREN MUKOMUKO")
    maks = max(max(v), AMBANG)
    for i, nilai in enumerate(v, 1):
        print(f"Hari {i:>2} {nilai:>4} | {bar(nilai, maks)}"
              f"{' [!]' if nilai > AMBANG else ''}")
    print(f"\nRincian: maks {max(v)}, rata-rata {sum(v) / len(v):.1f}, "
          f"hari > ambang {sum(1 for x in v if x > AMBANG)}")


def main():
    if "--demo" in sys.argv:
        demo()
        return
    print("Selamat datang. Ketik nomor menu lalu tekan Enter.")
    while True:
        menu()
        pilihan = baca("Pilihan Anda: ")
        if pilihan == "0":
            ok("Sampai jumpa.")
            break
        aksi = AKSI.get(pilihan)
        if aksi:
            aksi()
        else:
            salah("Pilihan tidak dikenal. Ketik angka 0-5 sesuai menu.")


if __name__ == "__main__":
    main()
