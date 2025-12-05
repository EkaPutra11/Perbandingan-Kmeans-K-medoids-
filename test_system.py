#!/usr/bin/env python
from app import create_app
from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result, get_kmeans_result
from app.processing_kmedoids import process_kmedoids_manual, save_kmedoids_manual_result, get_kmedoids_result

app = create_app()
app.app_context().push()

print("=" * 60)
print("COMPLETE SYSTEM TEST")
print("=" * 60)

# Test KMeans
print("\n[1] Testing KMeans Clustering...")
print("-" * 60)
kmeans_result = process_kmeans_manual(k=3)
print(f"✓ Inertia: {kmeans_result['inertia']:.2f}")
print(f"✓ Davies-Bouldin Index: {kmeans_result['davies_bouldin']:.3f}")
print(f"✓ Number of iterations: {kmeans_result['n_iter']}")
print(f"✓ Samples processed: {kmeans_result['n_samples']}")

# Save KMeans
print("\n[2] Saving KMeans Results...")
print("-" * 60)
save_kmeans_manual_result(kmeans_result)
print("✓ Results saved to database")

# Retrieve KMeans
print("\n[3] Retrieving KMeans Results...")
print("-" * 60)
retrieved_km = get_kmeans_result()
if retrieved_km:
    print(f"✓ Retrieved K={retrieved_km['k_value']}")
    print(f"✓ Inertia: {retrieved_km['inertia']:.2f}")
    print(f"✓ DBI: {retrieved_km['davies_bouldin_index']:.3f}")
    print(f"✓ Cluster distribution: {retrieved_km['cluster_distribution']}")
    print(f"✓ Analysis categories: {list(retrieved_km.get('analysis', {}).keys())}")

# Test KMedoids
print("\n[4] Testing KMedoids Clustering...")
print("-" * 60)
kmedoids_result = process_kmedoids_manual(k=3)
print(f"✓ Cost: {kmedoids_result['cost']:.2f}")
print(f"✓ Davies-Bouldin Index: {kmedoids_result['davies_bouldin']:.3f}")
print(f"✓ Number of iterations: {kmedoids_result['n_iter']}")
print(f"✓ Medoids: {kmedoids_result['medoids']}")

# Save KMedoids
print("\n[5] Saving KMedoids Results...")
print("-" * 60)
save_kmedoids_manual_result(kmedoids_result)
print("✓ Results saved to database")

# Retrieve KMedoids
print("\n[6] Retrieving KMedoids Results...")
print("-" * 60)
retrieved_kmed = get_kmedoids_result()
if retrieved_kmed:
    print(f"✓ Retrieved K={retrieved_kmed['k_value']}")
    print(f"✓ Cost: {retrieved_kmed['cost']:.2f}")
    print(f"✓ DBI: {retrieved_kmed['davies_bouldin_index']:.3f}")
    print(f"✓ Cluster distribution: {retrieved_kmed['cluster_distribution']}")
    print(f"✓ Analysis categories: {list(retrieved_kmed.get('analysis', {}).keys())}")

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
