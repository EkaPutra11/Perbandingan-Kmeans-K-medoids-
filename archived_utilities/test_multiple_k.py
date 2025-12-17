"""
Test K-Means and K-Medoids convergence with different k values
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.processing_kmeans import process_kmeans_manual
from app.processing_kmedoids import process_kmedoids_manual

# Create Flask app instance
app = create_app()

def test_convergence_for_multiple_k():
    """Test convergence for k=2, 3, 4, 5"""
    k_values = [2, 3, 4, 5]
    
    print("\n" + "="*80)
    print("TESTING CONVERGENCE FOR MULTIPLE K VALUES")
    print("="*80)
    
    results = {
        'kmeans': {},
        'kmedoids': {}
    }
    
    with app.app_context():
        for k in k_values:
            print(f"\n{'='*80}")
            print(f"TESTING WITH K = {k}")
            print(f"{'='*80}")
            
            # Test K-Means
            print(f"\n[K-Means, k={k}] Running...")
            try:
                kmeans_result = process_kmeans_manual(k=k)
                if kmeans_result:
                    results['kmeans'][k] = {
                        'n_iter': kmeans_result['n_iter'],
                        'inertia': kmeans_result['inertia'],
                        'dbi': kmeans_result['davies_bouldin']
                    }
                    print(f"✓ Converged at iteration {kmeans_result['n_iter']}")
                    print(f"  Inertia: {kmeans_result['inertia']:.4f}")
                    print(f"  DBI: {kmeans_result['davies_bouldin']:.4f}")
                else:
                    print(f"✗ Failed")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
            
            # Test K-Medoids
            print(f"\n[K-Medoids, k={k}] Running...")
            try:
                kmedoids_result = process_kmedoids_manual(k=k)
                if kmedoids_result:
                    results['kmedoids'][k] = {
                        'n_iter': kmedoids_result['n_iter'],
                        'cost': kmedoids_result['cost'],
                        'dbi': kmedoids_result['davies_bouldin']
                    }
                    print(f"✓ Converged at iteration {kmedoids_result['n_iter']}")
                    print(f"  Cost: {kmedoids_result['cost']:.4f}")
                    print(f"  DBI: {kmedoids_result['davies_bouldin']:.4f}")
                else:
                    print(f"✗ Failed")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
    
    # Print summary
    print("\n" + "="*80)
    print("CONVERGENCE SUMMARY")
    print("="*80)
    
    print("\nK-MEANS ITERATIONS:")
    print(f"{'K Value':<10} {'Iterations':<15} {'Inertia':<15} {'DBI':<10}")
    print("-" * 50)
    for k in k_values:
        if k in results['kmeans']:
            r = results['kmeans'][k]
            print(f"{k:<10} {r['n_iter']:<15} {r['inertia']:<15.4f} {r['dbi']:<10.4f}")
    
    print("\nK-MEDOIDS ITERATIONS:")
    print(f"{'K Value':<10} {'Iterations':<15} {'Cost':<15} {'DBI':<10}")
    print("-" * 50)
    for k in k_values:
        if k in results['kmedoids']:
            r = results['kmedoids'][k]
            print(f"{k:<10} {r['n_iter']:<15} {r['cost']:<15.4f} {r['dbi']:<10.4f}")
    
    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    
    if results['kmeans']:
        avg_iter_kmeans = sum(r['n_iter'] for r in results['kmeans'].values()) / len(results['kmeans'])
        print(f"\n✓ K-Means average iterations: {avg_iter_kmeans:.1f}")
        max_iter_kmeans = max(r['n_iter'] for r in results['kmeans'].values())
        print(f"  Maximum iterations used: {max_iter_kmeans} (out of 10)")
        if max_iter_kmeans < 10:
            print(f"  → All tests converged before max iterations!")
        
    if results['kmedoids']:
        avg_iter_kmedoids = sum(r['n_iter'] for r in results['kmedoids'].values()) / len(results['kmedoids'])
        print(f"\n✓ K-Medoids average iterations: {avg_iter_kmedoids:.1f}")
        max_iter_kmedoids = max(r['n_iter'] for r in results['kmedoids'].values())
        print(f"  Maximum iterations used: {max_iter_kmedoids} (out of 10)")
        if max_iter_kmedoids < 10:
            print(f"  → All tests converged before max iterations!")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_convergence_for_multiple_k()
