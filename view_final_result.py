"""
View K-Means Final Result from database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import KMeansFinalResult, KMeansResult
from app.processing_kmeans import get_kmeans_final_results

# Create Flask app instance
app = create_app()

def view_final_results():
    """View all final results grouped by cluster"""
    with app.app_context():
        try:
            # Get K-Means result info
            kmeans_result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
            
            if kmeans_result:
                print(f"K-Means Result Information:")
                print(f"  - K Value: {kmeans_result.k_value}")
                print(f"  - Davies-Bouldin Index: {kmeans_result.davies_bouldin_index:.4f}")
                print(f"  - Inertia: {kmeans_result.inertia:.4f}")
                print(f"  - Iterations Used: {kmeans_result.n_iter} out of {kmeans_result.max_iterations}")
                print(f"  - Total Samples: {kmeans_result.n_samples}")
                print(f"  - Created: {kmeans_result.created_at}")
            
            # Get final results
            final_results = get_kmeans_final_results()
            
            if not final_results:
                print("\n✗ No final results found")
                return
            
            print(f"\n{'='*80}")
            print(f"K-MEANS FINAL RESULT - COMPLETE DATA ({len(final_results)} records)")
            print(f"{'='*80}")
            
            # Group by cluster
            clusters = {}
            for r in final_results:
                cluster_id = r['cluster_id']
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(r)
            
            # Display each cluster
            for cluster_id in sorted(clusters.keys()):
                cluster_data = clusters[cluster_id]
                print(f"\n{'='*80}")
                print(f"CLUSTER {cluster_id} - {len(cluster_data)} samples")
                print(f"{'='*80}")
                print(f"{'No':<5} {'Kategori':<20} {'Size Range':<15} {'Jumlah Terjual':<15}")
                print("-" * 70)
                
                total_terjual = 0
                for idx, r in enumerate(cluster_data, 1):
                    print(f"{idx:<5} {r['kategori']:<20} {r['size_range']:<15} {r['jumlah_terjual']:<15}")
                    total_terjual += r['jumlah_terjual']
                
                print("-" * 70)
                print(f"{'TOTAL':<40} {total_terjual:<15}")
            
            # Summary
            print(f"\n{'='*80}")
            print("SUMMARY")
            print(f"{'='*80}")
            print(f"Total Clusters: {len(clusters)}")
            for cluster_id in sorted(clusters.keys()):
                cluster_data = clusters[cluster_id]
                total = sum(r['jumlah_terjual'] for r in cluster_data)
                print(f"  Cluster {cluster_id}: {len(cluster_data)} samples, Total Terjual: {total}")
            
            grand_total = sum(r['jumlah_terjual'] for r in final_results)
            print(f"\nGrand Total Jumlah Terjual: {grand_total}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("VIEWING K-MEANS FINAL RESULT FROM DATABASE")
    print("="*80 + "\n")
    
    view_final_results()
    
    print("\n" + "="*80)
