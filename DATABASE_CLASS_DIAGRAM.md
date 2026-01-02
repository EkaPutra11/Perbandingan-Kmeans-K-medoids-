# Class Diagram - Database Penjualan Arwana

## Visualisasi ERD (Entity Relationship Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PENJUALAN                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ • id : Integer (PK)                                                                     │
│ • tanggal_terjual : Date                                                                │
│ • kategori : String(100)                                                                │
│ • size : String(50)                                                                     │
│ • jumlah_terjual : Integer                                                              │
│ • harga_satuan : Numeric(15,0)                                                          │
│ • total_harga : Numeric(18,0)                                                           │
│ • nama_penjual : String(100)                                                            │
│ • kota_tujuan : String(100)                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────────┐
        │  KMEANS_RESULT     │  │ KMEDOIDS_RESULT    │  │ KMEANS_FINAL_RESULT  │
        ├────────────────────┤  ├────────────────────┤  ├──────────────────────┤
        │ • id : Integer (PK)│  │ • id : Integer(PK) │  │ • id : Integer (PK)  │
        │ • k_value : Integer│  │ • k_value : Integer│  │ • kmeans_result_id   │
        │ • inertia : Float  │  │ • cost : Float     │  │   (FK)               │
        │ • davies_bouldin_  │  │ • davies_bouldin_  │  │ • cluster_id : Int   │
        │   index : Float    │  │   index : Float    │  │ • kategori : String  │
        │ • n_iter : Integer │  │ • n_iter : Integer │  │ • size_range : String│
        │ • n_samples : Int  │  │ • n_samples : Int  │  │ • jumlah_terjual : I │
        │ • max_iterations   │  │ • max_iterations   │  │ • jumlah_transaksi   │
        │   : Integer        │  │   : Integer        │  │ • created_at : DateTime
        │ • random_state : I │  │ • random_state : I │  └──────────────────────┘
        │ • cluster_distrib. │  │ • medoids : JSON   │
        │   : JSON           │  │ • cluster_distrib. │
        │ • analysis_data    │  │   : JSON           │
        │   : JSON           │  │ • analysis_data    │
        │ • data_kategori_c. │  │   : JSON           │
        │   : Integer        │  │ • data_kategori_c. │
        │ • data_size_count  │  │   : Integer        │
        │   : Integer        │  │ • data_size_count  │
        │ • data_penjual_c.  │  │   : Integer        │
        │   : Integer        │  │ • data_penjual_c.  │
        │ • data_kota_count  │  │   : Integer        │
        │   : Integer        │  │ • data_kota_count  │
        │ • created_at       │  │   : Integer        │
        │   : DateTime       │  │ • created_at       │
        │                    │  │   : DateTime       │
        │ ◆ detail_clusters  │  │ ◆ detail_clusters  │
        │   (1→N)            │  │   (1→N)            │
        └────────────────────┘  └────────────────────┘
                    │                    │
                    ▼                    ▼
        ┌────────────────────────┐  ┌──────────────────────────┐
        │KMEANS_CLUSTER_DETAIL   │  │KMEDOIDS_CLUSTER_DETAIL   │
        ├────────────────────────┤  ├──────────────────────────┤
        │ • id : Integer (PK)    │  │ • id : Integer (PK)      │
        │ • kmeans_result_id (FK)│  │ • kmedoids_result_id(FK) │
        │ • cluster_id : Integer │  │ • cluster_id : Integer   │
        │ • kategori : String    │  │ • kategori : String      │
        │ • size : String        │  │ • size : String          │
        │ • jumlah_terjual : Int │  │ • jumlah_terjual : Int   │
        │ • jumlah_transaksi : I │  │ • jumlah_transaksi : Int │
        │ • total_harga : Numeric│  │ • total_harga : Numeric  │
        │ • distance_to_centroid │  │ • distance_to_medoid : F │
        │   : Float             │  │ • is_medoid : Boolean    │
        └────────────────────────┘  └──────────────────────────┘
```

---

## Deskripsi Tabel

### 1. **PENJUALAN** (Data Sumber)
Data penjualan ikan Arwana dari CV Putra Rizky Aroindo (periode 2023-2025)

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | Integer | Primary Key |
| `tanggal_terjual` | Date | Tanggal transaksi penjualan |
| `kategori` | String(100) | Kategori produk ikan |
| `size` | String(50) | Ukuran ikan |
| `jumlah_terjual` | Integer | Jumlah unit terjual |
| `harga_satuan` | Numeric(15,0) | Harga per unit |
| `total_harga` | Numeric(18,0) | Total harga transaksi |
| `nama_penjual` | String(100) | Nama penjual/sales |
| `kota_tujuan` | String(100) | Kota tujuan pengiriman |

---

### 2. **KMEANS_RESULT** (Hasil K-Means)
Menyimpan hasil eksekusi algoritma K-Means dengan berbagai nilai K

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | Integer | Primary Key |
| `k_value` | Integer | Jumlah cluster (K) |
| `inertia` | Float | Nilai inertia (sum of squared distances) |
| `davies_bouldin_index` | Float | DBI untuk evaluasi kualitas cluster |
| `n_iter` | Integer | Jumlah iterasi yang dijalankan |
| `n_samples` | Integer | Jumlah sampel data |
| `max_iterations` | Integer | Maksimum iterasi yang diatur |
| `random_state` | Integer | Seed untuk reproducibility |
| `cluster_distribution` | JSON | Distribusi data per cluster |
| `analysis_data` | JSON | Data analisis tambahan |
| `data_kategori_count` | Integer | Jumlah unique kategori |
| `data_size_count` | Integer | Jumlah unique size |
| `data_penjual_count` | Integer | Jumlah unique penjual |
| `data_kota_count` | Integer | Jumlah unique kota |
| `created_at` | DateTime | Waktu eksekusi |

---

### 3. **KMEDOIDS_RESULT** (Hasil K-Medoids)
Menyimpan hasil eksekusi algoritma K-Medoids dengan berbagai nilai K

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | Integer | Primary Key |
| `k_value` | Integer | Jumlah cluster (K) |
| `cost` | Float | Nilai cost (total distance) |
| `davies_bouldin_index` | Float | DBI untuk evaluasi kualitas cluster |
| `n_iter` | Integer | Jumlah iterasi |
| `n_samples` | Integer | Jumlah sampel data |
| `max_iterations` | Integer | Maksimum iterasi |
| `random_state` | Integer | Seed untuk reproducibility |
| `medoids` | JSON | Medoid points dari setiap cluster |
| `cluster_distribution` | JSON | Distribusi data per cluster |
| `analysis_data` | JSON | Data analisis tambahan |
| `data_kategori_count` | Integer | Jumlah unique kategori |
| `data_size_count` | Integer | Jumlah unique size |
| `data_penjual_count` | Integer | Jumlah unique penjual |
| `data_kota_count` | Integer | Jumlah unique kota |
| `created_at` | DateTime | Waktu eksekusi |

---

### 4. **KMEANS_CLUSTER_DETAIL** (Detail Cluster K-Means)
Detail anggota setiap cluster dari hasil K-Means

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | Integer | Primary Key |
| `kmeans_result_id` | Integer | Foreign Key ke KMEANS_RESULT |
| `cluster_id` | Integer | ID cluster (0, 1, 2, ...) |
| `kategori` | String(100) | Kategori produk |
| `size` | String(50) | Size range produk |
| `jumlah_terjual` | Integer | Total jumlah terjual |
| `jumlah_transaksi` | Integer | Jumlah transaksi |
| `total_harga` | Numeric(18,0) | Total harga agregat |
| `distance_to_centroid` | Float | Jarak ke pusat cluster |

---

### 5. **KMEDOIDS_CLUSTER_DETAIL** (Detail Cluster K-Medoids)
Detail anggota setiap cluster dari hasil K-Medoids

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | Integer | Primary Key |
| `kmedoids_result_id` | Integer | Foreign Key ke KMEDOIDS_RESULT |
| `cluster_id` | Integer | ID cluster (0, 1, 2, ...) |
| `kategori` | String(100) | Kategori produk |
| `size` | String(50) | Size range produk |
| `jumlah_terjual` | Integer | Total jumlah terjual |
| `jumlah_transaksi` | Integer | Jumlah transaksi |
| `total_harga` | Numeric(18,0) | Total harga agregat |
| `distance_to_medoid` | Float | Jarak ke medoid cluster |
| `is_medoid` | Boolean | Apakah ini adalah medoid point |

---

### 6. **KMEANS_FINAL_RESULT** (Hasil Final K-Means)
Hasil clustering K-Means yang sudah di-tier untuk ditampilkan di dashboard

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | Integer | Primary Key |
| `kmeans_result_id` | Integer | Foreign Key ke KMEANS_RESULT |
| `cluster_id` | Integer | ID cluster |
| `kategori` | String(100) | Kategori produk |
| `size_range` | String(50) | Range ukuran produk |
| `jumlah_terjual` | Integer | Jumlah terjual |
| `jumlah_transaksi` | Integer | Jumlah transaksi |
| `created_at` | DateTime | Waktu pembuatan |

---

## Relasi Antar Tabel

| Relasi | Dari | Ke | Tipe | Deskripsi |
|--------|------|-----|------|-----------|
| 1 | KMEANS_RESULT | KMEANS_CLUSTER_DETAIL | 1:N | Satu hasil K-Means punya banyak detail cluster |
| 2 | KMEDOIDS_RESULT | KMEDOIDS_CLUSTER_DETAIL | 1:N | Satu hasil K-Medoids punya banyak detail cluster |
| 3 | KMEANS_RESULT | KMEANS_FINAL_RESULT | 1:N | Satu hasil K-Means punya banyak final result |

---

## Alur Data

```
[PENJUALAN] 
    ↓
    ├─→ Preprocessing (Normalisasi, Agregasi per size range)
    ├─→ Feature extraction (jumlah_terjual, jumlah_transaksi)
    ↓
    ├─→ [KMEANS_RESULT] ─→ [KMEANS_CLUSTER_DETAIL] ─→ [KMEANS_FINAL_RESULT] ─→ Dashboard
    │
    └─→ [KMEDOIDS_RESULT] ─→ [KMEDOIDS_CLUSTER_DETAIL] ─→ DBI Comparison Chart
```

---

## Key Features

✅ **Dual Clustering Methods**: Mendukung K-Means dan K-Medoids untuk perbandingan  
✅ **Davies-Bouldin Index**: Metrik evaluasi kualitas cluster  
✅ **JSON Storage**: Fleksibilitas untuk menyimpan data kompleks  
✅ **Timestamp Tracking**: Audit trail untuk setiap eksekusi  
✅ **Cascade Delete**: Integritas relasional terjaga  
✅ **Tier Classification**: Kategori penjualan (Terlaris, Sedang, Kurang Laris)

