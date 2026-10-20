"""
Studi Kasus 4 - Introduction to Machine Learning

Kasus : Memprediksi faktur yang akan TERLAMBAT dibayar (supervised learning,
        klasifikasi biner) memakai regresi logistik yang dibuat dari nol.
Isi   : pembagian data latih/uji, standardisasi, pelatihan gradient descent,
        evaluasi (akurasi, precision, recall, F1, confusion matrix), jebakan
        akurasi pada data tidak seimbang, dan demo data leakage.
Data  : dibangkitkan secara acak dengan seed tetap (fiktif).
Hanya memakai library bawaan Python.
"""

import math
import random

FITUR = ["rasio_tunggakan", "rata2_hari_telat_lalu", "nilai_faktur_juta",
         "lama_langganan_bulan"]


def buat_data(n=900, seed=5):
    rnd = random.Random(seed)
    data = []
    for _ in range(n):
        rasio = min(1.0, max(0.0, rnd.betavariate(1.5, 5)))
        telat_lalu = max(0.0, rnd.gauss(6 * rasio * 3, 3))
        nilai = max(1.0, rnd.gauss(20, 9))
        lama = max(1.0, rnd.gauss(24, 12))
        logit = (-4.4 + 3.4 * rasio + 0.16 * telat_lalu + 0.025 * nilai
                 - 0.02 * lama)
        p = 1 / (1 + math.exp(-logit))
        telat = 1 if rnd.random() < p else 0
        data.append(([rasio, telat_lalu, nilai, lama], telat))
    return data


def bagi(data, rasio_latih=0.7, seed=1):
    data = data[:]
    random.Random(seed).shuffle(data)
    k = int(len(data) * rasio_latih)
    return data[:k], data[k:]


def standardisasi(latih, uji):
    n_fitur = len(latih[0][0])
    rata = [sum(x[j] for x, _ in latih) / len(latih) for j in range(n_fitur)]
    std = []
    for j in range(n_fitur):
        v = sum((x[j] - rata[j]) ** 2 for x, _ in latih) / len(latih)
        std.append(math.sqrt(v) or 1.0)

    def ubah(d):
        return [([(x[j] - rata[j]) / std[j] for j in range(n_fitur)], y)
                for x, y in d]
    return ubah(latih), ubah(uji)


def sigmoid(z):
    z = max(-30, min(30, z))
    return 1 / (1 + math.exp(-z))


def latih_model(latih, epoch=600, lr=0.2):
    n_fitur = len(latih[0][0])
    w = [0.0] * n_fitur
    b = 0.0
    n = len(latih)
    for _ in range(epoch):
        gw = [0.0] * n_fitur
        gb = 0.0
        for x, y in latih:
            err = sigmoid(sum(wi * xi for wi, xi in zip(w, x)) + b) - y
            for j in range(n_fitur):
                gw[j] += err * x[j]
            gb += err
        w = [wi - lr * g / n for wi, g in zip(w, gw)]
        b -= lr * gb / n
    return w, b


def prediksi_proba(model, x):
    w, b = model
    return sigmoid(sum(wi * xi for wi, xi in zip(w, x)) + b)


def evaluasi(model, data, ambang=0.5):
    tp = fp = tn = fn = 0
    for x, y in data:
        pred = 1 if prediksi_proba(model, x) >= ambang else 0
        if pred and y:
            tp += 1
        elif pred and not y:
            fp += 1
        elif not pred and not y:
            tn += 1
        else:
            fn += 1
    total = tp + fp + tn + fn
    akurasi = (tp + tn) / total
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "akurasi": akurasi,
            "precision": precision, "recall": recall, "f1": f1}


def cetak(judul, m):
    print(f"\n{judul}")
    print(f"  Confusion matrix : TP={m['tp']}  FP={m['fp']}  "
          f"FN={m['fn']}  TN={m['tn']}")
    print(f"  Akurasi {m['akurasi'] * 100:5.1f}% | Precision "
          f"{m['precision'] * 100:5.1f}% | Recall {m['recall'] * 100:5.1f}% | "
          f"F1 {m['f1'] * 100:5.1f}%")


def main():
    print("=" * 64)
    print("PREDIKSI KETERLAMBATAN PEMBAYARAN FAKTUR (regresi logistik)")
    print("=" * 64)

    data = buat_data()
    latih, uji = bagi(data)
    pos = sum(y for _, y in data)
    print(f"Total data {len(data)} | terlambat {pos} ({pos / len(data) * 100:.1f}%)"
          f" | tepat waktu {len(data) - pos}")
    print(f"Data latih {len(latih)} | data uji {len(uji)}")
    print("Fitur:", ", ".join(FITUR))

    latih_s, uji_s = standardisasi(latih, uji)
    model = latih_model(latih_s)

    print("\nBobot hasil belajar (data standar):")
    for nama, w in zip(FITUR, model[0]):
        print(f"  {nama:<24}{w:+.3f}")

    # Baseline: selalu menebak "tepat waktu"
    tebak_nol = sum(1 for _, y in uji_s if y == 0) / len(uji_s)
    print(f"\nBASELINE 'selalu tepat waktu' : akurasi {tebak_nol * 100:.1f}%, "
          "recall 0.0%")
    print("-> Akurasi tinggi belum berarti model berguna pada data tidak seimbang.")

    cetak("MODEL @ ambang 0.5", evaluasi(model, uji_s, 0.5))
    cetak("MODEL @ ambang 0.3 (lebih peka terhadap kasus terlambat)",
          evaluasi(model, uji_s, 0.3))

    # Demo data leakage: fitur dari masa depan
    print("\n--- DEMO DATA LEAKAGE ---")
    bocor_latih = [(x + [float(y) + random.Random(i).gauss(0, 0.05)], y)
                   for i, (x, y) in enumerate(latih)]
    bocor_uji = [(x + [float(y) + random.Random(i + 9999).gauss(0, 0.05)], y)
                 for i, (x, y) in enumerate(uji)]
    bl, bu = standardisasi(bocor_latih, bocor_uji)
    model_bocor = latih_model(bl)
    cetak("Model dengan fitur 'status pembayaran aktual' (informasi masa depan)",
          evaluasi(model_bocor, bu, 0.5))
    print("Hasil tampak nyaris sempurna karena model 'mengintip' jawaban.")
    print("Di dunia nyata fitur itu belum diketahui saat prediksi dibuat.")

    # Prediksi data baru
    print("\n--- PREDIKSI FAKTUR BARU ---")
    baru = [("Pelanggan lancar", [0.05, 0.5, 10, 40]),
            ("Pelanggan berisiko", [0.60, 12, 35, 6])]
    # standardisasi memakai statistik data latih
    n_fitur = len(FITUR)
    rata = [sum(x[j] for x, _ in latih) / len(latih) for j in range(n_fitur)]
    std = [math.sqrt(sum((x[j] - rata[j]) ** 2 for x, _ in latih) / len(latih))
           for j in range(n_fitur)]
    for nama, x in baru:
        xs = [(x[j] - rata[j]) / std[j] for j in range(n_fitur)]
        p = prediksi_proba(model, xs)
        print(f"  {nama:<20} peluang terlambat {p * 100:5.1f}% -> "
              f"{'WASPADA' if p >= 0.3 else 'aman'}")
    print("\nCatatan: model belajar dari data masa lalu; keputusan kredit tetap")
    print("perlu pengawasan manusia dan pemantauan setelah dipakai.")


if __name__ == "__main__":
    main()
