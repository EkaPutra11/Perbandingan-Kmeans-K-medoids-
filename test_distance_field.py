"""
Test script untuk verifikasi distance_to_centroid sudah disimpan
"""
from app import create_app
from app.models import KMeansClusterDetail, KMedoidsClusterDetail

app = create_app()
app.app_context().push()

print("=" * 80)
print("TEST: Verifikasi distance_to_centroid dan distance_to_medoid")
print("=" * 80)

# Check KMeans
print("\n[1] Checking KMeans Cluster Details...")
kmeans_details = KMeansClusterDetail.query.limit(5).all()

if kmeans_details:
    print(f"✓ Found {KMeansClusterDetail.query.count()} KMeans cluster details")
    print("\nSample data:")
    for detail in kmeans_details:
        print(f"  - Penjualan ID: {detail.penjualan_id}, Cluster: {detail.cluster_id}, Distance: {detail.distance_to_centroid}")
    
    # Check if distance is not null
    null_count = KMeansClusterDetail.query.filter(KMeansClusterDetail.distance_to_centroid.is_(None)).count()
    if null_count == 0:
        print(f"\n✅ SUCCESS: Semua {KMeansClusterDetail.query.count()} records punya distance_to_centroid")
    else:
        print(f"\n❌ ERROR: {null_count} records masih NULL distance_to_centroid")
else:
    print("❌ No KMeans cluster details found")

# Check KMedoids
print("\n[2] Checking KMedoids Cluster Details...")
kmedoids_details = KMedoidsClusterDetail.query.limit(5).all()

if kmedoids_details:
    print(f"✓ Found {KMedoidsClusterDetail.query.count()} KMedoids cluster details")
    print("\nSample data:")
    for detail in kmedoids_details:
        print(f"  - Penjualan ID: {detail.penjualan_id}, Cluster: {detail.cluster_id}, Distance: {detail.distance_to_medoid}, Is Medoid: {detail.is_medoid}")
    
    # Check if distance is not null
    null_count = KMedoidsClusterDetail.query.filter(KMedoidsClusterDetail.distance_to_medoid.is_(None)).count()
    if null_count == 0:
        print(f"\n✅ SUCCESS: Semua {KMedoidsClusterDetail.query.count()} records punya distance_to_medoid")
    else:
        print(f"\n❌ ERROR: {null_count} records masih NULL distance_to_medoid")
else:
    print("❌ No KMedoids cluster details found")

print("\n" + "=" * 80)
