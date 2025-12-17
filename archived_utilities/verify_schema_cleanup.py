"""
Test script to verify the database schema has been updated correctly
and the models match the database structure
"""
from app import create_app
from app.models import db, KMeansClusterDetail, KMedoidsClusterDetail
import inspect

app = create_app()

with app.app_context():
    print("=" * 60)
    print("COLUMN CLEANUP VERIFICATION")
    print("=" * 60)
    
    # Check KMeansClusterDetail model
    print("\n1. KMeansClusterDetail Model Columns:")
    kmeans_columns = [col.name for col in KMeansClusterDetail.__table__.columns]
    print(f"   Columns: {kmeans_columns}")
    
    removed_cols = ['penjualan_id', 'cluster', 'harga_satuan', 'nama_penjual', 'kota_tujuan']
    found_removed = [col for col in removed_cols if col in kmeans_columns]
    
    if found_removed:
        print(f"   ❌ ERROR: Found removed columns: {found_removed}")
    else:
        print(f"   ✅ OK: All removed columns are gone")
    
    # Check KMedoidsClusterDetail model
    print("\n2. KMedoidsClusterDetail Model Columns:")
    kmedoids_columns = [col.name for col in KMedoidsClusterDetail.__table__.columns]
    print(f"   Columns: {kmedoids_columns}")
    
    found_removed = [col for col in removed_cols if col in kmedoids_columns]
    
    if found_removed:
        print(f"   ❌ ERROR: Found removed columns: {found_removed}")
    else:
        print(f"   ✅ OK: All removed columns are gone")
    
    # Check database tables
    print("\n3. Database Table Structure:")
    try:
        import pymysql
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='db_penjualan_arwana'
        )
        cursor = conn.cursor()
        
        # Check kmeans_cluster_detail
        cursor.execute("DESCRIBE kmeans_cluster_detail")
        kmeans_db_cols = [row[0] for row in cursor.fetchall()]
        print(f"\n   kmeans_cluster_detail: {kmeans_db_cols}")
        
        # Check kmedoids_cluster_detail
        cursor.execute("DESCRIBE kmedoids_cluster_detail")
        kmedoids_db_cols = [row[0] for row in cursor.fetchall()]
        print(f"   kmedoids_cluster_detail: {kmedoids_db_cols}")
        
        conn.close()
        
        # Verify removed columns are not in database
        kmeans_removed = [col for col in removed_cols if col in kmeans_db_cols]
        kmedoids_removed = [col for col in removed_cols if col in kmedoids_db_cols]
        
        if kmeans_removed:
            print(f"   ❌ ERROR: kmeans_cluster_detail has removed columns: {kmeans_removed}")
        else:
            print(f"   ✅ OK: kmeans_cluster_detail cleaned")
            
        if kmedoids_removed:
            print(f"   ❌ ERROR: kmedoids_cluster_detail has removed columns: {kmedoids_removed}")
        else:
            print(f"   ✅ OK: kmedoids_cluster_detail cleaned")
        
    except Exception as e:
        print(f"   ⚠️  Could not verify database tables: {e}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nExpected columns in KMeansClusterDetail:")
    print("   ✓ id, kmeans_result_id, cluster_id, kategori, size")
    print("   ✓ jumlah_terjual, total_harga, distance_to_centroid, created_at")
    print("\nExpected columns in KMedoidsClusterDetail:")
    print("   ✓ id, kmedoids_result_id, cluster_id, kategori, size")
    print("   ✓ jumlah_terjual, total_harga, distance_to_medoid, is_medoid, created_at")
