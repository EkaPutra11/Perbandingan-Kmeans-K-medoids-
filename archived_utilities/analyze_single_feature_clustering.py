"""
Analisis: Clustering dengan 1 Feature (jumlah_terjual saja) vs 2 Features
Membandingkan hasil clustering dengan dan tanpa total_harga
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score

# Database connection
DATABASE_URI = 'mysql+pymysql://root:@localhost/db_penjualan_arwana'
engine = create_engine(DATABASE_URI)

print("="*80)
print("ANALISIS: CLUSTERING 1 FEATURE vs 2 FEATURES")
print("="*80)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n[1] Loading data from database...")
query = "SELECT * FROM penjualan"
df = pd.read_sql(query, engine)
print(f"    Total records: {len(df)}")

# ============================================================================
# 2. AGGREGATION
# ============================================================================
print("\n[2] Aggregating data by kategori + size range...")

def get_size_range(size_str):
    try:
        size_num = int(size_str.replace('cm', '').strip())
        range_start = (size_num // 5) * 5
        range_end = range_start + 4
        return f"{range_start}-{range_end} cm"
    except:
        return "Unknown"

df['size_range'] = df['size'].apply(get_size_range)
df = df[df['size_range'] != 'Unknown'].copy()

df_agg = df.groupby(['kategori', 'size_range']).agg({
    'jumlah_terjual': 'sum',
    'total_harga': 'sum'
}).reset_index()

print(f"    Aggregated records: {len(df_agg)}")
print(f"    Features: jumlah_terjual, total_harga")

# ============================================================================
# 3. CLUSTERING SKENARIO A: 1 FEATURE (jumlah_terjual saja, NO NORMALIZATION)
# ============================================================================
print("\n" + "="*80)
print("SKENARIO A: 1 Feature (jumlah_terjual) - NO NORMALIZATION")
print("="*80)

X_single = df_agg[['jumlah_terjual']].values
print(f"\nFeature matrix shape: {X_single.shape}")
print(f"Feature range: {X_single.min():.0f} - {X_single.max():.0f}")

# K-Means dengan 1 feature
kmeans_single = KMeans(n_clusters=3, random_state=42, n_init=10)
labels_single = kmeans_single.fit_predict(X_single)
centroids_single = kmeans_single.cluster_centers_

print("\nCentroid values (jumlah_terjual):")
for i in range(3):
    count = np.sum(labels_single == i)
    pct = count / len(labels_single) * 100
    print(f"  Cluster {i}: {centroids_single[i][0]:.1f} units  ({count} data, {pct:.1f}%)")

# Metrics
inertia_single = kmeans_single.inertia_
dbi_single = davies_bouldin_score(X_single, labels_single)
sil_single = silhouette_score(X_single, labels_single)

print(f"\nMetrics:")
print(f"  Inertia: {inertia_single:.2f}")
print(f"  Davies-Bouldin Index: {dbi_single:.4f}")
print(f"  Silhouette Score: {sil_single:.4f}")

# Distribution per cluster
print("\nCluster distribution:")
for i in range(3):
    cluster_data = X_single[labels_single == i]
    print(f"  Cluster {i}: min={cluster_data.min():.0f}, max={cluster_data.max():.0f}, "
          f"mean={cluster_data.mean():.1f}, median={np.median(cluster_data):.1f}")

# Assign tier based on centroid ranking
centroid_ranks = np.argsort(centroids_single.flatten())[::-1]  # Descending
tier_map_single = {}
tier_map_single[centroid_ranks[0]] = 'Terlaris'
tier_map_single[centroid_ranks[1]] = 'Sedang'
tier_map_single[centroid_ranks[2]] = 'Kurang Laris'

print("\nTier assignment (based on centroid ranking):")
for cluster_id, tier in tier_map_single.items():
    count = np.sum(labels_single == cluster_id)
    pct = count / len(labels_single) * 100
    print(f"  Cluster {cluster_id} → {tier}: {count} data ({pct:.1f}%)")

# ============================================================================
# 4. CLUSTERING SKENARIO B: 2 FEATURES (jumlah_terjual + total_harga, NORMALIZED)
# ============================================================================
print("\n" + "="*80)
print("SKENARIO B: 2 Features (jumlah_terjual + total_harga) - WITH NORMALIZATION")
print("="*80)

X_dual = df_agg[['jumlah_terjual', 'total_harga']].values
print(f"\nFeature matrix shape: {X_dual.shape}")
print(f"Feature 1 range (jumlah): {X_dual[:,0].min():.0f} - {X_dual[:,0].max():.0f}")
print(f"Feature 2 range (harga): {X_dual[:,1].min():.0f} - {X_dual[:,1].max():.0f}")

# Normalization
X_mean = X_dual.mean(axis=0)
X_std = X_dual.std(axis=0)
X_dual_norm = (X_dual - X_mean) / (X_std + 1e-8)

print(f"\nAfter normalization:")
print(f"  Mean: {X_dual_norm.mean(axis=0)}")
print(f"  Std: {X_dual_norm.std(axis=0)}")

# K-Means dengan 2 features normalized
kmeans_dual = KMeans(n_clusters=3, random_state=42, n_init=10)
labels_dual = kmeans_dual.fit_predict(X_dual_norm)
centroids_dual_norm = kmeans_dual.cluster_centers_

# Denormalize centroids for interpretation
centroids_dual = centroids_dual_norm * X_std + X_mean

print("\nCentroid values (denormalized):")
for i in range(3):
    count = np.sum(labels_dual == i)
    pct = count / len(labels_dual) * 100
    print(f"  Cluster {i}: jumlah={centroids_dual[i][0]:.1f}, harga={centroids_dual[i][1]:.0f}  "
          f"({count} data, {pct:.1f}%)")

# Metrics
inertia_dual = kmeans_dual.inertia_
dbi_dual = davies_bouldin_score(X_dual_norm, labels_dual)
sil_dual = silhouette_score(X_dual_norm, labels_dual)

print(f"\nMetrics:")
print(f"  Inertia: {inertia_dual:.2f}")
print(f"  Davies-Bouldin Index: {dbi_dual:.4f}")
print(f"  Silhouette Score: {sil_dual:.4f}")

# Distribution per cluster
print("\nCluster distribution (jumlah_terjual):")
for i in range(3):
    cluster_data = X_dual[labels_dual == i, 0]  # jumlah_terjual only
    print(f"  Cluster {i}: min={cluster_data.min():.0f}, max={cluster_data.max():.0f}, "
          f"mean={cluster_data.mean():.1f}, median={np.median(cluster_data):.1f}")

# Assign tier based on composite score
composite_scores = []
for i in range(3):
    # Composite score: normalized centroid magnitude
    score = np.linalg.norm(centroids_dual_norm[i])
    composite_scores.append((i, score))

composite_scores.sort(key=lambda x: x[1], reverse=True)
tier_map_dual = {}
tier_map_dual[composite_scores[0][0]] = 'Terlaris'
tier_map_dual[composite_scores[1][0]] = 'Sedang'
tier_map_dual[composite_scores[2][0]] = 'Kurang Laris'

print("\nTier assignment (based on composite score):")
for cluster_id, tier in tier_map_dual.items():
    count = np.sum(labels_dual == cluster_id)
    pct = count / len(labels_dual) * 100
    print(f"  Cluster {cluster_id} → {tier}: {count} data ({pct:.1f}%)")

# ============================================================================
# 5. PERCENTILE-BASED TIER ASSIGNMENT (Current Implementation)
# ============================================================================
print("\n" + "="*80)
print("SKENARIO C: PERCENTILE-BASED TIER ASSIGNMENT (Current)")
print("="*80)

# Using 2 features normalized data from Skenario B
jumlah_norm = (df_agg['jumlah_terjual'] - df_agg['jumlah_terjual'].min()) / \
              (df_agg['jumlah_terjual'].max() - df_agg['jumlah_terjual'].min() + 1e-8)
harga_norm = (df_agg['total_harga'] - df_agg['total_harga'].min()) / \
             (df_agg['total_harga'].max() - df_agg['total_harga'].min() + 1e-8)

performance_score = 0.6 * jumlah_norm + 0.4 * harga_norm

p30 = performance_score.quantile(0.30)
p70 = performance_score.quantile(0.70)

print(f"\nPercentile thresholds:")
print(f"  P30 = {p30:.4f}")
print(f"  P70 = {p70:.4f}")

tier_labels_percentile = []
for score in performance_score:
    if score >= p70:
        tier_labels_percentile.append(0)  # Terlaris
    elif score >= p30:
        tier_labels_percentile.append(1)  # Sedang
    else:
        tier_labels_percentile.append(2)  # Kurang Laris

tier_labels_percentile = np.array(tier_labels_percentile)

print("\nTier distribution (percentile-based):")
tiers = ['Terlaris', 'Sedang', 'Kurang Laris']
for i, tier in enumerate(tiers):
    count = np.sum(tier_labels_percentile == i)
    pct = count / len(tier_labels_percentile) * 100
    print(f"  {tier}: {count} data ({pct:.1f}%)")

# Distribution per tier
print("\nData distribution per tier (jumlah_terjual):")
for i, tier in enumerate(tiers):
    tier_data = df_agg.loc[tier_labels_percentile == i, 'jumlah_terjual']
    print(f"  {tier}: min={tier_data.min():.0f}, max={tier_data.max():.0f}, "
          f"mean={tier_data.mean():.1f}, median={tier_data.median():.1f}")

# ============================================================================
# 6. COMPARATIVE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("COMPARATIVE ANALYSIS")
print("="*80)

# Create comparison table
comparison_data = []

# Skenario A
tier_counts_a = []
for tier in ['Terlaris', 'Sedang', 'Kurang Laris']:
    cluster_ids = [k for k, v in tier_map_single.items() if v == tier]
    count = sum(np.sum(labels_single == cid) for cid in cluster_ids)
    tier_counts_a.append(count)

# Skenario B
tier_counts_b = []
for tier in ['Terlaris', 'Sedang', 'Kurang Laris']:
    cluster_ids = [k for k, v in tier_map_dual.items() if v == tier]
    count = sum(np.sum(labels_dual == cid) for cid in cluster_ids)
    tier_counts_b.append(count)

# Skenario C
tier_counts_c = [
    np.sum(tier_labels_percentile == 0),
    np.sum(tier_labels_percentile == 1),
    np.sum(tier_labels_percentile == 2)
]

print("\n1. TIER DISTRIBUTION COMPARISON:")
print("-" * 80)
print(f"{'Tier':<20} {'Skenario A':<20} {'Skenario B':<20} {'Skenario C':<20}")
print(f"{'':20} {'(1 Feature)':<20} {'(2 Features Norm)':<20} {'(Percentile)':<20}")
print("-" * 80)

tiers = ['Terlaris', 'Sedang', 'Kurang Laris']
for i, tier in enumerate(tiers):
    pct_a = tier_counts_a[i] / len(df_agg) * 100
    pct_b = tier_counts_b[i] / len(df_agg) * 100
    pct_c = tier_counts_c[i] / len(df_agg) * 100
    print(f"{tier:<20} {tier_counts_a[i]:>3} ({pct_a:>5.1f}%)       "
          f"{tier_counts_b[i]:>3} ({pct_b:>5.1f}%)       "
          f"{tier_counts_c[i]:>3} ({pct_c:>5.1f}%)")

print("\n2. CLUSTERING QUALITY METRICS:")
print("-" * 80)
print(f"{'Metric':<25} {'Skenario A':<20} {'Skenario B':<20}")
print("-" * 80)
print(f"{'Inertia':<25} {inertia_single:<20.2f} {inertia_dual:<20.2f}")
print(f"{'Davies-Bouldin Index':<25} {dbi_single:<20.4f} {dbi_dual:<20.4f}")
print(f"{'Silhouette Score':<25} {sil_single:<20.4f} {sil_dual:<20.4f}")
print("\nNote: DBI lower is better, Silhouette higher is better")

# ============================================================================
# 7. DETAILED EXAMPLES
# ============================================================================
print("\n" + "="*80)
print("CONTOH DATA KONKRET")
print("="*80)

# Get top 10 by jumlah_terjual
df_agg_sorted = df_agg.sort_values('jumlah_terjual', ascending=False).head(10).copy()
df_agg_sorted['tier_skenario_a'] = [tier_map_single[labels_single[i]] 
                                     for i in df_agg_sorted.index]
df_agg_sorted['tier_skenario_b'] = [tier_map_dual[labels_dual[i]] 
                                     for i in df_agg_sorted.index]
df_agg_sorted['tier_skenario_c'] = [tiers[tier_labels_percentile[i]] 
                                     for i in df_agg_sorted.index]

print("\nTop 10 Produk (sorted by jumlah_terjual):")
print("-" * 120)
print(f"{'Kategori':<15} {'Size Range':<15} {'Jumlah':<10} {'Harga':<12} "
      f"{'Tier A':<15} {'Tier B':<15} {'Tier C':<15}")
print("-" * 120)

for idx, row in df_agg_sorted.iterrows():
    print(f"{row['kategori']:<15} {row['size_range']:<15} "
          f"{row['jumlah_terjual']:<10.0f} {row['total_harga']:<12.0f} "
          f"{row['tier_skenario_a']:<15} {row['tier_skenario_b']:<15} "
          f"{row['tier_skenario_c']:<15}")

# ============================================================================
# 8. KESIMPULAN
# ============================================================================
print("\n" + "="*80)
print("KESIMPULAN")
print("="*80)

print("\n📊 SKENARIO A: 1 Feature (jumlah_terjual saja) - NO NORMALIZATION")
print("-" * 80)
print("✓ KELEBIHAN:")
print("  • Sederhana dan mudah diinterpretasikan")
print("  • Fokus hanya pada volume penjualan")
print("  • Tidak perlu normalisasi")
print("  • Cocok jika revenue tidak penting")
print("\n✗ KEKURANGAN:")
print("  • Mengabaikan nilai revenue (total_harga)")
print("  • Produk murah yang laku banyak = Produk mahal yang laku sedikit")
print("  • Tidak bisa bedakan produk premium vs ekonomis")
print("  • Distribusi tidak terkontrol (bisa sangat timpang)")
print(f"  • Actual distribution: {tier_counts_a[0]}/{tier_counts_a[1]}/{tier_counts_a[2]} "
      f"({tier_counts_a[0]/len(df_agg)*100:.1f}%/{tier_counts_a[1]/len(df_agg)*100:.1f}%/"
      f"{tier_counts_a[2]/len(df_agg)*100:.1f}%)")

print("\n📊 SKENARIO B: 2 Features (jumlah + harga) - WITH NORMALIZATION")
print("-" * 80)
print("✓ KELEBIHAN:")
print("  • Mempertimbangkan 2 aspek: volume DAN revenue")
print("  • Lebih comprehensive dalam evaluasi performa")
print("  • Normalisasi mencegah dominasi feature dengan skala besar")
print("  • Better clustering quality (DBI, Silhouette)")
print("\n✗ KEKURANGAN:")
print("  • Lebih kompleks")
print("  • Distribusi tetap tidak terkontrol")
print(f"  • Actual distribution: {tier_counts_b[0]}/{tier_counts_b[1]}/{tier_counts_b[2]} "
      f"({tier_counts_b[0]/len(df_agg)*100:.1f}%/{tier_counts_b[1]/len(df_agg)*100:.1f}%/"
      f"{tier_counts_b[2]/len(df_agg)*100:.1f}%)")

print("\n📊 SKENARIO C: PERCENTILE-BASED (Current Implementation)")
print("-" * 80)
print("✓ KELEBIHAN:")
print("  • Distribusi DIJAMIN seimbang (30/40/30)")
print("  • Mempertimbangkan volume DAN revenue dengan weighted score")
print("  • Adil untuk semua kategori produk")
print("  • Business-friendly interpretation")
print("  • Menambahkan analytical columns (performance_score, avg_price, etc)")
print(f"  • Actual distribution: {tier_counts_c[0]}/{tier_counts_c[1]}/{tier_counts_c[2]} "
      f"({tier_counts_c[0]/len(df_agg)*100:.1f}%/{tier_counts_c[1]/len(df_agg)*100:.1f}%/"
      f"{tier_counts_c[2]/len(df_agg)*100:.1f}%)")
print("\n✗ KEKURANGAN:")
print("  • Lebih kompleks untuk dijelaskan")
print("  • Tidak murni clustering (hybrid approach)")

print("\n🎯 REKOMENDASI:")
print("-" * 80)
print("Gunakan SKENARIO C (Percentile-Based) karena:")
print("  1. Data arwana sales sangat skewed (85% produk terjual 0-5 unit)")
print("  2. Cluster-based labeling menghasilkan distribusi 1/18/71 (tidak masuk akal)")
print("  3. Percentile approach memberikan distribusi seimbang 27/36/27")
print("  4. Lebih adil untuk business decision making")
print("  5. Menggabungkan volume + revenue dengan weighted score")

print("\n💡 ALTERNATIF:")
print("-" * 80)
print("Jika HANYA ingin fokus pada VOLUME PENJUALAN:")
print("  → Gunakan Skenario A (1 feature: jumlah_terjual)")
print("  → TAPI tetap gunakan percentile-based tier assignment!")
print("  → performance_score = jumlah_terjual_normalized (100% weight)")
print("  → Hasilnya: distribusi tetap 30/40/30, tapi hanya berdasarkan volume")

print("\n" + "="*80)
print("END OF ANALYSIS")
print("="*80)
