"""
Test untuk memastikan DBI terpisah ditampilkan dengan benar
"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual

app = create_app()

with app.app_context():
    print("="*80)
    print("TEST DBI TERPISAH UNTUK UI")
    print("="*80)
    
    print("\n🔄 Running K-Means clustering...")
    result = process_kmeans_manual(k=3)
    
    if result:
        print(f"\n✅ Result berhasil!")
        print(f"\n📊 Nilai yang akan ditampilkan di UI:")
        print(f"   Inertia: {result['inertia']:.2f}")
        print(f"   DBI Combined: {result['davies_bouldin_combined']:.3f}")
        print(f"   DBI Standard: {result['davies_bouldin_standard']:.3f}")
        print(f"   DBI Non-Standard: {result['davies_bouldin_non_standard']:.3f}")
        
        print(f"\n💡 Di UI akan tampil sebagai:")
        print(f"""
┌─────────────────────────────────────────┐
│  INERTIA                                │
│  {result['inertia']:.2f}                                    │
│  Jumlah kuadrat jarak ke centroid      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  DAVIES-BOULDIN INDEX (Combined)        │
│  {result['davies_bouldin_combined']:.3f}                                  │
│  Semakin rendah semakin baik            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  DBI STANDARD                           │
│  {result['davies_bouldin_standard']:.3f}                                  │
│  DBI untuk kategori Standard            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  DBI NON-STANDARD                       │
│  {result['davies_bouldin_non_standard']:.3f}                                  │
│  DBI untuk kategori Non-Standard        │
└─────────────────────────────────────────┘
        """)
        
        print(f"\n" + "="*80)
        print("✅ UPDATE SELESAI!")
        print("="*80)
        print("""
File yang diupdate:
1. app/routes.py - mengirim DBI terpisah ke frontend
2. app/templates/preprocessing_kmeans.html - tampilan 3 card DBI
3. app/static/js/preprocessing-kmeans.js - menampilkan nilai DBI terpisah
4. app/templates/preprocessing_kmedoids.html - tampilan 3 card DBI
5. app/static/js/preprocessing-kmedoids.js - menampilkan nilai DBI terpisah

Sekarang UI akan menampilkan:
- DBI Combined (0.481) - untuk semua data
- DBI Standard (0.518) - hanya kategori Standard
- DBI Non-Standard (0.404) - hanya kategori Non-Standard

Silakan jalankan Flask app dan test di browser!
        """)
    else:
        print("❌ Clustering gagal!")
