"""
Studi Kasus 6 - Attributing Direct Drivers to Deforestation Alerts
                with Satellite Imagery and AI

Kasus : Mendeteksi hilangnya hutan dari citra satelit simulasi 30x30 piksel
        (1 piksel = 30 m x 30 m = 0,09 ha), lalu menebak penyebab langsungnya.
Ide   : - Citra optik (NDVI) terhalang awan; radar tetap bisa mengamati.
          Keduanya dipakai bersama agar saling melengkapi.
        - Satu alert hanya berkata "ada perubahan", bukan penyebabnya.
          Penyebab ditebak dari bentuk, luas, dan NDVI, dengan tingkat
          keyakinan. Bila bukti kurang -> "tidak pasti (keyakinan rendah)".
Catatan: klasifikasi di sini berbasis aturan (rule-based), bukan CNN, dan
         hanya contoh. Hasil asli memerlukan verifikasi lapangan.
Hanya memakai library bawaan Python.
"""

import random

N = 30
HA_PER_PIKSEL = 0.09

# Ambang
TURUN_NDVI = 0.30      # alert optik bila NDVI turun lebih dari ini
TURUN_RADAR_DB = 3.0   # alert radar bila hamburan balik turun >= 3 dB


def buat_citra(seed=21):
    rnd = random.Random(seed)
    ndvi_sebelum = [[0.82 + rnd.gauss(0, 0.02) for _ in range(N)] for _ in range(N)]
    radar_sebelum = [[-7.0 + rnd.gauss(0, 0.4) for _ in range(N)] for _ in range(N)]
    ndvi_sesudah = [r[:] for r in ndvi_sebelum]
    radar_sesudah = [r[:] for r in radar_sebelum]
    awan = [[False] * N for _ in range(N)]
    kebenaran = {}

    def buka(baris, kolom, nilai_ndvi, label):
        for r in baris:
            for c in kolom:
                ndvi_sesudah[r][c] = nilai_ndvi + rnd.gauss(0, 0.03)
                radar_sesudah[r][c] = -11.5 + rnd.gauss(0, 0.5)
                kebenaran[(r, c)] = label

    # Jalan (garis panjang, tipis)
    buka(range(3, 4), range(2, 26), 0.35, "Jalan")
    # Pertanian besar (persegi teratur), sebagian tertutup awan
    buka(range(12, 20), range(14, 24), 0.30, "Pertanian")
    # Kebakaran (NDVI sangat rendah, bentuk tidak teratur)
    for r in range(20, 27):
        for c in range(3, 12):
            if (r - 23) ** 2 + (c - 7) ** 2 <= 14 + rnd.randint(-2, 2):
                ndvi_sesudah[r][c] = 0.05 + rnd.gauss(0, 0.02)
                radar_sesudah[r][c] = -11.0 + rnd.gauss(0, 0.5)
                kebenaran[(r, c)] = "Kebakaran"
    # Penebangan selektif (petak kecil)
    buka(range(9, 11), range(4, 6), 0.40, "Penebangan")
    # Kejadian kecil yang seluruhnya tertutup awan
    buka(range(26, 28), range(22, 24), 0.35, "Tidak diketahui")

    # Awan menutupi sebagian citra sesudah
    for r in range(11, 17):
        for c in range(14, 19):
            awan[r][c] = True
    for r in range(24, 29):
        for c in range(20, 26):
            awan[r][c] = True
    for r in range(N):
        for c in range(N):
            if awan[r][c]:
                ndvi_sesudah[r][c] = None   # optik tidak tersedia
    return ndvi_sebelum, ndvi_sesudah, radar_sebelum, radar_sesudah, awan, kebenaran


def deteksi_alert(nb, na, rb, ra):
    alert = [[False] * N for _ in range(N)]
    for r in range(N):
        for c in range(N):
            if na[r][c] is not None:
                alert[r][c] = (nb[r][c] - na[r][c]) > TURUN_NDVI
            else:
                alert[r][c] = (rb[r][c] - ra[r][c]) >= TURUN_RADAR_DB
    return alert


def kelompokkan(alert):
    """Menggabungkan piksel alert bersebelahan (8 arah) dengan flood fill."""
    terlihat = [[False] * N for _ in range(N)]
    area = []
    for r in range(N):
        for c in range(N):
            if alert[r][c] and not terlihat[r][c]:
                tumpukan = [(r, c)]
                terlihat[r][c] = True
                piksel = []
                while tumpukan:
                    y, x = tumpukan.pop()
                    piksel.append((y, x))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = y + dy, x + dx
                            if (0 <= ny < N and 0 <= nx < N and alert[ny][nx]
                                    and not terlihat[ny][nx]):
                                terlihat[ny][nx] = True
                                tumpukan.append((ny, nx))
                area.append(piksel)
    return area


def fitur_area(piksel, na, awan):
    baris = [p[0] for p in piksel]
    kolom = [p[1] for p in piksel]
    tinggi = max(baris) - min(baris) + 1
    lebar = max(kolom) - min(kolom) + 1
    nilai = [na[r][c] for r, c in piksel if na[r][c] is not None]
    return {
        "n": len(piksel),
        "luas_ha": len(piksel) * HA_PER_PIKSEL,
        "isi_kotak": len(piksel) / (tinggi * lebar),
        "memanjang": max(tinggi, lebar) / min(tinggi, lebar),
        "ndvi": sum(nilai) / len(nilai) if nilai else None,
        "awan": sum(1 for r, c in piksel if awan[r][c]) / len(piksel),
        "pusat": (sum(baris) / len(baris), sum(kolom) / len(kolom)),
    }


def klasifikasi(f):
    """Mengembalikan (penyebab, keyakinan, alasan)."""
    if f["awan"] >= 0.8 and f["luas_ha"] < 1:
        return "Tidak pasti", "rendah", "area kecil dan hampir seluruhnya tertutup awan"
    if f["memanjang"] >= 4 and f["luas_ha"] < 4:
        return "Pembangunan jalan", "tinggi", "bentuk memanjang seperti garis"
    if f["ndvi"] is not None and f["ndvi"] < 0.15:
        return "Kebakaran", "sedang", "NDVI sangat rendah (lahan gosong)"
    if f["luas_ha"] >= 4 and f["isi_kotak"] >= 0.8:
        yakin = "sedang" if f["awan"] > 0.2 else "tinggi"
        return "Pertanian skala besar", yakin, "area luas dan berbentuk kotak teratur"
    if f["luas_ha"] < 1:
        return "Penebangan selektif", "sedang", "petak kecil di tengah hutan"
    return "Tidak pasti", "rendah", "ciri tidak cocok dengan aturan mana pun"


def cetak_peta(alert, awan, label_area):
    print("Peta (. hutan | ? awan tanpa alert | huruf = area alert):")
    peta = [["." for _ in range(N)] for _ in range(N)]
    for r in range(N):
        for c in range(N):
            if awan[r][c]:
                peta[r][c] = "?"
    for huruf, piksel in label_area.items():
        for r, c in piksel:
            peta[r][c] = huruf
    for baris in peta:
        print("  " + "".join(baris))


def main():
    nb, na, rb, ra, awan, kebenaran = buat_citra()
    print("=" * 64)
    print("ATRIBUSI PENYEBAB DEFORESTASI (simulasi optik + radar)")
    print("=" * 64)
    jumlah_awan = sum(sum(1 for x in r if x) for r in awan)
    print(f"Citra {N}x{N} piksel, piksel tertutup awan: {jumlah_awan} "
          f"({jumlah_awan / N / N * 100:.1f}%)")
    print("Piksel berawan memakai radar; lainnya memakai penurunan NDVI.\n")

    alert = deteksi_alert(nb, na, rb, ra)
    total = sum(sum(1 for x in r if x) for r in alert)
    print(f"Total piksel alert: {total} (= {total * HA_PER_PIKSEL:.2f} ha)\n")

    area = kelompokkan(alert)
    area.sort(key=len, reverse=True)
    huruf = {chr(ord("A") + i): p for i, p in enumerate(area)}
    cetak_peta(alert, awan, huruf)

    print(f"\nDitemukan {len(area)} area alert:\n")
    print(f"{'ID':<4}{'Luas(ha)':>9}{'Awan':>7}{'NDVI':>7}  "
          f"{'Dugaan penyebab':<24}{'Keyakinan':<10}")
    benar = 0
    for h, piksel in huruf.items():
        f = fitur_area(piksel, na, awan)
        sebab, yakin, alasan = klasifikasi(f)
        ndvi = f"{f['ndvi']:.2f}" if f["ndvi"] is not None else "  -"
        print(f"{h:<4}{f['luas_ha']:>9.2f}{f['awan'] * 100:>6.0f}%{ndvi:>7}  "
              f"{sebab:<24}{yakin:<10}")
        print(f"    alasan: {alasan}")
        # bandingkan dengan kebenaran simulasi
        label_asli = {}
        for p in piksel:
            l = kebenaran.get(p, "?")
            label_asli[l] = label_asli.get(l, 0) + 1
        asli = max(label_asli, key=label_asli.get)
        cocok = {"Pertanian skala besar": "Pertanian", "Pembangunan jalan": "Jalan",
                 "Kebakaran": "Kebakaran", "Penebangan selektif": "Penebangan",
                 "Tidak pasti": "Tidak diketahui"}
        if cocok.get(sebab) == asli:
            benar += 1
    print(f"\nKesesuaian dengan kebenaran simulasi: {benar} dari {len(area)} area")
    print("\nCatatan penting:")
    print("- Satu alert hanya menunjukkan perubahan, bukan penyebab pasti.")
    print("- Area 'Tidak pasti' perlu data lapangan atau citra tambahan.")
    print("- Hubungan waktu antarkejadian belum membuktikan sebab-akibat.")
    print("- Peta satelit adalah alat bantu; verifikasi lapangan tetap wajib")
    print("  sebelum menetapkan tindakan atau tanggung jawab.")


if __name__ == "__main__":
    main()
