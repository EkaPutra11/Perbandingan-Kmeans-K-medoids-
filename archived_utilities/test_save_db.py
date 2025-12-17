"""Test save to database"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result, save_kmeans_final_result
from app.models import KMeansResult, KMeansClusterDetail, KMeansFinalResult

app = create_app()
with app.app_context():
    print("\n" + "="*70)
    print("TEST SAVE K-MEANS KE DATABASE")
    print("="*70)
    
    # Process K-Means
    print("\n[1] Running K-Means clustering...")
    result = process_kmeans_manual(k=3)
    if result:
        print(f"✓ Clustering berhasil: {result['n_samples']} sampel")
        
        # Save to database
        print("\n[2] Saving to database...")
        save_success = save_kmeans_manual_result(result)
        if save_success:
            print("✓ Save kmeans_result berhasil")
            
            # Get latest result
            latest = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
            if latest:
                print(f"   ID: {latest.id}")
                print(f"   DBI: {latest.davies_bouldin_index:.4f}")
                print(f"   Cluster dist: {latest.cluster_distribution}")
                
                # Count details
                detail_count = KMeansClusterDetail.query.filter_by(kmeans_result_id=latest.id).count()
                print(f"   Details: {detail_count} records")
                
                # Save to final result
                print("\n[3] Saving to kmeans_final_result...")
                final_success = save_kmeans_final_result(latest.id)
                if final_success:
                    print("✓ Save kmeans_final_result berhasil")
                    
                    # Count final results
                    final_count = KMeansFinalResult.query.count()
                    print(f"   Final results: {final_count} records")
                    
                    # Sample beberapa records
                    samples = KMeansFinalResult.query.limit(5).all()
                    print("\n[4] Sample data:")
                    for s in samples:
                        print(f"   - Cluster {s.cluster_id}: {s.kategori} {s.size_range} ({s.jumlah_terjual} terjual)")
                    
                    print("\n" + "="*70)
                    print("✅ SEMUA TEST BERHASIL!")
                    print("="*70 + "\n")
                else:
                    print("✗ Save final result GAGAL")
            else:
                print("✗ Latest result tidak ditemukan")
        else:
            print("✗ Save GAGAL")
    else:
        print("✗ Clustering GAGAL")
