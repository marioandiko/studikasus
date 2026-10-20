"""
Studi Kasus 3 - Career and Competition in the Industrial Era with GIS

Kasus : Perencanaan lokasi usaha (salah satu penerapan GIS di materi).
        Memilih lokasi gerai baru di Kota Bengkulu berdasarkan jumlah
        penduduk di sekitar lokasi dan jarak ke gerai pesaing.
Konsep: koordinat geografis, rumus Haversine, analisis radius, skor lokasi.
Semua nama dan koordinat di bawah adalah data contoh (fiktif).
Hanya memakai library bawaan Python.
"""

import math

R_BUMI = 6371.0  # km

# Pusat permukiman: (nama, lat, lon, penduduk)
PERMUKIMAN = [
    ("Padang Harapan", -3.7870, 102.2750, 14000),
    ("Sawah Lebar", -3.8100, 102.2800, 11000),
    ("Kebun Tebeng", -3.8330, 102.3000, 9000),
    ("Pasar Melintang", -3.7950, 102.2600, 8000),
    ("Kampung Bali", -3.7800, 102.2580, 6500),
    ("Betungan", -3.8650, 102.3250, 7000),
]

# Gerai pesaing yang sudah ada
PESAING = [
    ("Pesaing A", -3.7900, 102.2700),
    ("Pesaing B", -3.8120, 102.2750),
    ("Pesaing C", -3.7820, 102.2600),
]

# Calon lokasi gerai baru
KANDIDAT = [
    ("Lokasi 1 - Dekat Kampus", -3.7600, 102.2700),
    ("Lokasi 2 - Jalan Raya Sawah Lebar", -3.8140, 102.2860),
    ("Lokasi 3 - Pusat Kota", -3.7930, 102.2640),
    ("Lokasi 4 - Kebun Tebeng", -3.8300, 102.2980),
    ("Lokasi 5 - Betungan", -3.8620, 102.3220),
]

RADIUS_PASAR_KM = 3.0
JARAK_PESAING_IDEAL_KM = 2.0


def haversine(lat1, lon1, lat2, lon2):
    """Jarak dua titik di permukaan bumi (km)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_BUMI * math.asin(math.sqrt(a))


def arah(lat1, lon1, lat2, lon2):
    """Arah mata angin dari titik 1 ke titik 2."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    derajat = (math.degrees(math.atan2(y, x)) + 360) % 360
    nama = ["Utara", "Timur Laut", "Timur", "Tenggara",
            "Selatan", "Barat Daya", "Barat", "Barat Laut"]
    return nama[int((derajat + 22.5) // 45) % 8]


def analisis(kandidat):
    nama, lat, lon = kandidat
    penduduk, terjangkau = 0, []
    for p_nama, p_lat, p_lon, jumlah in PERMUKIMAN:
        jarak = haversine(lat, lon, p_lat, p_lon)
        if jarak <= RADIUS_PASAR_KM:
            penduduk += jumlah
            terjangkau.append((p_nama, jarak))
    pesaing = min(((n, haversine(lat, lon, a, b)) for n, a, b in PESAING),
                  key=lambda t: t[1])
    pesaing_dalam = sum(1 for _, a, b in PESAING
                        if haversine(lat, lon, a, b) <= RADIUS_PASAR_KM)
    return {
        "nama": nama, "lat": lat, "lon": lon, "penduduk": penduduk,
        "terjangkau": terjangkau, "pesaing_terdekat": pesaing,
        "pesaing_dalam": pesaing_dalam,
    }


def beri_skor(hasil, maks_penduduk):
    skor_pop = hasil["penduduk"] / maks_penduduk * 60
    jarak = min(hasil["pesaing_terdekat"][1], JARAK_PESAING_IDEAL_KM)
    skor_pesaing = jarak / JARAK_PESAING_IDEAL_KM * 40
    return round(skor_pop + skor_pesaing, 1)


def main():
    print("=" * 66)
    print("PEMILIHAN LOKASI GERAI BARU (analisis spasial)")
    print("=" * 66)
    print(f"Radius pasar : {RADIUS_PASAR_KM} km | jarak ideal ke pesaing : "
          f">= {JARAK_PESAING_IDEAL_KM} km")
    print("Skor = 60% jumlah penduduk dalam radius + 40% jarak ke pesaing\n")

    hasil = [analisis(k) for k in KANDIDAT]
    maks = max(h["penduduk"] for h in hasil) or 1
    for h in hasil:
        h["skor"] = beri_skor(h, maks)

    for h in sorted(hasil, key=lambda x: x["skor"], reverse=True):
        p_nama, p_jarak = h["pesaing_terdekat"]
        p_lat, p_lon = next((a, b) for n, a, b in PESAING if n == p_nama)
        print(f"{h['nama']}")
        print(f"  Koordinat          : {h['lat']}, {h['lon']}")
        print(f"  Penduduk dalam {RADIUS_PASAR_KM:.0f} km : {h['penduduk']:,} jiwa "
              f"({len(h['terjangkau'])} permukiman)")
        print(f"  Pesaing terdekat   : {p_nama}, {p_jarak:.2f} km ke arah "
              f"{arah(h['lat'], h['lon'], p_lat, p_lon)}")
        print(f"  Pesaing dalam radius: {h['pesaing_dalam']}")
        print(f"  SKOR               : {h['skor']}")
        print(f"  Peta               : https://www.google.com/maps?q="
              f"{h['lat']},{h['lon']}\n")

    terbaik = max(hasil, key=lambda x: x["skor"])
    print("-" * 66)
    print(f"REKOMENDASI: {terbaik['nama']} (skor {terbaik['skor']})")
    print("Catatan: data spasial adalah bukti pendukung keputusan, bukan")
    print("satu-satunya. Harga sewa, akses jalan, dan survei lapangan tetap")
    print("perlu dipertimbangkan sebelum keputusan akhir.")


if __name__ == "__main__":
    main()
