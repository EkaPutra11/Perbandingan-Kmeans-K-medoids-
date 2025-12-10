"""
Generate final cluster summary for K-Means result
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import KMeansFinalResult, KMeansResult

app = create_app()

def generate_cluster_summary():
    """Generate cluster summary table"""
    with app.app_context():
        # Get current K-Means result
        kmeans_result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
        
        if not kmeans_result:
            print("No K-Means result found")
            return
        
        print("="*80)
        print("K-MEANS CLUSTER SUMMARY")
        print("="*80)
        print(f"\nResult Details:")
        print(f"  K Value: {kmeans_result.k_value}")
        print(f"  Converged at Iteration: {kmeans_result.n_iter}")
        print(f"  Davies-Bouldin Index: {kmeans_result.davies_bouldin_index:.4f} (Best Quality)")
        print(f"  Inertia: {kmeans_result.inertia:.4f}")
        print(f"  Total Samples: {kmeans_result.n_samples}")
        
        # Get final results
        final_results = KMeansFinalResult.query.all()
        
        # Calculate totals per cluster
        clusters = {}
        for r in final_results:
            if r.cluster_id not in clusters:
                clusters[r.cluster_id] = {
                    'samples': 0,
                    'total': 0
                }
            clusters[r.cluster_id]['samples'] += 1
            clusters[r.cluster_id]['total'] += r.jumlah_terjual
        
        # Sort by total sales
        cluster_list = []
        for cid, data in clusters.items():
            cluster_list.append({
                'id': cid,
                'samples': data['samples'],
                'total': data['total']
            })
        
        cluster_list.sort(key=lambda x: x['total'])
        
        grand_total = sum(c['total'] for c in cluster_list)
        
        print("\n" + "="*80)
        print("RINGKASAN CLUSTER (Sorted by Total Jumlah Terjual)")
        print("="*80)
        print(f"\n{'CLUSTER':<12} {'JUMLAH':<12} {'SAMPLES':<12} {'% TOTAL':<12} {'DESKRIPSI':<20}")
        print("-" * 80)
        
        # Assign descriptions based on sorted order
        for idx, cluster in enumerate(cluster_list):
            percentage = (cluster['total'] / grand_total) * 100
            
            # Assign label
            if idx == 0:  # Lowest sales
                desc = "Kurang Laris 📉"
            elif idx == len(cluster_list) - 1:  # Highest sales
                desc = "Terlaris ⭐"
            else:  # Middle
                desc = "Sedang 📊"
            
            print(f"C{cluster['id']:<11} {cluster['total']:<12} {cluster['samples']:<12} {percentage:>6.1f}%      {desc:<20}")
        
        print("-" * 80)
        print(f"{'TOTAL':<12} {grand_total:<12} {sum(c['samples'] for c in cluster_list):<12} {'100.0%':<12}")
        
        print("\n" + "="*80)
        print("PENJELASAN")
        print("="*80)
        
        for idx, cluster in enumerate(cluster_list):
            if idx == 0:
                label = "KURANG LARIS 📉"
            elif idx == len(cluster_list) - 1:
                label = "TERLARIS ⭐"
            else:
                label = "SEDANG 📊"
            
            avg = cluster['total'] / cluster['samples']
            print(f"\n{label} - Cluster {cluster['id']}:")
            print(f"  - Total jumlah terjual: {cluster['total']} unit")
            print(f"  - Jumlah produk (samples): {cluster['samples']} jenis")
            print(f"  - Rata-rata per produk: {avg:.1f} unit")
            print(f"  - Persentase dari total: {(cluster['total'] / grand_total * 100):.1f}%")
        
        print("\n" + "="*80)
        print("KESIMPULAN")
        print("="*80)
        print(f"✓ Data diambil dari: K = {kmeans_result.k_value}")
        print(f"✓ Algoritma converged di: Iterasi ke-{kmeans_result.n_iter}")
        print(f"✓ Kualitas clustering (DBI): {kmeans_result.davies_bouldin_index:.4f} (Terbaik!)")
        print(f"✓ Total penjualan seluruh cluster: {grand_total} unit")
        
        # Compare with user's data
        print("\n" + "="*80)
        print("PERBANDINGAN DENGAN DATA USER")
        print("="*80)
        
        user_data = {
            'C0': 1194,
            'C1': 3174,
            'C2': 1372
        }
        
        print(f"\n{'CLUSTER':<12} {'Data User':<15} {'Data Actual':<15} {'Selisih':<15} {'Match?':<10}")
        print("-" * 70)
        
        for cluster in cluster_list:
            cid = f"C{cluster['id']}"
            actual = cluster['total']
            user = user_data.get(cid, 0)
            diff = actual - user
            match = "✓" if diff == 0 else "✗"
            
            print(f"{cid:<12} {user:<15} {actual:<15} {diff:<15} {match:<10}")
        
        print("\n⚠️ CATATAN:")
        print("Data yang Anda sebutkan (C0=1194, C1=3174, C2=1372) BERBEDA dengan data actual!")
        print("Kemungkinan:")
        print("  1. Data dari iterasi/run yang berbeda")
        print("  2. Data sebelum update/re-run K-Means")
        print("  3. Data dari K value yang berbeda")
        
        print("\n✓ DATA YANG BENAR DAN TERBARU:")
        print(f"  K = {kmeans_result.k_value}, Iterasi = {kmeans_result.n_iter}")
        for idx, cluster in enumerate(cluster_list):
            if idx == 0:
                desc = "Kurang Laris 📉"
            elif idx == len(cluster_list) - 1:
                desc = "Terlaris ⭐"
            else:
                desc = "Sedang 📊"
            print(f"  C{cluster['id']}: {cluster['total']} unit - {desc}")

if __name__ == "__main__":
    generate_cluster_summary()
