"""
Test script untuk run clustering dan verifikasi distance field
"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result
from app.processing_kmedoids import process_kmedoids_manual, save_kmedoids_manual_result
from app.models import KMeansClusterDetail, KMedoidsClusterDetail

app = create_app()
app.app_context().push()

print("=" * 80)
print("TEST: Run Clustering dan Verifikasi Distance Fields")
print("=" * 80)

# Test KMeans
print("\n[1] Running KMeans with K=3...")
kmeans_result = process_kmeans_manual(k=3)
if kmeans_result:
    print("✓ KMeans completed")
    print(f"  - Inertia: {kmeans_result['inertia']:.4f}")
    print(f"  - DBI: {kmeans_result['davies_bouldin']:.4f}")
    
    # Save to database
    if save_kmeans_manual_result(kmeans_result):
        print("✓ KMeans result saved to database")
        
        # Check distance field
        sample_details = KMeansClusterDetail.query.limit(5).all()
        print("\nSample KMeans details:")
        for detail in sample_details:
            print(f"  - Penjualan ID: {detail.penjualan_id}, Cluster: {detail.cluster_id}, Distance: {detail.distance_to_centroid}")
        
        # Count null values
        null_count = KMeansClusterDetail.query.filter(KMeansClusterDetail.distance_to_centroid.is_(None)).count()
        total_count = KMeansClusterDetail.query.count()
        
        if null_count == 0:
            print(f"\n✅ SUCCESS: Semua {total_count} KMeans records punya distance_to_centroid")
        else:
            print(f"\n❌ ERROR: {null_count}/{total_count} records masih NULL")
    else:
        print("❌ Failed to save KMeans result")
else:
    print("❌ KMeans failed")

# Test KMedoids
print("\n[2] Running KMedoids with K=3...")
kmedoids_result = process_kmedoids_manual(k=3)
if kmedoids_result:
    print("✓ KMedoids completed")
    print(f"  - Cost: {kmedoids_result['cost']:.4f}")
    print(f"  - DBI: {kmedoids_result['davies_bouldin']:.4f}")
    
    # Save to database
    if save_kmedoids_manual_result(kmedoids_result):
        print("✓ KMedoids result saved to database")
        
        # Check distance field
        sample_details = KMedoidsClusterDetail.query.limit(5).all()
        print("\nSample KMedoids details:")
        for detail in sample_details:
            print(f"  - Penjualan ID: {detail.penjualan_id}, Cluster: {detail.cluster_id}, Distance: {detail.distance_to_medoid}, Is Medoid: {detail.is_medoid}")
        
        # Count null values
        null_count = KMedoidsClusterDetail.query.filter(KMedoidsClusterDetail.distance_to_medoid.is_(None)).count()
        total_count = KMedoidsClusterDetail.query.count()
        
        if null_count == 0:
            print(f"\n✅ SUCCESS: Semua {total_count} KMedoids records punya distance_to_medoid")
        else:
            print(f"\n❌ ERROR: {null_count}/{total_count} records masih NULL")
    else:
        print("❌ Failed to save KMedoids result")
else:
    print("❌ KMedoids failed")

print("\n" + "=" * 80)
