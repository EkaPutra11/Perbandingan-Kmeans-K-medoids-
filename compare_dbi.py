"""
Compare DBI: Clustering Terpisah vs Digabung
"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual
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

def aggregate_data_by_size_range(df):
    df['size_range'] = df['size'].apply(get_size_range)
    df = df[df['size_range'] != 'Unknown'].copy()
    
    aggregated = df.groupby(['kategori', 'size_range']).agg({
        'jumlah_terjual': 'sum',
        'total_harga': 'sum'
    }).reset_index()
    
    return aggregated

def davies_bouldin_index_manual(X, labels, centroids):
    n_clusters = len(np.unique(labels))
    
    if n_clusters <= 1:
        return 0.0

    S = np.zeros(n_clusters)
    for i in range(n_clusters):
        cluster_points = X[labels == i]
        if len(cluster_points) > 0:
            S[i] = np.mean(np.linalg.norm(cluster_points - centroids[i], axis=1))

    db_index = 0.0
    for i in range(n_clusters):
        max_ratio = 0.0
        for j in range(n_clusters):
            if i != j:
                centroid_distance = np.linalg.norm(centroids[i] - centroids[j])
                if centroid_distance > 0:
                    ratio = (S[i] + S[j]) / centroid_distance
                    max_ratio = max(max_ratio, ratio)
        db_index += max_ratio

    return db_index / n_clusters

with app.app_context():
    print("="*80)
    print("PERBANDINGAN DBI: CLUSTERING TERPISAH vs DIGABUNG")
    print("="*80)
    
    # Get data
    data = Penjualan.query.all()
    df = pd.DataFrame([{
        'kategori': d.kategori,
        'size': d.size,
        'jumlah_terjual': d.jumlah_terjual,
        'total_harga': float(d.total_harga) if d.total_harga else 0,
    } for d in data])
    
    df_aggregated = aggregate_data_by_size_range(df)
    
    print(f"\nTotal data: {len(df_aggregated)} records")
    
    # Test dengan clustering terpisah (yang sekarang)
    print("\n" + "="*80)
    print("1️⃣  CLUSTERING TERPISAH (Current Implementation)")
    print("="*80)
    result_separated = process_kmeans_manual(k=3)
    
    if result_separated:
        print(f"\n✅ DBI (Terpisah): {result_separated['davies_bouldin']:.4f}")
        print(f"   Inertia: {result_separated['inertia']:.4f}")
        print(f"   Iterations: {result_separated['n_iter']}")
        
        # Show cluster distribution
        labels = result_separated['labels']
        print(f"\n   Cluster Distribution:")
        for i in range(3):
            count = int(np.sum(labels == i))
            print(f"     Cluster {i}: {count} items ({count/len(labels)*100:.1f}%)")
    
    # Simulate clustering digabung (old way)
    print("\n" + "="*80)
    print("2️⃣  CLUSTERING DIGABUNG (Old Implementation - for comparison)")
    print("="*80)
    
    from app.processing_kmeans import KMeansManual
    
    # Prepare features (combined)
    X_combined = df_aggregated[['jumlah_terjual', 'total_harga']].values.astype(float)
    X_mean_combined = X_combined.mean(axis=0)
    X_std_combined = X_combined.std(axis=0)
    X_normalized_combined = (X_combined - X_mean_combined) / (X_std_combined + 1e-8)
    
    # Clustering combined
    kmeans_combined = KMeansManual(k=3, max_iterations=10, random_state=42)
    kmeans_combined.fit(X_normalized_combined)
    
    # Calculate DBI for combined
    dbi_combined = davies_bouldin_index_manual(X_normalized_combined, 
                                                kmeans_combined.labels, 
                                                kmeans_combined.centroids)
    
    print(f"\n✅ DBI (Digabung): {dbi_combined:.4f}")
    print(f"   Inertia: {kmeans_combined.inertia:.4f}")
    print(f"   Iterations: {kmeans_combined.n_iter}")
    
    # Show cluster distribution
    print(f"\n   Cluster Distribution:")
    for i in range(3):
        count = int(np.sum(kmeans_combined.labels == i))
        print(f"     Cluster {i}: {count} items ({count/len(kmeans_combined.labels)*100:.1f}%)")
    
    # Comparison
    print("\n" + "="*80)
    print("📊 PERBANDINGAN HASIL")
    print("="*80)
    
    if result_separated:
        dbi_diff = result_separated['davies_bouldin'] - dbi_combined
        dbi_pct = (dbi_diff / dbi_combined) * 100
        
        print(f"\nDBI Terpisah: {result_separated['davies_bouldin']:.4f}")
        print(f"DBI Digabung: {dbi_combined:.4f}")
        print(f"Selisih: {dbi_diff:+.4f} ({dbi_pct:+.1f}%)")
        
        if dbi_diff > 0:
            print(f"\n⚠️  DBI Terpisah LEBIH TINGGI (lebih buruk) {abs(dbi_pct):.1f}%")
        else:
            print(f"\n✅ DBI Terpisah LEBIH RENDAH (lebih baik) {abs(dbi_pct):.1f}%")
    
    # Analysis
    print("\n" + "="*80)
    print("🔍 ANALISIS")
    print("="*80)
    
    print("""
KENAPA DBI TERPISAH LEBIH TINGGI (BURUK)?

1. RANGE DATA LEBIH KECIL:
   - Standard: 67-1372 unit (range: 1305)
   - Non-Standard: 1-107 unit (range: 106)
   - Dalam kelompok kecil, cluster lebih overlap
   
2. SEPARATION ANTAR CLUSTER LEBIH RENDAH:
   - Di Standard saja: semua data punya volume tinggi
   - Di Non-Standard saja: semua data punya volume rendah
   - Jarak antar cluster dalam 1 kelompok lebih kecil
   
3. SCATTER DALAM CLUSTER LEBIH BESAR:
   - Karena normalisasi per kelompok
   - Variasi dalam cluster jadi lebih terlihat

4. SAAT DIGABUNG:
   - Range data: 1-1372 unit (range: 1371)
   - Cluster sangat terpisah (Standard vs Non-Standard)
   - Separation tinggi → DBI rendah (baik secara metrik)

APAKAH INI MASALAH?

❌ BUKAN MASALAH! Ini justru EKSPEKTASI NORMAL:

- DBI mengukur separation vs scatter
- Clustering terpisah: data lebih homogen dalam kelompok
  → Cluster lebih overlap → DBI lebih tinggi
  → TAPI interpretasi LEBIH BERGUNA untuk bisnis!

- Clustering digabung: data sangat heterogen
  → Cluster sangat terpisah → DBI lebih rendah
  → TAPI interpretasi MENYESATKAN (bias ke Standard)!

KESIMPULAN:

✅ DBI RENDAH ≠ CLUSTERING LEBIH BAIK untuk analisis bisnis
✅ Clustering terpisah LEBIH BERMAKNA meskipun DBI lebih tinggi
✅ Untuk skripsi: jelaskan trade-off antara metrik vs interpretasi
    """)
    
    print("\n" + "="*80)
