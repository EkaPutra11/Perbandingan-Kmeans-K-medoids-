"""
Perhitungan Manual DBI untuk Standard dan Non-Standard Terpisah
TANPA menggunakan code existing - fresh calculation from scratch
"""
from app import create_app
from app.models import Penjualan
import pandas as pd
import numpy as np

app = create_app()

# ============================================================================
# HELPER FUNCTIONS - Manual Implementation
# ============================================================================

def get_size_range(size_str):
    """Convert size to range"""
    try:
        size_num = int(size_str.replace('cm', '').strip())
        range_start = (size_num // 5) * 5
        range_end = range_start + 4
        return f"{range_start}-{range_end} cm"
    except:
        return "Unknown"

def manual_kmeans(X, k=3, max_iter=100, seed=42):
    """Manual K-Means implementation from scratch"""
    np.random.seed(seed)
    n_samples, n_features = X.shape
    
    # Random initialization
    indices = np.random.choice(n_samples, k, replace=False)
    centroids = X[indices].copy()
    
    for iteration in range(max_iter):
        # Assign to nearest centroid
        distances = np.zeros((n_samples, k))
        for i in range(k):
            distances[:, i] = np.sqrt(np.sum((X - centroids[i])**2, axis=1))
        
        labels = np.argmin(distances, axis=1)
        
        # Update centroids
        old_centroids = centroids.copy()
        for i in range(k):
            cluster_points = X[labels == i]
            if len(cluster_points) > 0:
                centroids[i] = cluster_points.mean(axis=0)
        
        # Check convergence
        if np.allclose(old_centroids, centroids, atol=1e-4):
            print(f"  Converged at iteration {iteration + 1}")
            break
    
    return labels, centroids

def calculate_dbi(X, labels, centroids):
    """Calculate Davies-Bouldin Index from scratch"""
    n_clusters = len(np.unique(labels))
    
    if n_clusters <= 1:
        return 0.0
    
    # Calculate scatter (average distance within cluster)
    scatter = np.zeros(n_clusters)
    for i in range(n_clusters):
        cluster_points = X[labels == i]
        if len(cluster_points) > 0:
            distances = np.sqrt(np.sum((cluster_points - centroids[i])**2, axis=1))
            scatter[i] = distances.mean()
    
    # Calculate DBI
    dbi = 0.0
    for i in range(n_clusters):
        max_ratio = 0.0
        for j in range(n_clusters):
            if i != j:
                # Distance between centroids
                centroid_dist = np.sqrt(np.sum((centroids[i] - centroids[j])**2))
                if centroid_dist > 0:
                    ratio = (scatter[i] + scatter[j]) / centroid_dist
                    max_ratio = max(max_ratio, ratio)
        dbi += max_ratio
    
    return dbi / n_clusters

# ============================================================================
# MAIN CALCULATION
# ============================================================================

with app.app_context():
    print("="*80)
    print("PERHITUNGAN MANUAL DBI - CLUSTERING TERPISAH")
    print("="*80)
    
    # 1. Get and prepare data
    print("\n📊 STEP 1: LOAD & PREPARE DATA")
    print("-"*80)
    
    data = Penjualan.query.all()
    df = pd.DataFrame([{
        'kategori': d.kategori,
        'size': d.size,
        'jumlah_terjual': d.jumlah_terjual,
        'total_harga': float(d.total_harga) if d.total_harga else 0,
    } for d in data])
    
    # Aggregate by size range
    df['size_range'] = df['size'].apply(get_size_range)
    df = df[df['size_range'] != 'Unknown']
    
    df_agg = df.groupby(['kategori', 'size_range']).agg({
        'jumlah_terjual': 'sum',
        'total_harga': 'sum'
    }).reset_index()
    
    print(f"Total aggregated records: {len(df_agg)}")
    
    # 2. Split Standard vs Non-Standard
    print("\n📊 STEP 2: SPLIT DATA")
    print("-"*80)
    
    df_agg['category_type'] = df_agg['kategori'].apply(
        lambda x: 'Standard' if x.lower() in ['standard', 'standar'] else 'Non-Standard'
    )
    
    df_standard = df_agg[df_agg['category_type'] == 'Standard'].copy()
    df_non_standard = df_agg[df_agg['category_type'] == 'Non-Standard'].copy()
    
    print(f"Standard records: {len(df_standard)}")
    print(f"Non-Standard records: {len(df_non_standard)}")
    
    # 3. Process Standard
    print("\n" + "="*80)
    print("🔵 CLUSTERING STANDARD")
    print("="*80)
    
    if len(df_standard) > 0:
        X_std = df_standard[['jumlah_terjual', 'total_harga']].values.astype(float)
        
        # Normalize
        X_std_mean = X_std.mean(axis=0)
        X_std_std = X_std.std(axis=0)
        X_std_norm = (X_std - X_std_mean) / (X_std_std + 1e-8)
        
        print(f"\nData shape: {X_std_norm.shape}")
        print(f"Mean: [{X_std_mean[0]:.2f}, {X_std_mean[1]:.2f}]")
        print(f"Std: [{X_std_std[0]:.2f}, {X_std_std[1]:.2f}]")
        
        # Clustering
        print("\nRunning K-Means (k=3)...")
        labels_std, centroids_std = manual_kmeans(X_std_norm, k=3, seed=42)
        
        # Calculate DBI
        dbi_std = calculate_dbi(X_std_norm, labels_std, centroids_std)
        
        print(f"\n✅ DBI Standard: {dbi_std:.4f}")
        
        # Cluster distribution
        print(f"\nCluster distribution:")
        for i in range(3):
            count = np.sum(labels_std == i)
            print(f"  Cluster {i}: {count} items ({count/len(labels_std)*100:.1f}%)")
        
        # Centroid info
        print(f"\nCentroids (normalized):")
        for i, c in enumerate(centroids_std):
            print(f"  Cluster {i}: [{c[0]:.4f}, {c[1]:.4f}]")
    else:
        print("⚠️  No Standard data")
        dbi_std = 0
        labels_std = np.array([])
    
    # 4. Process Non-Standard
    print("\n" + "="*80)
    print("🟠 CLUSTERING NON-STANDARD")
    print("="*80)
    
    if len(df_non_standard) > 0:
        X_nonstd = df_non_standard[['jumlah_terjual', 'total_harga']].values.astype(float)
        
        # Normalize
        X_nonstd_mean = X_nonstd.mean(axis=0)
        X_nonstd_std = X_nonstd.std(axis=0)
        X_nonstd_norm = (X_nonstd - X_nonstd_mean) / (X_nonstd_std + 1e-8)
        
        print(f"\nData shape: {X_nonstd_norm.shape}")
        print(f"Mean: [{X_nonstd_mean[0]:.2f}, {X_nonstd_mean[1]:.2f}]")
        print(f"Std: [{X_nonstd_std[0]:.2f}, {X_nonstd_std[1]:.2f}]")
        
        # Clustering
        print("\nRunning K-Means (k=3)...")
        labels_nonstd, centroids_nonstd = manual_kmeans(X_nonstd_norm, k=3, seed=42)
        
        # Calculate DBI
        dbi_nonstd = calculate_dbi(X_nonstd_norm, labels_nonstd, centroids_nonstd)
        
        print(f"\n✅ DBI Non-Standard: {dbi_nonstd:.4f}")
        
        # Cluster distribution
        print(f"\nCluster distribution:")
        for i in range(3):
            count = np.sum(labels_nonstd == i)
            print(f"  Cluster {i}: {count} items ({count/len(labels_nonstd)*100:.1f}%)")
        
        # Centroid info
        print(f"\nCentroids (normalized):")
        for i, c in enumerate(centroids_nonstd):
            print(f"  Cluster {i}: [{c[0]:.4f}, {c[1]:.4f}]")
    else:
        print("⚠️  No Non-Standard data")
        dbi_nonstd = 0
        labels_nonstd = np.array([])
    
    # 5. Combined DBI (weighted average)
    print("\n" + "="*80)
    print("📊 COMBINED DBI (WEIGHTED AVERAGE)")
    print("="*80)
    
    n_std = len(df_standard)
    n_nonstd = len(df_non_standard)
    n_total = n_std + n_nonstd
    
    if n_total > 0:
        weight_std = n_std / n_total
        weight_nonstd = n_nonstd / n_total
        
        dbi_combined_weighted = (dbi_std * weight_std) + (dbi_nonstd * weight_nonstd)
        
        print(f"\nStandard DBI: {dbi_std:.4f} (weight: {weight_std:.2%})")
        print(f"Non-Standard DBI: {dbi_nonstd:.4f} (weight: {weight_nonstd:.2%})")
        print(f"\n✅ Combined DBI (weighted): {dbi_combined_weighted:.4f}")
    
    # 6. Compare with DIGABUNG approach
    print("\n" + "="*80)
    print("🔄 COMPARISON: CLUSTERING DIGABUNG (for reference)")
    print("="*80)
    
    X_all = df_agg[['jumlah_terjual', 'total_harga']].values.astype(float)
    X_all_mean = X_all.mean(axis=0)
    X_all_std = X_all.std(axis=0)
    X_all_norm = (X_all - X_all_mean) / (X_all_std + 1e-8)
    
    print(f"\nData shape: {X_all_norm.shape}")
    print(f"Mean: [{X_all_mean[0]:.2f}, {X_all_mean[1]:.2f}]")
    print(f"Std: [{X_all_std[0]:.2f}, {X_all_std[1]:.2f}]")
    
    print("\nRunning K-Means (k=3)...")
    labels_all, centroids_all = manual_kmeans(X_all_norm, k=3, seed=42)
    
    dbi_all = calculate_dbi(X_all_norm, labels_all, centroids_all)
    
    print(f"\n✅ DBI Digabung: {dbi_all:.4f}")
    
    print(f"\nCluster distribution:")
    for i in range(3):
        count = np.sum(labels_all == i)
        print(f"  Cluster {i}: {count} items ({count/len(labels_all)*100:.1f}%)")
    
    # 7. Final comparison
    print("\n" + "="*80)
    print("📊 FINAL COMPARISON")
    print("="*80)
    
    print(f"""
┌─────────────────────────────────────────────────────────────┐
│                    DBI COMPARISON                           │
├─────────────────────────────────────────────────────────────┤
│ Clustering TERPISAH (weighted): {dbi_combined_weighted:.4f}                     │
│   - Standard DBI: {dbi_std:.4f}                                │
│   - Non-Standard DBI: {dbi_nonstd:.4f}                            │
│                                                             │
│ Clustering DIGABUNG: {dbi_all:.4f}                                 │
│                                                             │
│ Selisih: {dbi_combined_weighted - dbi_all:+.4f} ({(dbi_combined_weighted - dbi_all)/dbi_all*100:+.1f}%)                      │
└─────────────────────────────────────────────────────────────┘
    """)
    
    if dbi_combined_weighted > dbi_all:
        print("⚠️  DBI Terpisah LEBIH TINGGI (secara metrik lebih buruk)")
        print("    Tapi interpretasi lebih bermakna untuk bisnis!\n")
    else:
        print("✅ DBI Terpisah LEBIH RENDAH (secara metrik lebih baik)\n")
    
    # 8. Detailed analysis
    print("="*80)
    print("🔍 ANALISIS DETAIL")
    print("="*80)
    
    print(f"""
1. STANDARD CLUSTERING:
   - Jumlah data: {n_std}
   - Range jumlah_terjual: {df_standard['jumlah_terjual'].min():.0f} - {df_standard['jumlah_terjual'].max():.0f}
   - DBI: {dbi_std:.4f}
   - Interpretasi: Cluster dalam kelompok Standard saja

2. NON-STANDARD CLUSTERING:
   - Jumlah data: {n_nonstd}
   - Range jumlah_terjual: {df_non_standard['jumlah_terjual'].min():.0f} - {df_non_standard['jumlah_terjual'].max():.0f}
   - DBI: {dbi_nonstd:.4f}
   - Interpretasi: Cluster dalam kelompok Non-Standard saja

3. DIGABUNG CLUSTERING:
   - Jumlah data: {n_total}
   - Range jumlah_terjual: {df_agg['jumlah_terjual'].min():.0f} - {df_agg['jumlah_terjual'].max():.0f}
   - DBI: {dbi_all:.4f}
   - Interpretasi: Semua data di-cluster bersama

4. KESIMPULAN:
   {"✅ DBI terpisah lebih tinggi karena data lebih homogen dalam kelompok" if dbi_combined_weighted > dbi_all else "✅ DBI terpisah lebih rendah"}
   {"   Separation antar cluster lebih rendah dalam kelompok homogen" if dbi_combined_weighted > dbi_all else ""}
   {"   Ini NORMAL dan EKSPEKTASI untuk clustering domain-specific!" if dbi_combined_weighted > dbi_all else ""}
    """)
    
    print("="*80)
