"""Quick test untuk clustering terpisah"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual
from app.processing_kmedoids import process_kmedoids_manual

app = create_app()
with app.app_context():
    print("\n" + "="*60)
    print("TEST CLUSTERING TERPISAH")
    print("="*60)
    
    # K-Means
    print("\n[K-MEANS]")
    kmeans = process_kmeans_manual(k=3)
    print(f"Total: {kmeans['n_samples']} | DBI: {kmeans['davies_bouldin']:.4f}")
    if 'results_by_category' in kmeans:
        for cat, res in kmeans['results_by_category'].items():
            print(f"  {cat}: n={res['n_samples']}, DBI={res['dbi']:.4f}")
    
    # K-Medoids
    print("\n[K-MEDOIDS]")
    kmedoids = process_kmedoids_manual(k=3)
    print(f"Total: {kmedoids['n_samples']} | DBI: {kmedoids['davies_bouldin']:.4f}")
    if 'results_by_category' in kmedoids:
        for cat, res in kmedoids['results_by_category'].items():
            print(f"  {cat}: n={res['n_samples']}, DBI={res['dbi']:.4f}")
    
    print("\n✓ Clustering terpisah berhasil!")
    print("="*60 + "\n")
