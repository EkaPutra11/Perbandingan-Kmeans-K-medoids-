from app import create_app
from app.processing_kmeans import process_kmeans_manual
from app.processing_kmedoids import process_kmedoids_manual
import numpy as np

app = create_app()
with app.app_context():
    print("=" * 60)
    print("COMPARING K-MEANS VS K-MEDOIDS CLUSTERING")
    print("=" * 60)
    
    # Test K-Means
    print("\n[*] Testing K-MEANS...")
    kmeans_result = process_kmeans_manual(3)
    if kmeans_result:
        kmeans_labels = kmeans_result['labels']
        print(f"✓ K-Means Success!")
        print(f"  Labels: {kmeans_labels}")
        print(f"  Unique labels: {np.unique(kmeans_labels)}")
        print(f"  Label counts: {np.bincount(kmeans_labels)}")
        
        # Count by cluster
        c0 = np.sum(kmeans_labels == 0)
        c1 = np.sum(kmeans_labels == 1)
        c2 = np.sum(kmeans_labels == 2)
        print(f"\n  K-Means Distribution:")
        print(f"    C0: {c0} items")
        print(f"    C1: {c1} items")
        print(f"    C2: {c2} items")
    else:
        print("✗ K-Means Failed!")
    
    # Test K-Medoids
    print("\n[*] Testing K-MEDOIDS...")
    kmedoids_result = process_kmedoids_manual(3)
    if kmedoids_result:
        kmedoids_labels = kmedoids_result['labels']
        print(f"✓ K-Medoids Success!")
        print(f"  Labels: {kmedoids_labels}")
        print(f"  Unique labels: {np.unique(kmedoids_labels)}")
        print(f"  Label counts: {np.bincount(kmedoids_labels)}")
        
        # Count by cluster
        c0 = np.sum(kmedoids_labels == 0)
        c1 = np.sum(kmedoids_labels == 1)
        c2 = np.sum(kmedoids_labels == 2)
        print(f"\n  K-Medoids Distribution:")
        print(f"    C0: {c0} items")
        print(f"    C1: {c1} items")
        print(f"    C2: {c2} items")
    else:
        print("✗ K-Medoids Failed!")
    
    # Compare
    if kmeans_result and kmedoids_result:
        print("\n" + "=" * 60)
        print("COMPARISON:")
        print("=" * 60)
        
        # Check if labels are identical
        are_identical = np.array_equal(kmeans_labels, kmedoids_labels)
        print(f"\nLabels identical? {are_identical}")
        
        if are_identical:
            print("\n[!] WARNING: K-Means and K-Medoids produced IDENTICAL results!")
            print("This is VERY unusual and suggests:")
            print("  1. Both are using the same percentile-based assignment")
            print("  2. The actual clustering algorithm is being bypassed")
            print("  3. Labels are not from the clustering, but from assign_tiers_by_percentile")
        else:
            # Count differences
            diff_count = np.sum(kmeans_labels != kmedoids_labels)
            print(f"\n[OK] Results differ in {diff_count} out of {len(kmeans_labels)} points ({diff_count/len(kmeans_labels)*100:.1f}%)")
            print("This is expected - different algorithms should produce different results.")
        
        # Check centroids vs medoids
        print("\n[DATA] K-Means Centroids:")
        for i, centroid in enumerate(kmeans_result['centroids']):
            print(f"  C{i}: jumlah_terjual = {centroid[0]:.4f}")
        
        print("\n[DATA] K-Medoids Medoid Indices:")
        print(f"  Medoid indices: {kmedoids_result['medoids']}")
        
        # Get actual medoid values
        X = kmedoids_result['X_normalized']
        print("\n[DATA] K-Medoids Medoid Values:")
        for i, medoid_idx in enumerate(kmedoids_result['medoids']):
            print(f"  C{i}: jumlah_terjual = {X[medoid_idx][0]:.4f}")
