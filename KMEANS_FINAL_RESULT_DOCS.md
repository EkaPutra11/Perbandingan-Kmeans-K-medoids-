# K-MEANS FINAL RESULT - DOKUMENTASI

## Overview

Tabel `kmeans_final_result` menyimpan hasil clustering K-Means terbaik (k=3) yang menang dalam perbandingan dengan K-Medoids.

## Struktur Tabel

```sql
CREATE TABLE kmeans_final_result (
    id INT PRIMARY KEY AUTO_INCREMENT,
    kmeans_result_id INT NOT NULL,
    cluster_id INT NOT NULL,
    kategori VARCHAR(100),
    size_range VARCHAR(50),
    jumlah_terjual INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kmeans_result_id) REFERENCES kmeans_result(id)
);
```

## Kolom Deskripsi

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | INT | Primary key, auto increment |
| `kmeans_result_id` | INT | Foreign key ke tabel kmeans_result |
| `cluster_id` | INT | ID cluster (0, 1, 2 untuk k=3) |
| `kategori` | VARCHAR(100) | Kategori ikan arwana |
| `size_range` | VARCHAR(50) | Rentang ukuran (misal: 10-14 cm) |
| `jumlah_terjual` | INT | Jumlah ikan terjual |
| `created_at` | DATETIME | Timestamp pembuatan record |

## Hasil K-Means Terbaik

### Metrics
- **K Value**: 3 cluster
- **Davies-Bouldin Index**: 0.4813 (sangat baik, lebih rendah = lebih baik)
- **Inertia**: 40.2217
- **Iterasi**: 2 (converged sangat cepat!)
- **Total Samples**: 90 data agregasi
- **Total Records**: 90 records

### Distribusi Cluster

| Cluster | Jumlah Records | Total Terjual | Karakteristik |
|---------|----------------|---------------|---------------|
| **Cluster 0** | 71 samples | 1,429 | Volume rendah, beragam kategori & ukuran |
| **Cluster 1** | 18 samples | 2,939 | Volume menengah-tinggi, mayoritas Standard |
| **Cluster 2** | 1 sample | 1,372 | Volume sangat tinggi, Standard 10-14 cm |

**Total**: 90 samples, 5,740 jumlah terjual

## Interpretasi Cluster

### 🔵 Cluster 0: "Low Volume, Diverse Products"
- **71 samples** (79% dari data)
- **1,429 total terjual** (25% dari total)
- **Karakteristik**:
  - Berbagai kategori: Dayung Setan, King, Mata Panda, Semi King, Sepauk, Shortbody, Slayer, Special, Sumo
  - Berbagai ukuran dari 15-64 cm
  - Volume per item relatif rendah (rata-rata ~20 unit)
- **Insight**: Produk niche, varietas tinggi tapi volume rendah

### 🟢 Cluster 1: "Medium-High Volume, Mainstream"
- **18 samples** (20% dari data)
- **2,939 total terjual** (51% dari total)
- **Karakteristik**:
  - Didominasi kategori **Standard** (13 dari 18 samples)
  - Ukuran populer: 20-60 cm
  - Volume per item menengah-tinggi (rata-rata ~163 unit)
  - Standard 25-29 cm: **567 terjual** (tertinggi di cluster ini)
- **Insight**: Produk mainstream, volume stabil, permintaan tinggi

### 🔴 Cluster 2: "Ultra High Volume, Best Seller"
- **1 sample** (1% dari data)
- **1,372 total terjual** (24% dari total)
- **Karakteristik**:
  - **Hanya 1 produk**: Standard 10-14 cm
  - Volume **sangat tinggi** (1,372 unit!)
  - Outlier yang jelas terpisah
- **Insight**: Best seller absolut, ukuran kecil (starter fish), harga terjangkau

## Kenapa K-Means Menang?

### Perbandingan K-Means vs K-Medoids

| Metrik | K-Means | K-Medoids | Pemenang |
|--------|---------|-----------|----------|
| **Davies-Bouldin Index** | **0.4813** | 1.0047 | ✅ K-Means |
| **Convergence Speed** | **2 iterasi** | 8 iterasi | ✅ K-Means |
| **Quality** | Lebih baik | Kurang baik | ✅ K-Means |
| **Efisiensi** | Sangat cepat | Lebih lambat | ✅ K-Means |

### Alasan Kemenangan K-Means:
1. ✅ **DBI lebih rendah** (0.4813 vs 1.0047) → Cluster lebih compact dan terpisah
2. ✅ **Converge sangat cepat** (2 iterasi vs 8 iterasi)
3. ✅ **K-Means++ initialization** memberikan starting point optimal
4. ✅ **Early stopping** dengan tolerance detection yang tepat
5. ✅ Dataset cocok untuk K-Means (distribusi numerik yang smooth)

## File Scripts

### 1. `save_final_result.py`
Script untuk membuat tabel dan menyimpan hasil terbaik K-Means.

```bash
.\env\Scripts\python.exe save_final_result.py
```

**Output**: Membuat tabel `kmeans_final_result` dan menyimpan 90 records.

### 2. `view_final_result.py`
Script untuk melihat hasil final dari database dengan detail per cluster.

```bash
.\env\Scripts\python.exe view_final_result.py
```

**Output**: Menampilkan semua data dikelompokkan per cluster.

### 3. `queries_final_result.sql`
File SQL queries untuk analisis database.

## Fungsi Python

### Di `app/models.py`:

```python
class KMeansFinalResult(db.Model):
    """Model untuk hasil final K-Means terbaik"""
    __tablename__ = 'kmeans_final_result'
    
    id = db.Column(db.Integer, primary_key=True)
    kmeans_result_id = db.Column(db.Integer, db.ForeignKey('kmeans_result.id'))
    cluster_id = db.Column(db.Integer, nullable=False)
    kategori = db.Column(db.String(100))
    size_range = db.Column(db.String(50))
    jumlah_terjual = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Di `app/processing_kmeans.py`:

```python
def save_kmeans_final_result(kmeans_result_id):
    """Simpan hasil final K-Means ke tabel kmeans_final_result"""
    # Menghapus data lama dan menyimpan data baru
    
def get_kmeans_final_results():
    """Ambil semua hasil final dari database"""
    # Return list of dictionaries
```

## Query Examples

### Lihat semua data:
```sql
SELECT * FROM kmeans_final_result 
ORDER BY cluster_id, kategori, size_range;
```

### Summary per cluster:
```sql
SELECT 
    cluster_id,
    COUNT(*) as total_records,
    SUM(jumlah_terjual) as total_terjual,
    AVG(jumlah_terjual) as avg_terjual
FROM kmeans_final_result
GROUP BY cluster_id;
```

### Top 10 produk terlaris:
```sql
SELECT cluster_id, kategori, size_range, jumlah_terjual
FROM kmeans_final_result
ORDER BY jumlah_terjual DESC
LIMIT 10;
```

## Business Insights

### Rekomendasi Bisnis:

1. **Cluster 2 (Best Seller)**:
   - Focus: Standard 10-14 cm adalah top performer
   - Action: Pastikan stok selalu tersedia, ini adalah revenue driver utama
   - Target: Pemula/starter market

2. **Cluster 1 (Mainstream)**:
   - Focus: Standard ukuran 15-60 cm, volume stabil
   - Action: Maintain inventory, predictable demand
   - Target: Market menengah

3. **Cluster 0 (Niche)**:
   - Focus: Produk premium dan varietas (Dayung Setan, King, dll)
   - Action: Stock management hati-hati, demand lebih rendah tapi margin mungkin lebih tinggi
   - Target: Kolektor dan enthusiast

### Key Findings:

- 📊 **51% penjualan** dari hanya **20% produk** (Cluster 1)
- 🏆 **24% penjualan** dari **1 produk** saja (Cluster 2 - Standard 10-14cm)
- 🎯 **Standard 25-29 cm** = produk volume tertinggi di cluster mainstream (567 unit)
- 📈 Fokus pada **Standard size 10-60 cm** untuk **75% total revenue**

## Maintenance

### Update hasil baru:
```python
from app.processing_kmeans import save_kmeans_final_result

# Setelah running K-Means baru
kmeans_result_id = 123  # ID hasil baru
save_kmeans_final_result(kmeans_result_id)
```

### Clear dan re-populate:
Script `save_final_result.py` otomatis menghapus data lama sebelum menyimpan baru.

---

**Created**: December 10, 2025  
**Status**: ✅ Production Ready  
**Records**: 90 samples  
**Algorithm**: K-Means (k=3, DBI=0.4813)
