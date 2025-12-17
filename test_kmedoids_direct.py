from app import create_app
from app.processing_kmedoids import process_kmedoids_manual
import traceback

app = create_app()
with app.app_context():
    try:
        print("Testing K-Medoids with 3 clusters...")
        result = process_kmedoids_manual(3)
        
        if result is not None:
            print("✓ SUCCESS!")
            print(f"Clusters: {len(result['analysis']['standard']) + len(result['analysis']['non_standard'])}")
            print(f"Davies-Bouldin Index: {result['davies_bouldin']:.4f}")
            print(f"Iterations: {result['n_iter']}")
        else:
            print("✗ ERROR!")
            print("Result is None")
    except Exception as e:
        print(f"✗ EXCEPTION!")
        print(f"Error: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
