"""
Studi Kasus 2 - Bridging Global Infrastructure to Address Local Challenges (HPC)

Kasus : Simulasi Monte Carlo untuk memperkirakan peluang polusi udara (PM2.5)
        melewati ambang aman di beberapa wilayah pada musim kemarau.
Ide   : Masalah lokal (kabut asap) dijawab dengan komputasi paralel.
        Pekerjaan dibagi menjadi "job" kecil, lalu dijalankan serial (1 core)
        dan paralel (banyak core) untuk dibandingkan waktunya (speedup).
Hanya memakai library bawaan Python.
"""

import multiprocessing as mp
import random
import time

AMBANG = 55.0            # ug/m3, contoh ambang harian
HARI = 30                # panjang simulasi (hari)
HARI_BURUK_MAKS = 7      # "episode buruk" bila hari melewati ambang >= 7
SIMULASI_PER_WILAYAH = 40000

# (nama, rata-rata PM2.5, simpangan baku, ketergantungan hari sebelumnya)
WILAYAH = [
    ("Kota Bengkulu", 38, 14, 0.65),
    ("Bengkulu Utara", 42, 16, 0.70),
    ("Seluma", 36, 13, 0.60),
    ("Kepahiang", 30, 11, 0.55),
    ("Rejang Lebong", 33, 12, 0.60),
    ("Mukomuko", 45, 18, 0.72),
]


def satu_job(args):
    """Satu 'job': menjalankan sekian simulasi untuk satu wilayah."""
    nama, rata, std, rho, jumlah, seed = args
    rnd = random.Random(seed)
    episode = 0
    total_hari_buruk = 0
    sd_inovasi = std * (1 - rho ** 2) ** 0.5
    for _ in range(jumlah):
        nilai = rnd.gauss(rata, std)
        hari_buruk = 0
        for _ in range(HARI):
            nilai = rata + rho * (nilai - rata) + rnd.gauss(0, sd_inovasi)
            if nilai > AMBANG:
                hari_buruk += 1
        total_hari_buruk += hari_buruk
        if hari_buruk >= HARI_BURUK_MAKS:
            episode += 1
    return nama, jumlah, episode, total_hari_buruk


def buat_job(jumlah_potongan):
    """Membagi simulasi tiap wilayah menjadi beberapa potongan job."""
    job = []
    for i, (nama, rata, std, rho) in enumerate(WILAYAH):
        per = SIMULASI_PER_WILAYAH // jumlah_potongan
        for k in range(jumlah_potongan):
            job.append((nama, rata, std, rho, per, 1000 * i + k))
    return job


def gabung(hasil):
    ringkas = {}
    for nama, jumlah, episode, hari_buruk in hasil:
        j, e, h = ringkas.get(nama, (0, 0, 0))
        ringkas[nama] = (j + jumlah, e + episode, h + hari_buruk)
    return ringkas


def status(peluang):
    if peluang >= 0.30:
        return "TINGGI"
    if peluang >= 0.10:
        return "SEDANG"
    return "RENDAH"


def main():
    core = mp.cpu_count()
    print("=" * 62)
    print("SIMULASI RISIKO PM2.5 - SERIAL vs PARALEL")
    print("=" * 62)
    print(f"Jumlah core terdeteksi : {core}")
    print(f"Simulasi per wilayah   : {SIMULASI_PER_WILAYAH:,} x {HARI} hari")
    print(f"Episode buruk          : >= {HARI_BURUK_MAKS} hari melewati "
          f"{AMBANG:.0f} ug/m3\n")

    potongan = max(core, 2) * 2
    job = buat_job(potongan)

    t0 = time.perf_counter()
    hasil_serial = [satu_job(j) for j in job]
    waktu_serial = time.perf_counter() - t0

    t0 = time.perf_counter()
    with mp.Pool(processes=core) as pool:
        hasil_paralel = pool.map(satu_job, job)
    waktu_paralel = time.perf_counter() - t0

    ringkas = gabung(hasil_paralel)
    print(f"{'Wilayah':<17}{'Peluang episode buruk':>23}{'Rata2 hari buruk':>18}"
          f"{'Status':>9}")
    for nama, (jumlah, episode, hari_buruk) in ringkas.items():
        p = episode / jumlah
        print(f"{nama:<17}{p * 100:>22.1f}%{hari_buruk / jumlah:>18.1f}"
              f"{status(p):>9}")

    sama = gabung(hasil_serial) == ringkas
    print("\n--- Waktu komputasi ---")
    print(f"Serial  (1 core)        : {waktu_serial:6.2f} detik")
    print(f"Paralel ({core} core)       : {waktu_paralel:6.2f} detik")
    speedup = waktu_serial / waktu_paralel if waktu_paralel else float("inf")
    print(f"Speedup                 : {speedup:6.2f}x")
    print(f"Hasil serial = paralel  : {'ya' if sama else 'tidak'}")
    print("\nCatatan: pada HPC sungguhan, pekerjaan seperti ini ditulis sebagai")
    print("skrip batch lalu dikirim ke antrean (mis. Slurm) dengan jumlah")
    print("node/prosesor yang diminta. Penghematan energi tidak bisa")
    print("disimpulkan dari kecepatan saja; harus diukur langsung.")


if __name__ == "__main__":
    mp.freeze_support()
    main()
