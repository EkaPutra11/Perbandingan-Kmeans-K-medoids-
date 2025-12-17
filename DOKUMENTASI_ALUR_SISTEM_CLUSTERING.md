# 📘 DOKUMENTASI LENGKAP SISTEM CLUSTERING ARWANA SALES
## Alur Kerja, Cara Kerja, dan Proses Detail

**Tanggal Update:** 14 Desember 2025  
**Versi:** 2.0 (Dengan Percentile-Based Tier Assignment)

---

## 📋 DAFTAR ISI

1. [Arsitektur Sistem](#arsitektur-sistem)
2. [Alur Kerja Keseluruhan](#alur-kerja-keseluruhan)
3. [Proses K-Means Detail](#proses-k-means-detail)
4. [Proses K-Medoids Detail](#proses-k-medoids-detail)
5. [Percentile-Based Tier Assignment](#percentile-based-tier-assignment)
6. [Penyimpanan Database](#penyimpanan-database)
7. [Tampilan Dashboard](#tampilan-dashboard)
8. [Perbedaan Versi Lama vs Baru](#perbedaan-versi-lama-vs-baru)

---

## 1. ARSITEKTUR SISTEM

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK WEB APPLICATION                       │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼────┐        ┌─────▼─────┐       ┌─────▼─────┐
    │  MySQL  │        │  Routes   │       │ Templates │
    │ Database│        │(routes.py)│       │   (HTML)  │
    └─────────┘        └───────────┘       └───────────┘
         │                    │                    │
         │              ┌─────▼─────┐             │
         │              │Processing │             │
         │              │  Modules  │             │
         │              └───────────┘             │
         │                    │                   │
         │       ┌────────────┼────────────┐      │
         │       │            │            │      │
    ┌────▼───────▼──┐  ┌─────▼─────┐  ┌──▼──────▼────┐
    │processing_    │  │processing_│  │  JavaScript  │
    │  kmeans.py    │  │kmedoids.py│  │  (Frontend)  │
    └───────────────┘  └───────────┘  └──────────────┘
```

### File-file Utama:
- `app.py` - Entry point aplikasi
- `app/routes.py` - Routing dan API endpoints
- `app/processing_kmeans.py` - Algoritma K-Means
- `app/processing_kmedoids.py` - Algoritma K-Medoids
- `app/models.py` - Database models (SQLAlchemy)
- `app/templates/` - HTML templates
- `app/static/js/` - JavaScript untuk interaksi UI

---

## 2. ALUR KERJA KESELURUHAN

### 2.1 Flow Diagram

```
START
  │
  ├─► User buka halaman Preprocessing K-Means/K-Medoids
  │
  ├─► User set parameter K (jumlah cluster, default: 3)
  │
  ├─► User klik "Jalankan Clustering"
  │
  ├─► BACKEND PROCESSING:
  │   │
  │   ├─► 1. Ambil data dari database (MySQL)
  │   │      SELECT * FROM penjualan
  │   │      Total: 1358 records
  │   │
  │   ├─► 2. Agregasi data per kategori + size range
  │   │      Grouping by (kategori, size_range)
  │   │      1358 records → ~90 aggregated records
  │   │
  │   ├─► 3. Ekstrak features: [jumlah_terjual, total_harga]
  │   │
  │   ├─► 4. Normalisasi data (Z-score)
  │   │      X_normalized = (X - mean) / std
  │   │
  │   ├─► 5. Run clustering algorithm
  │   │      ├─► K-Means: Initialize centroids, iterate
  │   │      └─► K-Medoids: Initialize medoids, swap
  │   │      Output: cluster_labels [0, 1, 2, 1, 0, ...]
  │   │
  │   ├─► 6. ✨ PERCENTILE-BASED TIER ASSIGNMENT ✨
  │   │      ├─► Calculate performance_score per data
  │   │      ├─► Sort by score, apply percentile thresholds
  │   │      └─► Output: tier_labels [0, 1, 2, 0, ...]
  │   │           0 = Terlaris (Top 30%)
  │   │           1 = Sedang (Middle 40%)
  │   │           2 = Kurang Laris (Bottom 30%)
  │   │
  │   ├─► 7. Calculate Davies-Bouldin Index (DBI)
  │   │      Using cluster_labels (not tier_labels)
  │   │
  │   ├─► 8. Create analysis output (grouping Standard/Non-Standard)
  │   │
  │   ├─► 9. Save to database
  │   │      ├─► kmeans_result / kmedoids_result
  │   │      ├─► kmeans_cluster_detail / kmedoids_cluster_detail
  │   │      └─► kmeans_final_result (untuk dashboard)
  │   │
  │   └─► 10. Return JSON response ke frontend
  │
  ├─► FRONTEND RENDERING:
  │   │
  │   ├─► Display metrics (Inertia/Cost, DBI)
  │   ├─► Display iteration details
  │   ├─► Display final results table
  │   └─► Display summary stats (30/40/30 distribution)
  │
  └─► END
```

---

## 3. PROSES K-MEANS DETAIL

### 3.1 Function: `process_kmeans_manual(k=3)`

**Location:** `app/processing_kmeans.py`, line ~390

#### Langkah-langkah Eksekusi:

```python
def process_kmeans_manual(k=3):
    """
    Main function untuk menjalankan K-Means clustering dengan 
    percentile-based tier assignment
    """
```

#### STEP 1: Data Retrieval
```python
# Query database
data = Penjualan.query.all()

# Convert ke DataFrame
df = pd.DataFrame([{
    'id': d.id,
    'kategori': d.kategori,
    'size': d.size,
    'jumlah_terjual': d.jumlah_terjual,
    'total_harga': d.total_harga,
    # ... kolom lainnya
} for d in data])

# Output: DataFrame dengan 1358 rows
```

**Contoh data mentah:**
| id | kategori | size | jumlah_terjual | total_harga |
|----|----------|------|----------------|-------------|
| 1  | Standard | 15 cm| 2              | 100000      |
| 2  | Standard | 15 cm| 3              | 150000      |
| 3  | King     | 20 cm| 5              | 250000      |

---

#### STEP 2: Data Aggregation

```python
df_aggregated = aggregate_data_by_size_range(df)
```

**Proses di `aggregate_data_by_size_range()`:**

```python
def aggregate_data_by_size_range(df):
    # 1. Convert size ke size_range (grouping 5cm)
    df['size_range'] = df['size'].apply(get_size_range)
    #    "15 cm" → "15-19 cm"
    #    "23 cm" → "20-24 cm"
    
    # 2. Remove Unknown
    df = df[df['size_range'] != 'Unknown'].copy()
    
    # 3. Group by kategori + size_range, SUM values
    aggregated = df.groupby(['kategori', 'size_range']).agg({
        'jumlah_terjual': 'sum',
        'total_harga': 'sum'
    }).reset_index()
    
    return aggregated
```

**Contoh hasil agregasi:** 
| kategori | size_range | jumlah_terjual | total_harga |
|----------|------------|----------------|-------------|
| Standard | 15-19 cm   | 331            | 16550000    |
| Standard | 20-24 cm   | 304            | 15200000    |
| King     | 20-24 cm   | 43             | 2150000     |

**Hasil:** 1358 records → ~90 aggregated records

---

#### STEP 3: Feature Extraction & Normalization

```python
# Extract 2 features
X = df_aggregated[['jumlah_terjual', 'total_harga']].values
# X shape: (90, 2)

# Calculate mean and std
X_mean = X.mean(axis=0)  # [mean_jumlah, mean_harga]
X_std = X.std(axis=0)    # [std_jumlah, std_harga]
 

---

#### STEP 6: Calculate Davies-Bouldin Index

```python
davies_bouldin = davies_bouldin_index_manual(X_normalized, cluster_labels, kmeans.centroids)
```

**PENTING:** DBI menggunakan `cluster_labels` (hasil clustering asli), BUKAN `tier_labels`

**Algoritma DBI:**
```python
def davies_bouldin_index_manual(X, labels, centroids):
    # 1. Calculate average distance within each cluster
    S = []
    for i in range(k):
        cluster_points = X[labels == i]
        distances = np.linalg.norm(cluster_points - centroids[i], axis=1)
        S.append(distances.mean())
    
    # 2. Calculate DBI
    db_sum = 0
    for i in range(k):
        max_ratio = 0
        for j in range(k):
            if i != j:
                centroid_distance = np.linalg.norm(centroids[i] - centroids[j])
                ratio = (S[i] + S[j]) / centroid_distance
                max_ratio = max(max_ratio, ratio)
        db_sum += max_ratio
    
    return db_sum / k
```

**Interpretasi DBI:**
- DBI rendah (< 1.0) = Clustering bagus (compact & well-separated)
- DBI tinggi (> 2.0) = Clustering kurang baik (overlapping)

---

#### STEP 7: Create Analysis Output

```python
analysis = analyze_clustering_results_aggregated(df_aggregated, labels, kmeans.centroids)
```

**Fungsi `analyze_clustering_results_aggregated()`:**

```python
def analyze_clustering_results_aggregated(df_aggregated, labels, centroids):
    analysis = {
        'standard': {},
        'non_standard': {}
    }
    
    # Map tier labels (integer 0,1,2) ke tier names
    tier_names_map = {
        0: 'terlaris',
        1: 'sedang',
        2: 'kurang_laris'
    }
    
    # Process setiap aggregated row
    for i, (idx, row) in enumerate(df_aggregated.iterrows()):
        tier_id = int(labels[i])  # 0, 1, atau 2
        tier_normalized = tier_names_map[tier_id]
        cluster_id = tier_id  # Untuk frontend
        
        kategori = row['kategori']
        size_range = row['size_range']
        
        # Determine category type
        category_type = 'standard' if kategori.lower() in ['standar', 'standard'] else 'non_standard'
        
        # Create unique key
        unique_key = f"{kategori}_{size_range}"
        
        # Store in analysis dict
        analysis[category_type][unique_key] = {
            'kategori': kategori,
            'size_range': size_range,
            'total_terjual': row['jumlah_terjual'],
            'total_harga': row['total_harga'],
            'tier': tier_normalized,      # 'terlaris', 'sedang', 'kurang_laris'
            'cluster_id': cluster_id,     # 0, 1, 2 (untuk frontend)
            'dominant_cluster': cluster_id
        }
    
    return analysis
```

**Contoh output analysis:**
```json
{
  "standard": {
    "Standard_20-24 cm": {
      "kategori": "Standard",
      "size_range": "20-24 cm",
      "total_terjual": 304,
      "total_harga": 15200000,
      "tier": "sedang",
      "cluster_id": 1,
      "dominant_cluster": 1
    }
  },
  "non_standard": {
    "King_20-24 cm": {
      "kategori": "King",
      "size_range": "20-24 cm",
      "total_terjual": 43,
      "total_harga": 2150000,
      "tier": "kurang_laris",
      "cluster_id": 2,
      "dominant_cluster": 2
    }
  }
}
```

---

#### STEP 8: Return Result

```python
return {
    'kmeans': kmeans,
    'labels': labels,                    # tier_labels (0,1,2)
    'cluster_labels': cluster_labels,    # cluster asli (untuk DBI)
    'inertia': float(kmeans.inertia),
    'davies_bouldin': float(davies_bouldin),
    'n_iter': kmeans.n_iter,
    'n_samples': len(df_aggregated),
    'centroids': kmeans.centroids,
    'data': df,                          # Data original
    'data_aggregated': df_aggregated,    # Data aggregated + kolom baru
    'analysis': analysis,
    'X_mean': X_mean,
    'X_std': X_std,
    'X_normalized': X_normalized
}
```

---

## 4. PROSES K-MEDOIDS DETAIL

### 4.1 Function: `process_kmedoids_manual(k=3)`

**Location:** `app/processing_kmedoids.py`, line ~420

K-Medoids memiliki alur yang SAMA dengan K-Means, perbedaan utama hanya di algoritma clustering:

#### Perbedaan Utama K-Medoids vs K-Means:

| Aspek | K-Means | K-Medoids |
|-------|---------|-----------|
| **Representasi Cluster** | Centroid (titik virtual) | Medoid (actual data point) |
| **Distance Metric** | Euclidean (L2) | Manhattan (L1) |
| **Update Method** | Hitung rata-rata | Swap medoid dengan non-medoid |
| **Cost Function** | Sum of Squared Distances | Sum of Absolute Distances |
| **Robustness** | Sensitif terhadap outlier | Lebih robust terhadap outlier |

#### Algoritma K-Medoids (class `KMedoidsManual`):

```python
def fit(self, X):
    # 1. INITIALIZATION
    #    Pilih k medoids strategis (bukan random)
    self.distance_matrix = self._compute_distance_matrix(X)
    self.medoids = self._medoid_initialization(X, self.distance_matrix)
    
    # Iterasi hingga konvergen
    for iteration in range(self.max_iterations):
        
        # 2. ASSIGNMENT STEP
        #    Assign setiap point ke medoid terdekat (Manhattan distance)
        distances = self.distance_matrix[self.medoids].T
        self.labels = np.argmin(distances, axis=1)
        
        # 3. CALCULATE CURRENT COST
        current_cost = np.sum(np.min(distances, axis=1))
        
        # 4. SWAP STEP (berbeda dari K-Means!)
        improved = False
        non_medoids = [i for i in range(n_samples) if i not in self.medoids]
        
        # Coba swap random medoid dengan non-medoid
        for new_medoid in random_sample(non_medoids):
            for i, old_medoid in enumerate(self.medoids):
                # Try swap
                self.medoids[i] = new_medoid
                distances = self.distance_matrix[self.medoids].T
                new_cost = np.sum(np.min(distances, axis=1))
                
                # Keep if better, revert if worse
                if new_cost < current_cost:
                    current_cost = new_cost
                    improved = True
                    break
                else:
                    self.medoids[i] = old_medoid
        
        # 5. CONVERGENCE CHECK
        if not improved:
            print(f"Converged at iteration {iteration}")
            break
    
    self.cost = current_cost
```

**Contoh swap:**
```
Iteration 1:
  Medoids: [5, 23, 67] (index data points)
  Cost: 145.6
  
  Try swap medoid 5 → 12:
    New cost: 138.2  ✓ Better! Keep it
    Medoids: [12, 23, 67]
  
Iteration 2:
  Try swap medoid 23 → 45:
    New cost: 142.1  ✗ Worse! Revert
    Medoids: [12, 23, 67]  (unchanged)
  
  No improvement → CONVERGED
```

**STEP 5-8: SAMA dengan K-Means**
- Percentile-based tier assignment
- Davies-Bouldin Index calculation
- Analysis creation
- Return result

---

## 5. PERCENTILE-BASED TIER ASSIGNMENT

### 5.1 Mengapa Perlu Percentile?

**MASALAH DENGAN CLUSTER-BASED LABELING:**

```
Data distribution: 85% produk terjual 0-5 unit (highly skewed)

K-Means/K-Medoids clustering:
  Cluster 0: 5 data (high performers)
  Cluster 1: 20 data (mid performers)
  Cluster 2: 65 data (low performers)

Jika label berdasarkan cluster ID:
  C0 = Terlaris → 5 produk (5.5%)   ✗
  C1 = Sedang → 20 produk (22%)     ✗
  C2 = Kurang Laris → 65 produk (72%) ✗

TIDAK MASUK AKAL UNTUK BISNIS!
```

**SOLUSI: PERCENTILE-BASED TIER ASSIGNMENT**

```
Ignore cluster ID, rank by performance_score:

Sort all products by score → Apply percentile thresholds:
  P70-P100 (Top 30%) → Terlaris
  P30-P70 (Middle 40%) → Sedang
  P0-P30 (Bottom 30%) → Kurang Laris

Result:
  Terlaris: 27 produk (30%)   ✓
  Sedang: 36 produk (40%)     ✓
  Kurang Laris: 27 produk (30%) ✓

DISTRIBUSI SEIMBANG DAN MASUK AKAL!
```

### 5.2 Performance Score Formula

```python
performance_score = 0.6 * jumlah_norm + 0.4 * harga_norm
```

**Rationale:**
- **60% bobot untuk jumlah_terjual** - Volume penjualan adalah indikator utama popularitas
- **40% bobot untuk total_harga** - Revenue juga penting, tapi tidak dominant
- Normalisasi 0-1 memastikan kedua feature setara

**Alternatif formula yang bisa digunakan:**
```python
# Equal weight
performance_score = 0.5 * jumlah_norm + 0.5 * harga_norm

# Revenue priority
performance_score = 0.3 * jumlah_norm + 0.7 * harga_norm

# Hybrid (average + price consideration)
performance_score = jumlah_norm * (1 + 0.2 * log(avg_price_per_unit))
```

### 5.3 Kolom Analytical Tambahan

**1. avg_price_per_unit**
```python
avg_price_per_unit = total_harga / jumlah_terjual
```
- Menunjukkan harga rata-rata per unit produk
- Berguna untuk identifikasi produk premium vs ekonomis
- Contoh: Rp 50,000/unit vs Rp 150,000/unit

**2. relative_performance**
```python
relative_performance = (performance_score / mean_score) * 100
```
- Menunjukkan performa relatif terhadap rata-rata
- 100 = rata-rata
- >100 = di atas rata-rata
- <100 = di bawah rata-rata
- Contoh: 145% = 45% lebih baik dari rata-rata

---

## 6. PENYIMPANAN DATABASE

### 6.1 Function: `save_kmeans_manual_result(result)`

**Location:** `app/processing_kmeans.py`, line ~454

#### Database Schema:

```sql
-- Table 1: Menyimpan metadata hasil clustering
CREATE TABLE kmeans_result (
    id INT PRIMARY KEY AUTO_INCREMENT,
    k_value INT,                      -- Jumlah cluster (3)
    inertia FLOAT,                    -- SSE value
    davies_bouldin_index FLOAT,       -- DBI metric
    n_iter INT,                       -- Jumlah iterasi
    n_samples INT,                    -- Jumlah data (90)
    max_iterations INT,               -- Max iterasi (10)
    random_state INT,                 -- Seed (42)
    cluster_distribution JSON,        -- {'terlaris': 27, 'sedang': 36, 'kurang_laris': 27}
    analysis_data JSON,               -- Full analysis dict
    created_at TIMESTAMP
);

-- Table 2: Menyimpan detail per data point
CREATE TABLE kmeans_cluster_detail (
    id INT PRIMARY KEY AUTO_INCREMENT,
    kmeans_result_id INT,             -- FK ke kmeans_result
    cluster_id INT,                   -- 0, 1, atau 2
    jumlah_terjual INT,
    total_harga FLOAT,
    kategori VARCHAR(50),
    size VARCHAR(20),                 -- "20-24 cm"
    distance_to_centroid FLOAT        -- Jarak ke centroid
);

-- Table 3: Untuk tampilan dashboard
CREATE TABLE kmeans_final_result (
    id INT PRIMARY KEY AUTO_INCREMENT,
    kmeans_result_id INT,
    cluster_id INT,
    kategori VARCHAR(50),
    size_range VARCHAR(20),
    jumlah_terjual INT,
    created_at TIMESTAMP
);
```

#### Proses Penyimpanan:

```python
def save_kmeans_manual_result(result):
    # 1. DELETE PREVIOUS RESULTS
    KMeansClusterDetail.query.delete()
    KMeansResult.query.delete()
    db.session.commit()
    
    # 2. EXTRACT DATA FROM RESULT
    tier_labels = result['labels']          # [0, 1, 2, ...]
    cluster_labels = result['cluster_labels']  # [0, 1, 2, ...] (untuk distance)
    data_aggregated = result['data_aggregated']
    
    # 3. COUNT TIER DISTRIBUTION
    tier_counts = {
        'terlaris': int(np.sum(tier_labels == 0)),
        'sedang': int(np.sum(tier_labels == 1)),
        'kurang_laris': int(np.sum(tier_labels == 2))
    }
    
    # 4. SAVE HEADER RECORD
    result_record = KMeansResult(
        k_value=3,
        inertia=float(result['inertia']),
        davies_bouldin_index=float(result['davies_bouldin']),
        n_iter=result['n_iter'],
        n_samples=result['n_samples'],
        cluster_distribution=tier_counts,
        analysis_data=result['analysis']
    )
    db.session.add(result_record)
    db.session.flush()  # Get result_record.id
    
    # 5. SAVE DETAIL RECORDS
    X_normalized = result['X_normalized']
    centroids = result['centroids']
    
    for idx, item in enumerate(data_aggregated.itertuples()):
        # Calculate distance to centroid
        point = X_normalized[idx]
        centroid = centroids[cluster_labels[idx]]  # Use cluster_labels!
        distance = np.sqrt(np.sum((point - centroid) ** 2))
        
        # Get tier label (already integer)
        cluster_id = int(tier_labels[idx])  # 0, 1, or 2
        
        # Save detail
        detail = KMeansClusterDetail(
            kmeans_result_id=result_record.id,
            cluster_id=cluster_id,
            jumlah_terjual=int(item.jumlah_terjual),
            total_harga=float(item.total_harga),
            kategori=item.kategori,
            size=item.size_range,
            distance_to_centroid=float(distance)
        )
        db.session.add(detail)
    
    # 6. COMMIT TRANSACTION
    db.session.commit()
    
    # 7. SAVE TO FINAL RESULT TABLE (untuk dashboard)
    save_kmeans_final_result(result_record.id)
```

#### PENTING: tier_labels vs cluster_labels

```python
# tier_labels: Untuk labeling akhir (0=Terlaris, 1=Sedang, 2=Kurang Laris)
# cluster_labels: Untuk perhitungan distance ke centroid

# Kenapa perlu cluster_labels?
# Karena centroid index harus sesuai dengan cluster assignment hasil K-Means,
# bukan tier assignment hasil percentile

# Contoh:
Data point X:
  cluster_labels[X] = 1  → centroid yang dipakai: centroids[1]
  tier_labels[X] = 0     → disimpan sebagai cluster_id=0 (Terlaris)
```

---

## 7. TAMPILAN DASHBOARD

### 7.1 Route: `index()` - Dashboard Utama

**Location:** `app/routes.py`, line ~18

```python
@main.route('/')
def index():
    # 1. Get basic stats
    total_records = Penjualan.query.count()  # 1358
    
    # 2. Get clustering results
    clustering_results = []
    
    # Direct tier mapping (fixed!)
    tier_mapping = {
        0: 'Terlaris',
        1: 'Sedang',
        2: 'Kurang Laris'
    }
    
    # 3. Get final results from database
    latest_kmeans = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
    
    if latest_kmeans:
        final_results = KMeansFinalResult.query.filter_by(
            kmeans_result_id=latest_kmeans.id
        ).all()
        
        for result in final_results:
            # cluster_id sudah benar dari percentile assignment
            tier = tier_mapping[result.cluster_id]
            
            clustering_results.append({
                'kategori': result.kategori,
                'size_range': result.size_range,
                'jumlah_terjual': result.jumlah_terjual,
                'cluster_id': result.cluster_id,
                'tier': tier
            })
    
    # 4. Render template
    return render_template('index.html',
                         clustering_results=clustering_results,
                         total_records=total_records)
```

### 7.2 Template Rendering

**Location:** `app/templates/index.html`

```html
<!-- Summary Cards -->
<div class="summary-cards">
    <div class="card terlaris">
        <h3>⭐ Terlaris</h3>
        <p>{{ clustering_results | selectattr('cluster_id', 'equalto', 0) | list | length }}</p>
        <span>Produk</span>
    </div>
    <div class="card sedang">
        <h3>📊 Sedang</h3>
        <p>{{ clustering_results | selectattr('cluster_id', 'equalto', 1) | list | length }}</p>
        <span>Produk</span>
    </div>
    <div class="card kurang-laris">
        <h3>📉 Kurang Laris</h3>
        <p>{{ clustering_results | selectattr('cluster_id', 'equalto', 2) | list | length }}</p>
        <span>Produk</span>
    </div>
</div>

<!-- Data Table -->
<table>
    <thead>
        <tr>
            <th>Kategori</th>
            <th>Size Range</th>
            <th>Jumlah Terjual</th>
            <th>Cluster</th>
            <th>Kategori Penjualan</th>
        </tr>
    </thead>
    <tbody>
        {% for item in clustering_results %}
        <tr>
            <td>{{ item.kategori }}</td>
            <td>{{ item.size_range }}</td>
            <td>{{ item.jumlah_terjual }}</td>
            <td>
                <span class="badge cluster-{{ item.cluster_id }}">
                    C{{ item.cluster_id }}
                </span>
            </td>
            <td>
                {% if item.cluster_id == 0 %}
                    <span class="badge badge-success">⭐ Terlaris</span>
                {% elif item.cluster_id == 1 %}
                    <span class="badge badge-warning">📊 Sedang</span>
                {% else %}
                    <span class="badge badge-danger">📉 Kurang Laris</span>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

---

## 8. PERBEDAAN VERSI LAMA VS BARU

### 8.1 Perbandingan Alur

| Aspek | Versi Lama (Cluster-Based) | Versi Baru (Percentile-Based) |
|-------|---------------------------|-------------------------------|
| **Tier Assignment** | Berdasarkan cluster ID | Berdasarkan percentile score |
| **Distribusi** | Tidak terkontrol (1/18/71) | Dijamin 30/40/30 |
| **Performance Score** | Tidak ada | Ada (60% sales + 40% revenue) |
| **Kolom Tambahan** | Tidak ada | 3 kolom analytical |
| **Tier Mapping** | C0→Terlaris (tidak pasti) | P70→Terlaris (pasti) |
| **Business Logic** | Weak | Strong |

### 8.2 Perubahan Kode Utama

**SEBELUM:**
```python
# processing_kmeans.py - OLD VERSION
def process_kmeans_manual(k=3):
    # ... clustering ...
    labels = kmeans.labels  # Langsung pakai cluster labels
    
    # Analysis langsung dari cluster ID
    analysis = analyze_clustering_results(data, labels)
    return {'labels': labels, ...}

def analyze_clustering_results(data, labels):
    # Map cluster ID ke tier berdasarkan centroid ranking
    cluster_scores = calculate_cluster_averages(data, labels)
    sorted_clusters = sort_by_score(cluster_scores)
    
    # Assign tier berdasarkan ranking
    tier_mapping[sorted_clusters[0]] = 'terlaris'
    tier_mapping[sorted_clusters[1]] = 'sedang'
    tier_mapping[sorted_clusters[2]] = 'kurang_laris'
    
    # Masalah: Distribusi tidak terkontrol!
```

**SEKARANG:**
```python
# processing_kmeans.py - NEW VERSION
def process_kmeans_manual(k=3):
    # ... clustering ...
    cluster_labels = kmeans.labels  # Simpan untuk DBI
    
    # ✨ PERCENTILE-BASED TIER ASSIGNMENT
    tier_labels, df_with_scores = assign_tiers_by_percentile(df_aggregated, cluster_labels)
    labels = tier_labels  # Override!
    
    return {
        'labels': tier_labels,           # Untuk UI
        'cluster_labels': cluster_labels # Untuk DBI
    }

def assign_tiers_by_percentile(df, cluster_labels):
    # Calculate performance score
    df['performance_score'] = 0.6 * jumlah_norm + 0.4 * harga_norm
    
    # Apply percentile thresholds
    p30 = df['performance_score'].quantile(0.30)
    p70 = df['performance_score'].quantile(0.70)
    
    tier_labels = []
    for score in df['performance_score']:
        if score >= p70: tier_labels.append(0)      # Terlaris
        elif score >= p30: tier_labels.append(1)    # Sedang
        else: tier_labels.append(2)                 # Kurang Laris
    
    return np.array(tier_labels), df
```

### 8.3 Impact Analysis

**Metrik Kualitas:**

| Metrik | Versi Lama | Versi Baru |
|--------|-----------|-----------|
| **Distribusi** | 5.5% / 22% / 72.5% | 30% / 40% / 30% ✓ |
| **Business Logic** | Tidak konsisten | Konsisten ✓ |
| **Interpretability** | Sulit dijelaskan | Mudah dijelaskan ✓ |
| **Fairness** | Tidak adil (bias ke kurang laris) | Adil (seimbang) ✓ |
| **DBI Calculation** | Benar | Tetap benar ✓ |

---

## 9. CARA MENJALANKAN SISTEM

### 9.1 Setup Environment

```bash
# 1. Activate virtual environment
.\env\Scripts\activate

# 2. Install dependencies (jika belum)
pip install -r requirements.txt

# 3. Setup database
# Pastikan MySQL running dan database sudah di-import
```

### 9.2 Run Application

```bash
# Start Flask server
python app.py

# Output:
#  * Running on http://127.0.0.1:5000
#  * Debug mode: on
```

### 9.3 Testing Clustering

```
1. Buka browser: http://127.0.0.1:5000
2. Menu: Preprocessing → K-Means
3. Set parameter K = 3
4. Klik "Jalankan Clustering"
5. Tunggu proses (~5-10 detik)
6. Lihat hasil:
   - Metrics (Inertia, DBI)
   - Iterasi detail
   - Final results table
   - Summary (30/40/30)
7. Cek dashboard: Menu → Dashboard
   - Verifikasi distribusi cluster
```

---

## 10. TROUBLESHOOTING

### Masalah Umum:

**1. Semua data masuk C2 (Kurang Laris)**
```
Cause: tier_to_cluster mapping masih menggunakan string
Fix: Gunakan int(tier_labels[idx]) langsung
```

**2. Error "Failed to process data"**
```
Cause: Mismatch tipe data di analyze_clustering_results_aggregated
Fix: Pastikan tier_names_map menggunakan key integer (0, 1, 2)
```

**3. Final results tidak muncul di dashboard**
```
Cause: KMeansFinalResult tidak terisi atau tier_mapping salah
Fix: Pastikan save_kmeans_final_result() dipanggil dan tier_mapping = {0: 'Terlaris', ...}
```

**4. DBI calculation error**
```
Cause: Menggunakan tier_labels untuk DBI
Fix: Gunakan cluster_labels (bukan tier_labels) untuk DBI calculation
```

---

## 11. KESIMPULAN

### Key Takeaways:

1. **Percentile-based tier assignment** adalah solusi untuk mengatasi distribusi cluster yang tidak seimbang pada data skewed

2. **Separasi concern:** 
   - `cluster_labels` untuk metrik clustering (DBI, distance)
   - `tier_labels` untuk business labeling (Terlaris/Sedang/Kurang Laris)

3. **Performance score** mengkombinasikan multiple features dengan weighted sum (60/40)

4. **3 kolom tambahan** memberikan insight lebih dalam untuk analisis bisnis

5. **Distribusi 30/40/30** memberikan klasifikasi yang lebih adil dan masuk akal

### Rekomendasi Pengembangan:

1. **Dynamic percentile thresholds** - Biarkan user set P30 dan P70 sendiri
2. **Multi-feature scoring** - Tambah feature: frequency, recency, profit margin
3. **Time-series analysis** - Bandingkan performa antar periode waktu
4. **Category-specific thresholds** - Threshold berbeda untuk Standard vs Non-Standard
5. **Visualization** - Tambah scatter plot, dendogram, elbow curve

---

**END OF DOCUMENTATION**

Generated: 14 Desember 2025  
Author: AI Assistant  
Version: 2.0 Final
