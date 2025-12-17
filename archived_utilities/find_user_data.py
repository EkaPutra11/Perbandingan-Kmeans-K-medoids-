"""
Search for K-Means result that matches user's data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import KMeansResult, KMeansClusterDetail

app = create_app()

def find_matching_result():
    """Find K-Means result that matches user's cluster totals"""
    with app.app_context():
        print("="*80)
        print("SEARCHING FOR K-MEANS RESULT MATCHING USER DATA")
        print("="*80)
        print("\nUser's Data:")
        print("  C0: 1194 unit")
        print("  C1: 3174 unit")
        print("  C2: 1372 unit")
        print("  Total: 5740 unit")
        
        # Get all K-Means results
        all_results = KMeansResult.query.order_by(KMeansResult.created_at.desc()).all()
        
        print(f"\n✓ Found {len(all_results)} K-Means results in database")
        
        found = False
        
        for result in all_results:
            # Get cluster details for this result
            details = KMeansClusterDetail.query.filter_by(kmeans_result_id=result.id).all()
            
            # Calculate totals per cluster
            cluster_totals = {}
            for detail in details:
                cid = detail.cluster_id
                if cid not in cluster_totals:
                    cluster_totals[cid] = 0
                cluster_totals[cid] += detail.jumlah_terjual
            
            # Check if it matches user's data
            matches = (
                cluster_totals.get(0, 0) == 1194 and
                cluster_totals.get(1, 0) == 3174 and
                cluster_totals.get(2, 0) == 1372
            )
            
            print(f"\n{'='*80}")
            print(f"Result ID: {result.id}")
            print(f"K Value: {result.k_value}")
            print(f"Iterations: {result.n_iter}")
            print(f"DBI: {result.davies_bouldin_index:.4f}")
            print(f"Created: {result.created_at}")
            print(f"Cluster totals: {cluster_totals}")
            
            if matches:
                print("\n✓✓✓ THIS IS THE MATCHING RESULT! ✓✓✓")
                found = True
                
                print("\n" + "="*80)
                print("ANSWER:")
                print("="*80)
                print(f"Data cluster Anda berasal dari:")
                print(f"  - K Value: {result.k_value}")
                print(f"  - Iterasi ke-{result.n_iter}")
                print(f"  - Davies-Bouldin Index: {result.davies_bouldin_index:.4f}")
                print(f"  - Inertia: {result.inertia:.4f}")
                print(f"  - Total Samples: {result.n_samples}")
                print(f"  - Created: {result.created_at}")
                
                print("\n" + "="*80)
                print("CLUSTER DETAILS:")
                print("="*80)
                
                # Sort by total for description
                cluster_list = [
                    {'id': 0, 'total': 1194},
                    {'id': 1, 'total': 3174},
                    {'id': 2, 'total': 1372}
                ]
                cluster_list.sort(key=lambda x: x['total'])
                
                print("\nSorted by jumlah terjual:")
                for idx, c in enumerate(cluster_list):
                    if idx == 0:
                        desc = "Kurang Laris 📉"
                    elif idx == len(cluster_list) - 1:
                        desc = "Terlaris ⭐"
                    else:
                        desc = "Sedang 📊"
                    percentage = (c['total'] / 5740) * 100
                    print(f"  C{c['id']}: {c['total']} unit ({percentage:.1f}%) - {desc}")
                
                print("\nSesuai dengan data Anda:")
                print("  C0: 1194 - Kurang Laris 📉")
                print("  C1: 3174 - Terlaris ⭐")
                print("  C2: 1372 - Sedang 📊")
                
                break
        
        if not found:
            print("\n" + "="*80)
            print("⚠️ NO EXACT MATCH FOUND")
            print("="*80)
            print("\nData Anda tidak ditemukan di database yang ada.")
            print("Kemungkinan:")
            print("  1. Data dari run sebelumnya yang sudah dihapus")
            print("  2. Data dari environment/database berbeda")
            print("  3. Data sudah di-overwrite dengan run terbaru")
            
            print("\n✓ Data terbaru di database:")
            latest = all_results[0] if all_results else None
            if latest:
                details = KMeansClusterDetail.query.filter_by(kmeans_result_id=latest.id).all()
                cluster_totals = {}
                for detail in details:
                    cid = detail.cluster_id
                    if cid not in cluster_totals:
                        cluster_totals[cid] = 0
                    cluster_totals[cid] += detail.jumlah_terjual
                
                print(f"  K={latest.k_value}, Iterasi={latest.n_iter}")
                for cid in sorted(cluster_totals.keys()):
                    print(f"  C{cid}: {cluster_totals[cid]} unit")

if __name__ == "__main__":
    find_matching_result()
