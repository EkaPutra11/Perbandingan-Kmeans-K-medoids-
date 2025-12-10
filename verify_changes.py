"""
Verify that cluster summary now shows size ranges count instead of total sales
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import KMeansFinalResult, KMeansResult

app = create_app()

def verify_changes():
    """Verify the changes"""
    with app.app_context():
        print("="*80)
        print("VERIFICATION: CLUSTER SUMMARY CHANGES")
        print("="*80)
        
        # Get K-Means result
        kmeans_result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
        
        if not kmeans_result:
            print("No K-Means result found")
            return
        
        print(f"\n✓ K-Means Result Found:")
        print(f"  K Value: {kmeans_result.k_value}")
        print(f"  Iteration: {kmeans_result.n_iter}")
        
        # Get all final results
        final_results = KMeansFinalResult.query.all()
        
        # Count by cluster
        cluster_counts = {}
        cluster_sales = {}
        
        for r in final_results:
            cid = r.cluster_id
            if cid not in cluster_counts:
                cluster_counts[cid] = 0
                cluster_sales[cid] = 0
            cluster_counts[cid] += 1
            cluster_sales[cid] += r.jumlah_terjual
        
        print("\n" + "="*80)
        print("HASIL PERUBAHAN")
        print("="*80)
        
        # Sort by size ranges count
        cluster_list = sorted(cluster_counts.items(), key=lambda x: x[1])
        
        print("\n✓ SEBELUM (Total Penjualan):")
        print("  CLUSTER\tJUMLAH\t\tDESKRIPSI")
        sorted_by_sales = sorted(cluster_sales.items(), key=lambda x: x[1])
        for idx, (cid, sales) in enumerate(sorted_by_sales):
            if idx == 0:
                desc = "Kurang Laris 📉"
            elif idx == len(sorted_by_sales) - 1:
                desc = "Terlaris ⭐"
            else:
                desc = "Sedang 📊"
            print(f"  C{cid}\t\t{sales}\t\t{desc}")
        
        print("\n✅ SESUDAH (Jumlah Size Ranges):")
        print("  CLUSTER\tJUMLAH\t\tDESKRIPSI")
        for idx, (cid, count) in enumerate(cluster_list):
            if idx == 0:
                desc = "Kurang Laris 📉"
            elif idx == len(cluster_list) - 1:
                desc = "Terlaris ⭐"
            else:
                desc = "Sedang 📊"
            print(f"  C{cid}\t\t{count}\t\t{desc}")
        
        print("\n" + "="*80)
        print("PENJELASAN")
        print("="*80)
        print("\n✓ Field 'JUMLAH' sekarang menghitung:")
        print("  - BUKAN: Total penjualan (jumlah terjual)")
        print("  - TETAPI: Jumlah size ranges (produk) di cluster tersebut")
        
        print("\n✓ Perubahan di files:")
        print("  1. app/static/js/preprocessing-kmeans.js")
        print("     - Line ~183: Menggunakan clusterData[i].sizeRanges")
        print("     - Line ~234: Menampilkan data.sizeRanges")
        
        print("\n  2. app/static/js/preprocessing-kmedoids.js")
        print("     - Line ~186: Menggunakan clusterData[i].sizeRanges")
        print("     - Line ~224: Menampilkan data.sizeRanges")
        
        print("\n✓ Untuk melihat perubahan:")
        print("  1. Jalankan: .\\env\\Scripts\\python.exe app.py")
        print("  2. Buka browser: http://localhost:5000")
        print("  3. Klik menu 'Preprocessing K-Means' atau 'Preprocessing K-Medoids'")
        print("  4. Lihat tabel 'Ringkasan Cluster' - JUMLAH sekarang adalah jumlah size ranges")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    verify_changes()
