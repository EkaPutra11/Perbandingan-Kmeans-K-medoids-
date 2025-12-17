"""
Test script to check K-Means and K-Medoids convergence behavior
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.processing_kmeans import process_kmeans_manual
from app.processing_kmedoids import process_kmedoids_manual

# Create Flask app instance
app = create_app()

def test_kmeans_convergence():
    """Test K-Means convergence"""
    print("="*80)
    print("TESTING K-MEANS CONVERGENCE")
    print("="*80)
    
    try:
        # Run K-Means with k=3
        print("\n[K-Means] Running with k=3...")
        result = process_kmeans_manual(k=3)
        
        if result:
            print(f"\n✓ K-Means Completed Successfully")
            print(f"  - Iterations used: {result['n_iter']} out of max 10")
            print(f"  - Final Inertia: {result['inertia']:.4f}")
            print(f"  - Davies-Bouldin Index: {result['davies_bouldin']:.4f}")
            print(f"  - Number of samples: {result['n_samples']}")
            
            # Check cluster distribution
            labels = result['labels']
            print(f"\n  Cluster Distribution:")
            for i in range(3):
                count = sum(labels == i)
                print(f"    - Cluster {i}: {count} samples")
            
            return result
        else:
            print("\n✗ K-Means Failed")
            return None
            
    except Exception as e:
        print(f"\n✗ Error in K-Means: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_kmedoids_convergence():
    """Test K-Medoids convergence"""
    print("\n" + "="*80)
    print("TESTING K-MEDOIDS CONVERGENCE")
    print("="*80)
    
    try:
        # Run K-Medoids with k=3
        print("\n[K-Medoids] Running with k=3...")
        result = process_kmedoids_manual(k=3)
        
        if result:
            print(f"\n✓ K-Medoids Completed Successfully")
            print(f"  - Iterations used: {result['n_iter']} out of max 10")
            print(f"  - Final Cost: {result['cost']:.4f}")
            print(f"  - Davies-Bouldin Index: {result['davies_bouldin']:.4f}")
            print(f"  - Number of samples: {result['n_samples']}")
            
            # Check cluster distribution
            labels = result['labels']
            print(f"\n  Cluster Distribution:")
            for i in range(3):
                count = sum(labels == i)
                print(f"    - Cluster {i}: {count} samples")
            
            return result
        else:
            print("\n✗ K-Medoids Failed")
            return None
            
    except Exception as e:
        print(f"\n✗ Error in K-Medoids: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def compare_results(kmeans_result, kmedoids_result):
    """Compare both algorithm results"""
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    
    if kmeans_result and kmedoids_result:
        print(f"\nConvergence Speed:")
        print(f"  K-Means:    {kmeans_result['n_iter']} iterations")
        print(f"  K-Medoids:  {kmedoids_result['n_iter']} iterations")
        
        print(f"\nQuality Metrics:")
        print(f"  K-Means DBI:    {kmeans_result['davies_bouldin']:.4f}")
        print(f"  K-Medoids DBI:  {kmedoids_result['davies_bouldin']:.4f}")
        print(f"  (Lower DBI is better)")
        
        if kmeans_result['n_iter'] < 10:
            print(f"\n✓ K-Means converged early (stopped before max iterations)")
        else:
            print(f"\n⚠ K-Means used all 10 iterations without convergence")
            
        if kmedoids_result['n_iter'] < 10:
            print(f"✓ K-Medoids converged early (stopped before max iterations)")
        else:
            print(f"⚠ K-Medoids used all 10 iterations without convergence")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CONVERGENCE TEST - K-MEANS vs K-MEDOIDS")
    print("Max Iterations: 10")
    print("Dataset: Penjualan Arwana (aggregated)")
    print("="*80)
    
    # Run within Flask app context
    with app.app_context():
        # Test both algorithms
        kmeans_result = test_kmeans_convergence()
        kmedoids_result = test_kmedoids_convergence()
        
        # Compare results
        compare_results(kmeans_result, kmedoids_result)
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")
