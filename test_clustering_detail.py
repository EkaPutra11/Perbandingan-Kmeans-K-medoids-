"""
Test clustering dan bandingkan hasil DETAIL untuk melihat perbedaan
"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual
import pandas as pd

app = create_app()

with app.app_context():
    print("="*80)
    print("TEST CLUSTERING DENGAN 2 FITUR (jumlah_terjual + total_harga)")
    print("="*80)
    
    # Run clustering
    result = process_kmeans_manual(k=3)
    
    if not result:
        print("❌ Clustering gagal!")
    else:
        print(f"\n✅ Clustering berhasil!")
        print(f"\n📊 Metrics:")
        print(f"   Inertia: {result['inertia']:.2f}")
        print(f"   DBI: {result['davies_bouldin']:.4f}")
        print(f"   Iterations: {result['n_iter']}")
        print(f"   Samples: {result['n_samples']}")
        
        # Analyze clusters
        df = result['data_aggregated']
        labels = result['labels']
        
        print(f"\n📦 Distribusi Cluster:")
        for cluster_id in range(3):
            count = (labels == cluster_id).sum()
            print(f"   Cluster {cluster_id}: {count} items ({count/len(labels)*100:.1f}%)")
        
        # Show sample from each cluster
        print(f"\n🔍 Sample dari setiap cluster:")
        for cluster_id in range(3):
            df_cluster = df[labels == cluster_id].copy()
            
            print(f"\n   CLUSTER {cluster_id} ({len(df_cluster)} items):")
            print(f"   {'Kategori':<20} {'Size Range':<15} {'Jumlah':>10} {'Total Harga':>20}")
            print("   " + "-"*70)
            
            # Show top 3 by jumlah_terjual
            df_cluster_sorted = df_cluster.sort_values('jumlah_terjual', ascending=False)
            for i, (idx, row) in enumerate(df_cluster_sorted.head(3).iterrows()):
                print(f"   {row['kategori']:<20} {row['size_range']:<15} {row['jumlah_terjual']:>10} {row['total_harga']:>20,.0f}")
        
        # Check by category type
        df['category_type'] = df['kategori'].apply(
            lambda x: 'Standard' if x.lower() in ['standard', 'standar'] else 'Non-Standard'
        )
        
        print(f"\n📊 Distribusi berdasarkan Category Type:")
        print(f"\n   {'Category':<15} {'Cluster 0':>12} {'Cluster 1':>12} {'Cluster 2':>12} {'Total':>10}")
        print("   " + "-"*65)
        
        for cat_type in ['Standard', 'Non-Standard']:
            df_cat = df[df['category_type'] == cat_type]
            c0 = ((df['category_type'] == cat_type) & (labels == 0)).sum()
            c1 = ((df['category_type'] == cat_type) & (labels == 1)).sum()
            c2 = ((df['category_type'] == cat_type) & (labels == 2)).sum()
            total = c0 + c1 + c2
            print(f"   {cat_type:<15} {c0:>12} {c1:>12} {c2:>12} {total:>10}")
        
        # Check centroid characteristics
        print(f"\n🎯 Karakteristik Centroid (normalized):")
        centroids = result['centroids']
        X_mean = result['X_mean']
        X_std = result['X_std']
        
        print(f"\n   {'Cluster':<10} {'Norm Jumlah':>15} {'Norm Harga':>15} {'Score':>10}")
        print("   " + "-"*55)
        for i, centroid in enumerate(centroids):
            score = centroid.sum()
            print(f"   Cluster {i:<2} {centroid[0]:>15.4f} {centroid[1]:>15.4f} {score:>10.4f}")
        
        # Denormalize centroids
        print(f"\n🎯 Karakteristik Centroid (original scale):")
        print(f"\n   {'Cluster':<10} {'Avg Jumlah':>15} {'Avg Harga':>20}")
        print("   " + "-"*50)
        for i, centroid in enumerate(centroids):
            orig_jumlah = centroid[0] * X_std[0] + X_mean[0]
            orig_harga = centroid[1] * X_std[1] + X_mean[1]
            print(f"   Cluster {i:<2} {orig_jumlah:>15.1f} {orig_harga:>20,.0f}")
        
        # Show tier assignment
        analysis = result['analysis']
        
        print(f"\n📈 Tier Assignment (berdasarkan cluster):")
        tier_counts = {'terlaris': 0, 'sedang': 0, 'kurang_laris': 0}
        
        for cat_type in ['standard', 'non_standard']:
            if cat_type in analysis:
                for key, data in analysis[cat_type].items():
                    if 'tier' in data:
                        tier_counts[data['tier']] += 1
        
        print(f"   Terlaris: {tier_counts.get('terlaris', 0)}")
        print(f"   Sedang: {tier_counts.get('sedang', 0)}")
        print(f"   Kurang Laris: {tier_counts.get('kurang_laris', 0)}")
        
        # Identify potential issues
        print(f"\n⚠️  ANALISIS POTENSI MASALAH:")
        
        # Check if Standard dominates Cluster 0
        df_std_c0 = ((df['category_type'] == 'Standard') & (labels == 0)).sum()
        df_nonstd_c0 = ((df['category_type'] == 'Non-Standard') & (labels == 0)).sum()
        
        if df_std_c0 > 0 and df_nonstd_c0 == 0:
            print(f"   ⚠️  Cluster 0 hanya berisi Standard ({df_std_c0} items)")
            print(f"       Non-Standard tidak ada yang masuk Cluster 0 (Terlaris)")
            print(f"       Ini menunjukkan BIAS masih ada!")
        elif df_nonstd_c0 > 0:
            print(f"   ✅ Cluster 0 berisi Standard ({df_std_c0}) dan Non-Standard ({df_nonstd_c0})")
            print(f"       Bias berkurang, total_harga membantu!")
        
        # Check extreme imbalance
        cluster_counts = [((labels == i).sum()) for i in range(3)]
        max_count = max(cluster_counts)
        min_count = min(cluster_counts)
        
        if max_count / min_count > 10:
            print(f"   ⚠️  Cluster sangat tidak seimbang: {cluster_counts}")
            print(f"       Rasio max/min: {max_count/min_count:.1f}x")
        else:
            print(f"   ✅ Cluster relatif seimbang: {cluster_counts}")
        
        print(f"\n" + "="*80)
        print("KESIMPULAN:")
        print("="*80)
        print(f"""
DBI = {result['davies_bouldin']:.4f}

Nilai DBI sekitar 0.48 menunjukkan clustering cukup baik.

Untuk memastikan total_harga benar berpengaruh:
1. Lihat karakteristik centroid - apakah ada perbedaan signifikan di harga?
2. Lihat distribusi Standard vs Non-Standard per cluster
3. Jika masih bias, pertimbangkan:
   - Menambah weight pada total_harga
   - Atau gunakan clustering terpisah (Standard vs Non-Standard)

DBI yang baik (rendah) TIDAK selalu berarti clustering adil!
DBI bisa rendah karena Standard mendominasi satu cluster besar yang homogen.
        """)
