"""
SOLUSI: Weighted Features untuk mengurangi bias volume sambil menjaga DBI baik

Ide: Beri weight LEBIH BESAR pada total_harga, LEBIH KECIL pada jumlah_terjual
Ini akan mengurangi dominasi volume tanpa perlu memisahkan dataset
"""
from app import create_app
from app.models import Penjualan
from app.processing_kmeans import KMeansManual, davies_bouldin_index_manual, get_size_range
import pandas as pd
import numpy as np

app = create_app()

def test_weighted_clustering(weight_jumlah=1.0, weight_harga=1.0):
    """Test clustering dengan weighted features"""
    
    with app.app_context():
        # Get data
        data = Penjualan.query.all()
        df = pd.DataFrame([{
            'kategori': d.kategori,
            'size': d.size,
            'jumlah_terjual': d.jumlah_terjual,
            'total_harga': float(d.total_harga) if d.total_harga else 0,
        } for d in data])
        
        # Aggregate
        df['size_range'] = df['size'].apply(get_size_range)
        df = df[df['size_range'] != 'Unknown']
        
        df_agg = df.groupby(['kategori', 'size_range']).agg({
            'jumlah_terjual': 'sum',
            'total_harga': 'sum'
        }).reset_index()
        
        # Prepare features with WEIGHTS
        X = df_agg[['jumlah_terjual', 'total_harga']].values.astype(float)
        
        # Apply weights BEFORE normalization
        X_weighted = X.copy()
        X_weighted[:, 0] *= weight_jumlah  # jumlah_terjual
        X_weighted[:, 1] *= weight_harga   # total_harga
        
        # Normalize
        X_mean = X_weighted.mean(axis=0)
        X_std = X_weighted.std(axis=0)
        X_normalized = (X_weighted - X_mean) / (X_std + 1e-8)
        
        # Clustering
        kmeans = KMeansManual(k=3, max_iterations=10, random_state=42)
        kmeans.fit(X_normalized)
        labels = kmeans.labels
        
        # Metrics
        dbi = davies_bouldin_index_manual(X_normalized, labels, kmeans.centroids)
        
        # Analyze
        df_agg['category_type'] = df_agg['kategori'].apply(
            lambda x: 'Standard' if x.lower() in ['standard', 'standar'] else 'Non-Standard'
        )
        
        cluster_counts = [((labels == i).sum()) for i in range(3)]
        
        std_c0 = ((df_agg['category_type'] == 'Standard') & (labels == 0)).sum()
        std_c1 = ((df_agg['category_type'] == 'Standard') & (labels == 1)).sum()
        std_c2 = ((df_agg['category_type'] == 'Standard') & (labels == 2)).sum()
        
        nonstd_c0 = ((df_agg['category_type'] == 'Non-Standard') & (labels == 0)).sum()
        nonstd_c1 = ((df_agg['category_type'] == 'Non-Standard') & (labels == 1)).sum()
        nonstd_c2 = ((df_agg['category_type'] == 'Non-Standard') & (labels == 2)).sum()
        
        return {
            'weight_jumlah': weight_jumlah,
            'weight_harga': weight_harga,
            'dbi': dbi,
            'cluster_counts': cluster_counts,
            'std_distribution': [std_c0, std_c1, std_c2],
            'nonstd_distribution': [nonstd_c0, nonstd_c1, nonstd_c2],
            'inertia': kmeans.inertia,
            'iterations': kmeans.n_iter
        }

print("="*80)
print("TESTING WEIGHTED FEATURES untuk BALANCE antara DBI dan Fairness")
print("="*80)

# Test berbagai kombinasi weight
test_cases = [
    (1.0, 1.0),   # Equal weight (current)
    (1.0, 2.0),   # Harga 2x lebih penting
    (1.0, 3.0),   # Harga 3x lebih penting
    (1.0, 5.0),   # Harga 5x lebih penting
    (0.5, 1.0),   # Jumlah kurangi pengaruh
    (0.3, 1.0),   # Jumlah sangat kurang pengaruh
]

results = []

for w_jumlah, w_harga in test_cases:
    result = test_weighted_clustering(w_jumlah, w_harga)
    results.append(result)

print(f"\n📊 HASIL BERBAGAI WEIGHT COMBINATIONS:")
print(f"\n{'W_Jumlah':<10} {'W_Harga':<10} {'DBI':<8} {'Clusters':<20} {'Std Dist':<20} {'NonStd Dist'}")
print("-"*100)

for r in results:
    std_str = f"[{r['std_distribution'][0]},{r['std_distribution'][1]},{r['std_distribution'][2]}]"
    nonstd_str = f"[{r['nonstd_distribution'][0]},{r['nonstd_distribution'][1]},{r['nonstd_distribution'][2]}]"
    clusters_str = str(r['cluster_counts'])
    
    print(f"{r['weight_jumlah']:<10.1f} {r['weight_harga']:<10.1f} {r['dbi']:<8.4f} {clusters_str:<20} {std_str:<20} {nonstd_str}")

print(f"\n" + "="*80)
print("ANALISIS & REKOMENDASI")
print("="*80)

# Find best trade-off
print(f"\n🎯 Mencari trade-off terbaik:")

for r in results:
    max_cluster = max(r['cluster_counts'])
    min_cluster = min(r['cluster_counts'])
    balance_ratio = max_cluster / min_cluster if min_cluster > 0 else 999
    
    # Check if Non-Standard gets into multiple clusters
    nonstd_in_multiple = sum([1 for x in r['nonstd_distribution'] if x > 0])
    
    if balance_ratio < 20 and nonstd_in_multiple >= 2 and r['dbi'] < 0.65:
        print(f"\n   ✅ GOOD OPTION: Weight({r['weight_jumlah']}, {r['weight_harga']})")
        print(f"      DBI: {r['dbi']:.4f}")
        print(f"      Balance Ratio: {balance_ratio:.1f}x")
        print(f"      Cluster Distribution: {r['cluster_counts']}")
        print(f"      Standard: {r['std_distribution']}")
        print(f"      Non-Standard: {r['nonstd_distribution']}")

print(f"\n💡 REKOMENDASI:")
print(f"""
Berdasarkan hasil testing:

1. Weight(1.0, 2.0) atau Weight(1.0, 3.0) kemungkinan memberikan:
   - DBI masih rendah (< 0.60)
   - Distribusi lebih seimbang
   - Non-Standard tidak semua masuk cluster yang sama

2. Jika masih tidak memuaskan, opsi lain:
   
   a) CLUSTERING TERPISAH dengan penjelasan di skripsi:
      "Meskipun DBI lebih tinggi, pendekatan terpisah dipilih karena:
       - Interpretasi bisnis lebih bermakna
       - Menghindari bias volume yang ekstrem
       - Tier label kontekstual ('Standard Terlaris' vs 'Non-Standard Terlaris')"
   
   b) Gunakan SILHOUETTE SCORE sebagai metrik tambahan:
      - Silhouette bisa lebih adil untuk cluster tidak seimbang
      - Nilai -1 sampai 1 (lebih tinggi lebih baik)
      - Bisa jadi Silhouette terpisah lebih baik meski DBI lebih tinggi

3. Untuk skripsi, ARGUMEN KUAT lebih penting dari DBI rendah!
""")
