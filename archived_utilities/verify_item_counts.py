"""
Verify that cluster summary now correctly counts all kategori+size combinations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.processing_kmeans import process_kmeans_manual

app = create_app()

def verify_item_counts():
    """Verify item counts in analysis"""
    with app.app_context():
        print("="*80)
        print("VERIFICATION: CLUSTER COUNT FIX")
        print("="*80)
        
        # Run clustering
        result = process_kmeans_manual(k=3)
        
        if not result:
            print("Failed to run K-Means")
            return
        
        analysis = result['analysis']
        labels = result['labels']
        data_agg = result['data_aggregated']
        
        print(f"\nTotal aggregated data: {len(data_agg)} rows")
        print(f"Total labels: {len(labels)}")
        
        # Count by cluster from labels
        cluster_counts_actual = {}
        for label in labels:
            if label not in cluster_counts_actual:
                cluster_counts_actual[label] = 0
            cluster_counts_actual[label] += 1
        
        print("\n" + "="*80)
        print("ACTUAL CLUSTER COUNTS (from labels)")
        print("="*80)
        for cid in sorted(cluster_counts_actual.keys()):
            print(f"  C{cid}: {cluster_counts_actual[cid]} items")
        
        # Count from analysis structure
        print("\n" + "="*80)
        print("ANALYSIS STRUCTURE BREAKDOWN")
        print("="*80)
        
        cluster_items_from_analysis = {0: 0, 1: 0, 2: 0}
        
        if 'standard' in analysis:
            print(f"\nStandard data: {len(analysis['standard'])} unique size ranges")
            for size_range, data in analysis['standard'].items():
                item_count = len(data['items']) if 'items' in data else 1
                cluster_id = data.get('dominant_cluster', data.get('cluster_id', -1))
                if cluster_id != -1:
                    cluster_items_from_analysis[cluster_id] += item_count
                print(f"  {size_range}: {item_count} items -> Cluster {cluster_id}")
        
        if 'non_standard' in analysis:
            print(f"\nNon-Standard data: {len(analysis['non_standard'])} unique size ranges")
            for size_range, data in analysis['non_standard'].items():
                item_count = len(data['items']) if 'items' in data else 1
                cluster_id = data.get('dominant_cluster', data.get('cluster_id', -1))
                if cluster_id != -1:
                    cluster_items_from_analysis[cluster_id] += item_count
                print(f"  {size_range}: {item_count} items -> Cluster {cluster_id}")
        
        print("\n" + "="*80)
        print("CLUSTER COUNTS FROM ANALYSIS (should match actual)")
        print("="*80)
        for cid in sorted(cluster_items_from_analysis.keys()):
            actual = cluster_counts_actual.get(cid, 0)
            from_analysis = cluster_items_from_analysis[cid]
            match = "✓" if actual == from_analysis else "✗"
            print(f"  C{cid}: {from_analysis} items (actual: {actual}) {match}")
        
        print("\n" + "="*80)
        print("EXPECTED RESULT IN UI")
        print("="*80)
        print("\nCLUSTER\tJUMLAH\tDESKRIPSI")
        
        # Sort by count
        sorted_clusters = sorted(cluster_counts_actual.items(), key=lambda x: x[1])
        
        for idx, (cid, count) in enumerate(sorted_clusters):
            if idx == 0:
                desc = "Kurang Laris 📉"
            elif idx == len(sorted_clusters) - 1:
                desc = "Terlaris ⭐"
            else:
                desc = "Sedang 📊"
            print(f"C{cid}\t{count}\t{desc}")
        
        print("\n" + "="*80)
        print("VERIFICATION RESULT")
        print("="*80)
        
        all_match = all(
            cluster_counts_actual.get(cid, 0) == cluster_items_from_analysis[cid]
            for cid in cluster_counts_actual.keys()
        )
        
        if all_match:
            print("\n✓ SUCCESS! Counts match!")
            print("  JavaScript will now correctly count all kategori+size combinations")
            print("  because it uses data.items.length")
        else:
            print("\n✗ MISMATCH! There's still an issue")
            print("  Need to check the analysis structure")

if __name__ == "__main__":
    verify_item_counts()
