"""
Analyze K-Means clusters and determine which iteration/K value to use
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import KMeansFinalResult, KMeansResult
from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result, save_kmeans_final_result

# Create Flask app instance
app = create_app()

def analyze_current_final_result():
    """Analyze current data in kmeans_final_result"""
    with app.app_context():
        try:
            # Get K-Means result info
            kmeans_result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
            
            if not kmeans_result:
                print("✗ No K-Means result found")
                return None
            
            print("="*80)
            print("CURRENT K-MEANS RESULT IN DATABASE")
            print("="*80)
            print(f"K Value: {kmeans_result.k_value}")
            print(f"Iterations: {kmeans_result.n_iter}")
            print(f"Davies-Bouldin Index: {kmeans_result.davies_bouldin_index:.4f}")
            print(f"Inertia: {kmeans_result.inertia:.4f}")
            print(f"Created: {kmeans_result.created_at}")
            
            # Get final results
            final_results = KMeansFinalResult.query.all()
            
            if not final_results:
                print("\n✗ No final results in database")
                return None
            
            # Calculate per cluster
            clusters = {}
            for r in final_results:
                cluster_id = r.cluster_id
                if cluster_id not in clusters:
                    clusters[cluster_id] = {
                        'count': 0,
                        'total_terjual': 0,
                        'records': []
                    }
                clusters[cluster_id]['count'] += 1
                clusters[cluster_id]['total_terjual'] += r.jumlah_terjual
                clusters[cluster_id]['records'].append({
                    'kategori': r.kategori,
                    'size': r.size_range,
                    'jumlah': r.jumlah_terjual
                })
            
            print("\n" + "="*80)
            print("CLUSTER ANALYSIS")
            print("="*80)
            
            cluster_summary = []
            for cluster_id in sorted(clusters.keys()):
                data = clusters[cluster_id]
                cluster_summary.append({
                    'id': cluster_id,
                    'total': data['total_terjual']
                })
                print(f"\nCluster {cluster_id}:")
                print(f"  - Jumlah samples: {data['count']}")
                print(f"  - Total terjual: {data['total_terjual']}")
                print(f"  - Rata-rata per sample: {data['total_terjual'] / data['count']:.1f}")
            
            # Sort by total to determine labels
            cluster_summary.sort(key=lambda x: x['total'])
            
            grand_total = sum(c['total'] for c in cluster_summary)
            
            print("\n" + "="*80)
            print("SUMMARY TABLE")
            print("="*80)
            print(f"{'CLUSTER':<15} {'JUMLAH':<15} {'PERCENTAGE':<15} {'DESKRIPSI':<20}")
            print("-" * 80)
            
            # Assign labels based on total sales
            for idx, cluster in enumerate(cluster_summary):
                cluster_id = cluster['id']
                total = cluster['total']
                percentage = (total / grand_total) * 100
                
                # Determine description
                if idx == 0:  # Lowest
                    desc = "Kurang Laris 📉"
                elif idx == len(cluster_summary) - 1:  # Highest
                    desc = "Terlaris ⭐"
                else:  # Middle
                    desc = "Sedang 📊"
                
                print(f"C{cluster_id:<14} {total:<15} {percentage:<14.1f}% {desc:<20}")
            
            print("-" * 80)
            print(f"{'TOTAL':<15} {grand_total:<15} {'100.0%':<15}")
            
            print("\n" + "="*80)
            print(f"ANSWER: Data diambil dari K={kmeans_result.k_value}, Iterasi ke-{kmeans_result.n_iter}")
            print("="*80)
            
            return {
                'k': kmeans_result.k_value,
                'iteration': kmeans_result.n_iter,
                'clusters': cluster_summary
            }
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def test_different_k_values():
    """Test K-Means with different K values to compare"""
    with app.app_context():
        print("\n" + "="*80)
        print("TESTING DIFFERENT K VALUES")
        print("="*80)
        
        k_values = [2, 3, 4, 5]
        results_summary = []
        
        for k in k_values:
            print(f"\n{'='*80}")
            print(f"TESTING K = {k}")
            print(f"{'='*80}")
            
            # Run K-Means
            result = process_kmeans_manual(k=k)
            
            if result:
                labels = result['labels']
                data_agg = result['data_aggregated']
                
                # Calculate cluster totals
                clusters = {}
                for idx, label in enumerate(labels):
                    if label not in clusters:
                        clusters[label] = 0
                    clusters[label] += data_agg.iloc[idx]['jumlah_terjual']
                
                print(f"\nK={k} Results:")
                print(f"  - Iterations: {result['n_iter']}")
                print(f"  - DBI: {result['davies_bouldin']:.4f}")
                print(f"  - Inertia: {result['inertia']:.4f}")
                
                print(f"\n  Cluster Distribution:")
                cluster_list = []
                for cluster_id in sorted(clusters.keys()):
                    total = clusters[cluster_id]
                    cluster_list.append({'id': cluster_id, 'total': total})
                    print(f"    Cluster {cluster_id}: {total} terjual")
                
                # Sort and assign labels
                cluster_list.sort(key=lambda x: x['total'])
                print(f"\n  Sorted by volume:")
                for idx, c in enumerate(cluster_list):
                    if idx == 0:
                        desc = "Kurang Laris 📉"
                    elif idx == len(cluster_list) - 1:
                        desc = "Terlaris ⭐"
                    else:
                        desc = "Sedang 📊"
                    print(f"    C{c['id']}: {c['total']} - {desc}")
                
                results_summary.append({
                    'k': k,
                    'n_iter': result['n_iter'],
                    'dbi': result['davies_bouldin'],
                    'inertia': result['inertia'],
                    'clusters': cluster_list
                })
        
        # Summary comparison
        print("\n" + "="*80)
        print("COMPARISON SUMMARY")
        print("="*80)
        print(f"{'K':<5} {'Iter':<8} {'DBI':<12} {'Inertia':<12} {'Best Quality':<15}")
        print("-" * 60)
        
        best_dbi = min(results_summary, key=lambda x: x['dbi'])
        
        for r in results_summary:
            best_mark = "✓ BEST" if r['k'] == best_dbi['k'] else ""
            print(f"{r['k']:<5} {r['n_iter']:<8} {r['dbi']:<12.4f} {r['inertia']:<12.4f} {best_mark:<15}")
        
        print("\n" + "="*80)
        print(f"RECOMMENDATION: Use K={best_dbi['k']} (Best DBI: {best_dbi['dbi']:.4f})")
        print("="*80)
        
        return results_summary

if __name__ == "__main__":
    print("\n" + "="*80)
    print("K-MEANS CLUSTER ANALYSIS")
    print("="*80)
    
    # Step 1: Analyze current data
    print("\nSTEP 1: Analyzing current kmeans_final_result...")
    current = analyze_current_final_result()
    
    # Step 2: Test different K values
    print("\n\nSTEP 2: Testing different K values...")
    results = test_different_k_values()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETED")
    print("="*80)
