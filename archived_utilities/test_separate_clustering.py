"""
Test clustering terpisah untuk debug error
"""
from app import create_app, db
from app.processing_kmeans import process_kmeans_manual

app = create_app()

with app.app_context():
    print("Testing separate clustering...")
    try:
        result = process_kmeans_manual(k=3)
        if result:
            print("\n✅ SUCCESS!")
            print(f"Labels: {len(result['labels'])} items")
            print(f"Inertia: {result['inertia']}")
            print(f"DBI: {result['davies_bouldin']}")
            print(f"N samples: {result['n_samples']}")
        else:
            print("\n❌ Result is None!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
