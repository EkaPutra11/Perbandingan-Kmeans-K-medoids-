"""
Test langsung dari UI - simulasi request ke Flask app
"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result
from app.processing_kmedoids import process_kmedoids_manual, save_kmedoids_manual_result

app = create_app()

with app.app_context():
    print("="*80)
    print("SIMULASI REQUEST DARI UI")
    print("="*80)
    
    # Jalankan K-Means seperti dari UI
    print("\n🔄 Running K-Means clustering...")
    result_kmeans = process_kmeans_manual(k=3)
    
    if result_kmeans:
        print(f"\n✅ K-Means Result Object:")
        print(f"   Keys in result: {list(result_kmeans.keys())}")
        print(f"\n📊 DBI Values in result:")
        print(f"   davies_bouldin (legacy): {result_kmeans.get('davies_bouldin')}")
        print(f"   davies_bouldin_combined: {result_kmeans.get('davies_bouldin_combined')}")
        print(f"   davies_bouldin_standard: {result_kmeans.get('davies_bouldin_standard')}")
        print(f"   davies_bouldin_non_standard: {result_kmeans.get('davies_bouldin_non_standard')}")
        
        # Save to database
        print(f"\n💾 Saving to database...")
        if save_kmeans_manual_result(result_kmeans):
            print(f"   ✅ Saved successfully")
        else:
            print(f"   ❌ Failed to save")
    
    print("\n" + "="*80)
    
    # Jalankan K-Medoids seperti dari UI
    print("\n🔄 Running K-Medoids clustering...")
    result_kmedoids = process_kmedoids_manual(k=3)
    
    if result_kmedoids:
        print(f"\n✅ K-Medoids Result Object:")
        print(f"   Keys in result: {list(result_kmedoids.keys())}")
        print(f"\n📊 DBI Values in result:")
        print(f"   davies_bouldin (legacy): {result_kmedoids.get('davies_bouldin')}")
        print(f"   davies_bouldin_combined: {result_kmedoids.get('davies_bouldin_combined')}")
        print(f"   davies_bouldin_standard: {result_kmedoids.get('davies_bouldin_standard')}")
        print(f"   davies_bouldin_non_standard: {result_kmedoids.get('davies_bouldin_non_standard')}")
        
        # Save to database
        print(f"\n💾 Saving to database...")
        if save_kmedoids_manual_result(result_kmedoids):
            print(f"   ✅ Saved successfully")
        else:
            print(f"   ❌ Failed to save")
    
    print("\n" + "="*80)
    print("KESIMPULAN:")
    print("="*80)
    print("""
✅ Result object sekarang berisi:
   - davies_bouldin (legacy - untuk backward compatibility)
   - davies_bouldin_combined (sama dengan davies_bouldin)
   - davies_bouldin_standard (DBI hanya untuk Standard)
   - davies_bouldin_non_standard (DBI hanya untuk Non-Standard)

Untuk menampilkan di UI, Anda perlu update:
1. routes.py - untuk mengirim nilai DBI terpisah ke template
2. template HTML - untuk menampilkan 3 nilai DBI

Saat ini UI masih menampilkan davies_bouldin (legacy) yang sama seperti sebelumnya.
Nilai DBI terpisah sudah dihitung, hanya perlu ditampilkan di UI.
    """)
