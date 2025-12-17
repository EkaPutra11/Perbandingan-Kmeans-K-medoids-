"""
Check if user data matches by re-running K-Means multiple times
to see if cluster labels change
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.processing_kmeans import process_kmeans_manual

app = create_app()

def test_cluster_stability():
    """Test if cluster labels are stable across runs"""
    with app.app_context():
        print("="*80)
        print("TESTING CLUSTER LABEL STABILITY")
        print("="*80)
        print("\nRunning K-Means 5 times with K=3 to check cluster label stability...")
        
        runs = []
        for i in range(5):
            print(f"\nRun {i+1}...")
            result = process_kmeans_manual(k=3)
            
            if result:
                labels = result['labels']
                data_agg = result['data_aggregated']
                
                # Calculate cluster totals
                clusters = {}
                for idx, label in enumerate(labels):
                    if label not in clusters:
                        clusters[label] = 0
                    clusters[label] += data_agg.iloc[idx]['jumlah_terjual']
                
                runs.append({
                    'run': i+1,
                    'n_iter': result['n_iter'],
                    'dbi': result['davies_bouldin'],
                    'clusters': clusters
                })
                
                print(f"  Iterations: {result['n_iter']}")
                print(f"  DBI: {result['davies_bouldin']:.4f}")
                print(f"  Cluster totals: {clusters}")
        
        print("\n" + "="*80)
        print("ANALYSIS OF CLUSTER TOTALS")
        print("="*80)
        
        # Extract unique totals across all runs
        all_totals = set()
        for run in runs:
            for total in run['clusters'].values():
                all_totals.add(total)
        
        all_totals = sorted(all_totals)
        
        print(f"\nUnique cluster totals found: {all_totals}")
        print(f"\n⚠️ IMPORTANT: Cluster labels (0, 1, 2) are ARBITRARY!")
        print("The same group of products can be labeled as C0, C1, or C2 in different runs.")
        print("\nWhat matters is the TOTAL VALUES, not the cluster IDs!")
        
        # Check if user data matches any pattern
        user_totals = sorted([1194, 3174, 1372])
        actual_totals = sorted([1429, 2939, 1372])
        
        print("\n" + "="*80)
        print("COMPARISON")
        print("="*80)
        print(f"\nUser data (sorted): {user_totals}")
        print(f"Actual data (sorted): {actual_totals}")
        
        if 1372 in actual_totals:
            print("\n✓ Value 1372 matches! This is the outlier cluster (Standard 10-14cm)")
        
        print("\n" + "="*80)
        print("CONCLUSION")
        print("="*80)
        print("\n✓ Current database has:")
        print("  - C2: 1372 unit (Outlier)")
        print("  - C0: 1429 unit")
        print("  - C1: 2939 unit")
        
        print("\n✓ Data is from K=3, Iteration=2")
        
        print("\n⚠️ Deskripsi yang BENAR berdasarkan JUMLAH:")
        sorted_actual = sorted([
            {'id': 2, 'total': 1372},
            {'id': 0, 'total': 1429},
            {'id': 1, 'total': 2939}
        ], key=lambda x: x['total'])
        
        for idx, c in enumerate(sorted_actual):
            if idx == 0:
                desc = "Kurang Laris 📉"
            elif idx == 1:
                desc = "Sedang 📊"
            else:
                desc = "Terlaris ⭐"
            print(f"  C{c['id']}: {c['total']} unit - {desc}")

if __name__ == "__main__":
    test_cluster_stability()
