"""
Calculate cluster summary based on NUMBER OF SAMPLES (size ranges), not total sales
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import KMeansFinalResult, KMeansResult

app = create_app()

def calculate_by_samples():
    """Calculate cluster summary by number of samples/size ranges"""
    with app.app_context():
        # Get K-Means result
        kmeans_result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
        
        if not kmeans_result:
            print("No K-Means result found")
            return
        
        print("="*80)
        print("K-MEANS CLUSTER SUMMARY - BY NUMBER OF SAMPLES")
        print("="*80)
        print(f"\nK Value: {kmeans_result.k_value}")
        print(f"Iteration: {kmeans_result.n_iter}")
        print(f"DBI: {kmeans_result.davies_bouldin_index:.4f}")
        
        # Get all final results
        final_results = KMeansFinalResult.query.all()
        
        # Count samples per cluster
        cluster_counts = {}
        cluster_sales = {}
        
        for r in final_results:
            cid = r.cluster_id
            
            # Count samples
            if cid not in cluster_counts:
                cluster_counts[cid] = 0
            cluster_counts[cid] += 1
            
            # Also track total sales for reference
            if cid not in cluster_sales:
                cluster_sales[cid] = 0
            cluster_sales[cid] += r.jumlah_terjual
        
        print("\n" + "="*80)
        print("RAW DATA PER CLUSTER")
        print("="*80)
        
        for cid in sorted(cluster_counts.keys()):
            print(f"\nCluster {cid}:")
            print(f"  - Jumlah samples (size ranges): {cluster_counts[cid]}")
            print(f"  - Total penjualan: {cluster_sales[cid]} unit")
            print(f"  - Rata-rata per sample: {cluster_sales[cid] / cluster_counts[cid]:.1f} unit")
        
        # Sort by number of samples
        cluster_list = []
        for cid in cluster_counts.keys():
            cluster_list.append({
                'id': cid,
                'samples': cluster_counts[cid],
                'sales': cluster_sales[cid]
            })
        
        cluster_list.sort(key=lambda x: x['samples'])
        
        total_samples = sum(c['samples'] for c in cluster_list)
        total_sales = sum(c['sales'] for c in cluster_list)
        
        print("\n" + "="*80)
        print("RINGKASAN CLUSTER (Sorted by Jumlah Samples)")
        print("="*80)
        print(f"\n{'CLUSTER':<12} {'JUMLAH':<12} {'% TOTAL':<12} {'DESKRIPSI':<20}")
        print("-" * 70)
        
        # Assign descriptions based on NUMBER OF SAMPLES
        for idx, cluster in enumerate(cluster_list):
            percentage = (cluster['samples'] / total_samples) * 100
            
            # Assign label based on number of samples
            if idx == 0:  # Fewest samples
                desc = "Kurang Laris 📉"
            elif idx == len(cluster_list) - 1:  # Most samples
                desc = "Terlaris ⭐"
            else:  # Middle
                desc = "Sedang 📊"
            
            print(f"C{cluster['id']:<11} {cluster['samples']:<12} {percentage:>6.1f}%      {desc:<20}")
        
        print("-" * 70)
        print(f"{'TOTAL':<12} {total_samples:<12} {'100.0%':<12}")
        
        print("\n" + "="*80)
        print("TABEL FINAL")
        print("="*80)
        print(f"\n{'CLUSTER':<15} {'JUMLAH':<15} {'DESKRIPSI':<20}")
        print("-" * 50)
        
        for idx, cluster in enumerate(cluster_list):
            if idx == 0:
                desc = "Kurang Laris 📉"
            elif idx == len(cluster_list) - 1:
                desc = "Terlaris ⭐"
            else:
                desc = "Sedang 📊"
            
            print(f"C{cluster['id']:<14} {cluster['samples']:<15} {desc:<20}")
        
        print("\n" + "="*80)
        print("PENJELASAN DETAIL")
        print("="*80)
        
        for idx, cluster in enumerate(cluster_list):
            if idx == 0:
                label = "KURANG LARIS 📉"
            elif idx == len(cluster_list) - 1:
                label = "TERLARIS ⭐"
            else:
                label = "SEDANG 📊"
            
            print(f"\n{label} - Cluster {cluster['id']}:")
            print(f"  - Jumlah size ranges: {cluster['samples']} produk")
            print(f"  - Persentase: {(cluster['samples'] / total_samples * 100):.1f}%")
            print(f"  - Total penjualan: {cluster['sales']} unit")
            print(f"  - Rata-rata penjualan per produk: {cluster['sales'] / cluster['samples']:.1f} unit")
        
        print("\n" + "="*80)
        print("KESIMPULAN")
        print("="*80)
        print(f"\n✓ Data dari: K = {kmeans_result.k_value}, Iterasi = {kmeans_result.n_iter}")
        print(f"✓ Total size ranges: {total_samples} produk")
        print(f"✓ Total penjualan: {total_sales} unit")
        print("\n✓ JUMLAH = Jumlah size ranges (produk) di cluster tersebut")
        print("✓ BUKAN total penjualan!")
        
        # Show the correct table format
        print("\n" + "="*80)
        print("TABEL YANG BENAR:")
        print("="*80)
        print("\nCLUSTER\tJUMLAH\tDESKRIPSI")
        for idx, cluster in enumerate(cluster_list):
            if idx == 0:
                desc = "Kurang Laris 📉"
            elif idx == len(cluster_list) - 1:
                desc = "Terlaris ⭐"
            else:
                desc = "Sedang 📊"
            print(f"C{cluster['id']}\t{cluster['samples']}\t{desc}")

if __name__ == "__main__":
    calculate_by_samples()
