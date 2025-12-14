# DOKUMENTASI PERUBAHAN - SEPARATED CLUSTERING LOGIC

## Tanggal: 14 Desember 2025

## Tujuan
Memperbaiki bias clustering dengan memproses Standard dan Non-Standard TERPISAH secara internal, TANPA mengubah tampilan UI atau menghapus kode existing.

## Masalah Sebelumnya
- Clustering bias karena kategori Standard mendominasi dengan volume jauh lebih besar
- Non-Standard tidak mendapat penilaian cluster yang adil
- DBI dihitung dari semua data digabung, tidak merefleksikan performa per kategori

## Solusi yang Diimplementasikan

### File yang Dimodifikasi:

#### 1. `app/processing_kmeans.py` - Fungsi `process_kmeans_manual()`
**Perubahan:**
- ✅ Data diagregasi berdasarkan (kategori, size_range) dengan interval 5cm
- ✅ Dataframe dipisah menjadi `df_standard` dan `df_non_standard`
- ✅ Masing-masing subset dinormalisasi TERPISAH
- ✅ Clustering K-Means dijalankan TERPISAH untuk setiap subset
- ✅ DBI dihitung TERPISAH: `dbi_standard` dan `dbi_non_standard`
- ✅ DBI combined menggunakan weighted average
- ✅ Output tetap kompatibel dengan routes dan UI existing
- ✅ Iterasi dan logging tetap muncul

**Fitur Clustering:**
- `total_jumlah_terjual` (SUM dari aggregation)
- `total_harga` (SUM dari aggregation)

#### 2. `app/processing_kmedoids.py` - Fungsi `process_kmedoids_manual()`
**Perubahan:**
- ✅ Logika identik dengan K-Means
- ✅ Menggunakan K-Medoids algorithm untuk masing-masing subset
- ✅ DBI dihitung TERPISAH
- ✅ Cost dihitung sebagai total dari kedua subset
- ✅ Output tetap kompatibel dengan routes dan UI existing

### Yang TIDAK Berubah:
- ❌ Routes Flask (`app/routes.py`)
- ❌ Template HTML (semua file di `app/templates/`)
- ❌ JavaScript files (semua file di `app/static/js/`)
- ❌ CSS styles (semua file di `app/static/css/`)
- ❌ Format output hasil clustering
- ❌ Display iterasi per langkah
- ❌ Grafik dan tabel
- ❌ Struktur database

## Hasil Testing

### K-Means (Separated Processing):
```
Total records: 90 (Standard: 11, Non-Standard: 79)

[Standard]
- DBI: 0.4121
- Inertia: 2.9050
- Iterations: 2

[Non-Standard]
- DBI: 0.5004
- Inertia: 19.8856
- Iterations: 3

[Combined]
- DBI: 0.4896 (weighted average)
- Total Inertia: 22.7906
```

### K-Medoids (Separated Processing):
```
Total records: 90 (Standard: 11, Non-Standard: 79)

[Standard]
- DBI: 0.3715
- Cost: 7.0853
- Iterations: 3

[Non-Standard]
- DBI: 0.6893
- Cost: 49.1476
- Iterations: 4

[Combined]
- DBI: 0.6505 (weighted average)
- Total Cost: 56.2329
```

### Perbandingan:
- **K-Means DBI (Combined):** 0.4896 ✓ (LEBIH BAIK)
- **K-Medoids DBI (Combined):** 0.6505
- **Winner:** K-Means

## Keuntungan Logika Baru

1. ✅ **Tidak ada bias kategori** - Standard dan Non-Standard diproses terpisah
2. ✅ **Normalisasi independen** - Setiap subset dinormalisasi dengan mean/std sendiri
3. ✅ **DBI lebih akurat** - Mencerminkan performa clustering per kategori
4. ✅ **Label cluster adil** - Terlaris/Sedang/Kurang Laris dibandingkan dalam kelompoknya
5. ✅ **Transparansi** - DBI standard dan non-standard terlihat jelas
6. ✅ **Backward compatible** - Output format tetap sama, tidak break existing code
7. ✅ **Iterasi tetap muncul** - Logging dan print iterasi tidak hilang

## Cara Menggunakan

### Test dari terminal:
```bash
.\env\Scripts\python.exe test_separated_logic.py
```

### Jalankan aplikasi normal:
```bash
.\env\Scripts\python.exe app.py
```

Aplikasi akan otomatis menggunakan logika baru tanpa perubahan apapun di UI atau routes.

## Return Value Baru

Fungsi `process_kmeans_manual()` dan `process_kmedoids_manual()` sekarang mengembalikan:

```python
{
    'kmeans': kmeans_object,  # atau 'kmedoids'
    'labels': array,
    'inertia': float,  # atau 'cost' untuk kmedoids
    'davies_bouldin': float,  # DBI combined (weighted average)
    'davies_bouldin_standard': float,  # DBI khusus Standard
    'davies_bouldin_non_standard': float,  # DBI khusus Non-Standard
    'n_iter': int,
    'n_samples': int,
    'centroids': array,  # atau 'medoids'
    'data': dataframe,
    'data_aggregated': dataframe,
    'analysis': dict,
    'X_mean': array,
    'X_std': array,
    'X_normalized': array
}
```

Key baru yang ditambahkan:
- `davies_bouldin_standard`
- `davies_bouldin_non_standard`

## Status
✅ **SELESAI** - Implementasi berhasil, semua test passed
✅ **NO BREAKING CHANGES** - UI dan routes tetap berfungsi normal
✅ **CLUSTERING BIAS FIXED** - Standard dan Non-Standard diproses adil
