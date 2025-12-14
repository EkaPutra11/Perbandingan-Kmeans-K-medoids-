"""
Hitung DBI KESELURUHAN (90 data) setelah clustering terpisah
"""
from app import create_app
from app.models import Penjualan
import pandas as pd
import numpy as np

app = create_app()

def get_size_range(size_str):
    try:
        size_num = int(size_str.replace('cm', '').strip())
        range_start = (size_num // 5) * 5
        range_end = range_start + 4
        return f"{range_start}-{range_end} cm"
    except:
        return "Unknown"

def manual_kmeans(X, k=3, max_iter=100, seed=42):
    np.random.seed(seed)
    n_samples, n_features = X.shape
    
    indices = np.random.choice(n_samples, k, replace=False)
    centroids = X[indices].copy()
    
    for iteration in range(max_iter):
        distances = np.zeros((n_samples, k))
        for i in range(k):
            distances[:, i] = np.sqrt(np.sum((X - centroids[i])**2, axis=1))
        
        labels = np.argmin(distances, axis=1)
        
        old_centroids = centroids.copy()
        for i in range(k):
            cluster_points = X[labels == i]
            if len(cluster_points) > 0:
                centroids[i] = cluster_points.mean(axis=0)
        
        if np.allclose(old_centroids, centroids, atol=1e-4):
            break
    
    return labels, centroids

def calculate_dbi(X, labels, centroids):
    """Calculate Davies-Bouldin Index"""
    n_clusters = len(np.unique(labels))
    
    if n_clusters <= 1:
        return 0.0
    
    scatter = np.zeros(n_clusters)
    for i in range(n_clusters):
        cluster_points = X[labels == i]
        if len(cluster_points) > 0:
            distances = np.sqrt(np.sum((cluster_points - centroids[i])**2, axis=1))
            scatter[i] = distances.mean()
    
    dbi = 0.0
    for i in range(n_clusters):
        max_ratio = 0.0
        for j in range(n_clusters):
            if i != j:
                centroid_dist = np.sqrt(np.sum((centroids[i] - centroids[j])**2))
                if centroid_dist > 0:
                    ratio = (scatter[i] + scatter[j]) / centroid_dist
                    max_ratio = max(max_ratio, ratio)
        dbi += max_ratio
    
    return dbi / n_clusters

with app.app_context():
    print("="*80)
    print("HITUNG DBI KESELURUHAN SETELAH CLUSTERING TERPISAH")
    print("="*80)
    
    # Load data
    data = Penjualan.query.all()
    df = pd.DataFrame([{
        'kategori': d.kategori,
        'size': d.size,
        'jumlah_terjual': d.jumlah_terjual,
        'total_harga': float(d.total_harga) if d.total_harga else 0,
    } for d in data])
    
    df['size_range'] = df['size'].apply(get_size_range)
    df = df[df['size_range'] != 'Unknown']
    
    df_agg = df.groupby(['kategori', 'size_range']).agg({
        'jumlah_terjual': 'sum',
        'total_harga': 'sum'
    }).reset_index()
    
    # Split
    df_agg['category_type'] = df_agg['kategori'].apply(
        lambda x: 'Standard' if x.lower() in ['standard', 'standar'] else 'Non-Standard'
    )
    
    df_standard = df_agg[df_agg['category_type'] == 'Standard'].copy()
    df_non_standard = df_agg[df_agg['category_type'] == 'Non-Standard'].copy()
    
    print(f"\nTotal data: {len(df_agg)}")
    print(f"Standard: {len(df_standard)}")
    print(f"Non-Standard: {len(df_non_standard)}")
    
    # ========================================================================
    # CLUSTERING TERPISAH
    # ========================================================================
    print("\n" + "="*80)
    print("1️⃣  CLUSTERING TERPISAH")
    print("="*80)
    
    # Clustering Standard
    print("\n🔵 Standard Clustering...")
    X_std = df_standard[['jumlah_terjual', 'total_harga']].values.astype(float)
    X_std_mean = X_std.mean(axis=0)
    X_std_std = X_std.std(axis=0)
    X_std_norm = (X_std - X_std_mean) / (X_std_std + 1e-8)
    
    labels_std, centroids_std = manual_kmeans(X_std_norm, k=3, seed=42)
    df_standard['cluster_id'] = labels_std
    
    print(f"  Clusters: {np.bincount(labels_std)}")
    
    # Clustering Non-Standard
    print("\n🟠 Non-Standard Clustering...")
    X_nonstd = df_non_standard[['jumlah_terjual', 'total_harga']].values.astype(float)
    X_nonstd_mean = X_nonstd.mean(axis=0)
    X_nonstd_std = X_nonstd.std(axis=0)
    X_nonstd_norm = (X_nonstd - X_nonstd_mean) / (X_nonstd_std + 1e-8)
    
    labels_nonstd, centroids_nonstd = manual_kmeans(X_nonstd_norm, k=3, seed=42)
    df_non_standard['cluster_id'] = labels_nonstd
    
    print(f"  Clusters: {np.bincount(labels_nonstd)}")
    
    # Gabungkan kembali
    df_combined = pd.concat([df_standard, df_non_standard], ignore_index=True)
    
    # ========================================================================
    # HITUNG DBI DARI 90 DATA GABUNGAN
    # ========================================================================
    print("\n" + "="*80)
    print("2️⃣  HITUNG DBI KESELURUHAN (90 DATA GABUNGAN)")
    print("="*80)
    
    # Extract data dan labels
    X_all_original = df_combined[['jumlah_terjual', 'total_harga']].values.astype(float)
    labels_all = df_combined['cluster_id'].values
    
    print(f"\nTotal data points: {len(X_all_original)}")
    print(f"Unique clusters: {len(np.unique(labels_all))}")
    print(f"Cluster distribution: {np.bincount(labels_all)}")
    
    # Normalize seluruh data (untuk perhitungan DBI)
    X_all_mean = X_all_original.mean(axis=0)
    X_all_std = X_all_original.std(axis=0)
    X_all_norm = (X_all_original - X_all_mean) / (X_all_std + 1e-8)
    
    # Hitung centroid dari setiap cluster (dalam normalized space)
    unique_clusters = np.unique(labels_all)
    centroids_all = np.zeros((len(unique_clusters), 2))
    
    for i, cluster_id in enumerate(unique_clusters):
        cluster_points = X_all_norm[labels_all == cluster_id]
        centroids_all[i] = cluster_points.mean(axis=0)
    
    print(f"\nCentroids (normalized):")
    for i, c in enumerate(centroids_all):
        cluster_id = unique_clusters[i]
        n_points = np.sum(labels_all == cluster_id)
        print(f"  Cluster {cluster_id}: [{c[0]:7.4f}, {c[1]:7.4f}] ({n_points} points)")
    
    # Hitung DBI
    dbi_keseluruhan = calculate_dbi(X_all_norm, labels_all, centroids_all)
    
    print(f"\n" + "="*80)
    print(f"✅ DBI KESELURUHAN (90 data, clustering terpisah): {dbi_keseluruhan:.4f}")
    print("="*80)
    
    # ========================================================================
    # BANDINGKAN DENGAN CLUSTERING DIGABUNG
    # ========================================================================
    print("\n" + "="*80)
    print("3️⃣  BANDINGKAN: CLUSTERING DIGABUNG")
    print("="*80)
    
    # Reset dataframe
    df_agg_reset = df.groupby(['kategori', 'size_range']).agg({
        'jumlah_terjual': 'sum',
        'total_harga': 'sum'
    }).reset_index()
    
    X_digabung = df_agg_reset[['jumlah_terjual', 'total_harga']].values.astype(float)
    X_digabung_mean = X_digabung.mean(axis=0)
    X_digabung_std = X_digabung.std(axis=0)
    X_digabung_norm = (X_digabung - X_digabung_mean) / (X_digabung_std + 1e-8)
    
    labels_digabung, centroids_digabung = manual_kmeans(X_digabung_norm, k=3, seed=42)
    
    dbi_digabung = calculate_dbi(X_digabung_norm, labels_digabung, centroids_digabung)
    
    print(f"\nTotal data points: {len(X_digabung_norm)}")
    print(f"Cluster distribution: {np.bincount(labels_digabung)}")
    print(f"\n✅ DBI DIGABUNG: {dbi_digabung:.4f}")
    
    # ========================================================================
    # PERBANDINGAN FINAL
    # ========================================================================
    print("\n" + "="*80)
    print("📊 PERBANDINGAN FINAL")
    print("="*80)
    
    selisih = dbi_keseluruhan - dbi_digabung
    persen = (selisih / dbi_digabung) * 100
    
    print(f"""
┌─────────────────────────────────────────────────────────────────┐
│                    DBI COMPARISON SUMMARY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CLUSTERING TERPISAH (90 data keseluruhan):                    │
│    DBI = {dbi_keseluruhan:.4f}                                             │
│    Distribusi: {np.bincount(labels_all)}                            │
│                                                                 │
│  CLUSTERING DIGABUNG (90 data):                                │
│    DBI = {dbi_digabung:.4f}                                             │
│    Distribusi: {np.bincount(labels_digabung)}                            │
│                                                                 │
│  SELISIH: {selisih:+.4f} ({persen:+.1f}%)                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
    """)
    
    if selisih < 0:
        print("✅ CLUSTERING TERPISAH LEBIH BAIK (DBI lebih rendah)")
        print(f"   Clustering terpisah menghasilkan DBI {abs(persen):.1f}% lebih baik!\n")
    else:
        print("⚠️  CLUSTERING DIGABUNG LEBIH BAIK (DBI lebih rendah)")
        print(f"   Clustering terpisah menghasilkan DBI {abs(persen):.1f}% lebih buruk\n")
    
    # Detail analysis
    print("="*80)
    print("🔍 ANALISIS")
    print("="*80)
    
    print(f"""
METODE 1: CLUSTERING TERPISAH
- Standard dan Non-Standard di-cluster terpisah
- Kemudian digabungkan
- Total 6 cluster (3 Standard + 3 Non-Standard)
- DBI dihitung dari 90 data dengan 6 cluster labels
- Hasil DBI: {dbi_keseluruhan:.4f}

METODE 2: CLUSTERING DIGABUNG  
- Semua 90 data di-cluster sekaligus
- Total 3 cluster
- DBI dihitung dari 90 data dengan 3 cluster labels
- Hasil DBI: {dbi_digabung:.4f}

KESIMPULAN:
{"✅ Clustering terpisah menghasilkan DBI lebih rendah (lebih baik)" if selisih < 0 else "⚠️  Clustering digabung menghasilkan DBI lebih rendah"}
{"   Meskipun ada 6 cluster (bukan 3), DBI tetap lebih baik" if selisih < 0 else ""}
{"   Ini membuktikan clustering terpisah lebih optimal!" if selisih < 0 else ""}
    """)
    
    print("="*80)
