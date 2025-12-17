"""
Test DBI terpisah untuk Standard dan Non-Standard
"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual
from app.processing_kmedoids import process_kmedoids_manual

app = create_app()

with app.app_context():
    print("="*80)
    print("TEST SEPARATED DBI CALCULATION")
    print("="*80)
    
    # ========================================================================
    # Test K-Means
    # ========================================================================
    print("\n" + "="*80)
    print("1️⃣  K-MEANS CLUSTERING")
    print("="*80)
    
    result_kmeans = process_kmeans_manual(k=3)
    
    if result_kmeans:
        print(f"\n✅ K-Means completed!")
        print(f"\n📊 DBI Results:")
        print(f"   Combined DBI        : {result_kmeans['davies_bouldin_combined']:.4f}")
        if result_kmeans['davies_bouldin_standard']:
            print(f"   Standard DBI        : {result_kmeans['davies_bouldin_standard']:.4f}")
        if result_kmeans['davies_bouldin_non_standard']:
            print(f"   Non-Standard DBI    : {result_kmeans['davies_bouldin_non_standard']:.4f}")
        
        # Analyze cluster distribution
        df = result_kmeans['data_aggregated']
        labels = result_kmeans['labels']
        
        df['category_type'] = df['kategori'].apply(
            lambda x: 'Standard' if x.lower() in ['standard', 'standar'] else 'Non-Standard'
        )
        
        print(f"\n📦 Cluster Distribution:")
        print(f"   {'Category':<15} {'Cluster 0':>12} {'Cluster 1':>12} {'Cluster 2':>12} {'Total':>10}")
        print("   " + "-"*65)
        
        for cat_type in ['Standard', 'Non-Standard']:
            c0 = ((df['category_type'] == cat_type) & (labels == 0)).sum()
            c1 = ((df['category_type'] == cat_type) & (labels == 1)).sum()
            c2 = ((df['category_type'] == cat_type) & (labels == 2)).sum()
            total = c0 + c1 + c2
            print(f"   {cat_type:<15} {c0:>12} {c1:>12} {c2:>12} {total:>10}")
    else:
        print("\n❌ K-Means failed!")
    
    # ========================================================================
    # Test K-Medoids
    # ========================================================================
    print("\n" + "="*80)
    print("2️⃣  K-MEDOIDS CLUSTERING")
    print("="*80)
    
    result_kmedoids = process_kmedoids_manual(k=3)
    
    if result_kmedoids:
        print(f"\n✅ K-Medoids completed!")
        print(f"\n📊 DBI Results:")
        print(f"   Combined DBI        : {result_kmedoids['davies_bouldin_combined']:.4f}")
        if result_kmedoids['davies_bouldin_standard']:
            print(f"   Standard DBI        : {result_kmedoids['davies_bouldin_standard']:.4f}")
        if result_kmedoids['davies_bouldin_non_standard']:
            print(f"   Non-Standard DBI    : {result_kmedoids['davies_bouldin_non_standard']:.4f}")
        
        # Analyze cluster distribution
        df = result_kmedoids['data_aggregated']
        labels = result_kmedoids['labels']
        
        df['category_type'] = df['kategori'].apply(
            lambda x: 'Standard' if x.lower() in ['standard', 'standar'] else 'Non-Standard'
        )
        
        print(f"\n📦 Cluster Distribution:")
        print(f"   {'Category':<15} {'Cluster 0':>12} {'Cluster 1':>12} {'Cluster 2':>12} {'Total':>10}")
        print("   " + "-"*65)
        
        for cat_type in ['Standard', 'Non-Standard']:
            c0 = ((df['category_type'] == cat_type) & (labels == 0)).sum()
            c1 = ((df['category_type'] == cat_type) & (labels == 1)).sum()
            c2 = ((df['category_type'] == cat_type) & (labels == 2)).sum()
            total = c0 + c1 + c2
            print(f"   {cat_type:<15} {c0:>12} {c1:>12} {c2:>12} {total:>10}")
    else:
        print("\n❌ K-Medoids failed!")
    
    # ========================================================================
    # Summary
    # ========================================================================
    if result_kmeans and result_kmedoids:
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        
        print(f"""
┌─────────────────────────────────────────────────────────────────┐
│                    DBI COMPARISON SUMMARY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  K-MEANS:                                                       │
│    Combined DBI       : {result_kmeans['davies_bouldin_combined']:.4f}                               │
│    Standard DBI       : {result_kmeans['davies_bouldin_standard']:.4f} (hanya data Standard)       │
│    Non-Standard DBI   : {result_kmeans['davies_bouldin_non_standard']:.4f} (hanya data Non-Standard)   │
│                                                                 │
│  K-MEDOIDS:                                                     │
│    Combined DBI       : {result_kmedoids['davies_bouldin_combined']:.4f}                               │
│    Standard DBI       : {result_kmedoids['davies_bouldin_standard']:.4f} (hanya data Standard)       │
│    Non-Standard DBI   : {result_kmedoids['davies_bouldin_non_standard']:.4f} (hanya data Non-Standard)   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

✅ PENJELASAN:

1. Combined DBI: Dihitung dari SEMUA data (Standard + Non-Standard)
   → Nilai rendah karena Standard mendominasi cluster homogen
   → Tidak menggambarkan fairness clustering

2. Standard DBI: Dihitung HANYA dari data kategori Standard
   → Menunjukkan seberapa baik Standard ter-cluster dalam grupnya
   → Independen dari bias volume Non-Standard

3. Non-Standard DBI: Dihitung HANYA dari data kategori Non-Standard
   → Menunjukkan seberapa baik Non-Standard ter-cluster dalam grupnya
   → Independen dari dominasi volume Standard

INTERPRETASI:
- Jika Standard DBI & Non-Standard DBI keduanya rendah → clustering bagus
- Jika salah satu tinggi → clustering kurang bagus untuk kategori tersebut
- Combined DBI bisa rendah tapi tidak adil jika cluster sangat tidak seimbang

UNTUK SKRIPSI:
Gunakan DBI terpisah untuk menunjukkan evaluasi yang lebih adil,
terutama ketika data memiliki perbedaan skala ekstrem antar kategori.
        """)
    
    print("="*80)
    print("TEST COMPLETED")
    print("="*80)
