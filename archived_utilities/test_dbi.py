import sys
sys.path.insert(0, 'c:/Users/LENOVO/Documents/Project_Ta_Skripsi')

from app import create_app
from app.processing_kmeans import process_kmeans_manual
from app.dbi_calculator import calculate_dbi_comparison

app = create_app()
with app.app_context():
    print("=" * 70)
    print("VERIFIKASI DBI CALCULATION")
    print("=" * 70)
    
    # Test K=3
    print("\nTest dengan K=3:")
    print("-" * 70)
    
    result = process_kmeans_manual(k=3)
    if result:
        dbi_kmeans_prep = result['davies_bouldin']
        print(f"DBI dari preprocessing_kmeans.py: {dbi_kmeans_prep:.6f}")
    else:
        print("ERROR: process_kmeans_manual returned None")
    
    dbi_result = calculate_dbi_comparison(k_min=3, k_max=3, max_iterations=100)
    if dbi_result['status'] == 'success':
        dbi_kmeans_calc = dbi_result['list_dbi_kmeans'][0]
        dbi_kmedoids_calc = dbi_result['list_dbi_kmedoids'][0]
        print(f"DBI dari dbi_calculator KMeans: {dbi_kmeans_calc:.6f}")
        print(f"DBI dari dbi_calculator KMedoids: {dbi_kmedoids_calc:.6f}")
        
        # Perbandingan
        diff = abs(dbi_kmeans_prep - dbi_kmeans_calc)
        print(f"\nPerbandingan:")
        print(f"  Difference: {diff:.10f}")
        print(f"  Match: {'YES' if diff < 0.0001 else 'NO'}")
    else:
        print(f"ERROR: {dbi_result['message']}")
    
    print("\n" + "=" * 70)

