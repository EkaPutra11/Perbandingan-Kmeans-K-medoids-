"""
Test separated clustering implementation untuk K-Means dan K-Medoids
"""
from app import create_app
from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result
from app.processing_kmedoids import process_kmedoids_manual, save_kmedoids_manual_result

app = create_app()

with app.app_context():
    print("="*80)
    print("TEST SEPARATED CLUSTERING IMPLEMENTATION")
    print("="*80)
    
    # ========================================================================
    # Test K-Means
    # ========================================================================
    print("\n" + "="*80)
    print("1️⃣  K-MEANS CLUSTERING")
    print("="*80)
    
    result_kmeans = process_kmeans_manual(k=3)
    
    if result_kmeans:
        print(f"\n✅ K-Means clustering completed!")
        print(f"   Total samples: {result_kmeans['n_samples']}")
        print(f"   Iterations: {result_kmeans['n_iter']}")
        print(f"   DBI: {result_kmeans['davies_bouldin']:.4f}")
        print(f"   Inertia: {result_kmeans['inertia']:.2f}")
        
        # Analyze results by category
        df_result = result_kmeans['data_aggregated']
        print(f"\n📊 Results by Category:")
        
        for category_type in ['Standard', 'Non-Standard']:
            df_cat = df_result[df_result['category_type'] == category_type]
            if len(df_cat) > 0:
                print(f"\n   {category_type}:")
                print(f"     Total: {len(df_cat)} rows")
                print(f"     Clusters: {df_cat['cluster_id'].value_counts().sort_index().to_dict()}")
                if 'tier' in df_cat.columns:
                    print(f"     Tiers: {df_cat['tier'].value_counts().to_dict()}")
        
        # Save to database
        print(f"\n💾 Saving K-Means result to database...")
        if save_kmeans_manual_result(result_kmeans):
            print(f"   ✅ Saved successfully!")
        else:
            print(f"   ❌ Failed to save")
    else:
        print("\n❌ K-Means clustering failed!")
    
    # ========================================================================
    # Test K-Medoids
    # ========================================================================
    print("\n" + "="*80)
    print("2️⃣  K-MEDOIDS CLUSTERING")
    print("="*80)
    
    result_kmedoids = process_kmedoids_manual(k=3)
    
    if result_kmedoids:
        print(f"\n✅ K-Medoids clustering completed!")
        print(f"   Total samples: {result_kmedoids['n_samples']}")
        print(f"   Iterations: {result_kmedoids['n_iter']}")
        print(f"   DBI: {result_kmedoids['davies_bouldin']:.4f}")
        print(f"   Cost: {result_kmedoids['cost']:.2f}")
        
        # Analyze results by category
        df_result = result_kmedoids['data_aggregated']
        print(f"\n📊 Results by Category:")
        
        for category_type in ['Standard', 'Non-Standard']:
            df_cat = df_result[df_result['category_type'] == category_type]
            if len(df_cat) > 0:
                print(f"\n   {category_type}:")
                print(f"     Total: {len(df_cat)} rows")
                print(f"     Clusters: {df_cat['cluster_id'].value_counts().sort_index().to_dict()}")
                if 'tier' in df_cat.columns:
                    print(f"     Tiers: {df_cat['tier'].value_counts().to_dict()}")
        
        # Save to database
        print(f"\n💾 Saving K-Medoids result to database...")
        if save_kmedoids_manual_result(result_kmedoids):
            print(f"   ✅ Saved successfully!")
        else:
            print(f"   ❌ Failed to save")
    else:
        print("\n❌ K-Medoids clustering failed!")
    
    # ========================================================================
    # Compare Results
    # ========================================================================
    if result_kmeans and result_kmedoids:
        print("\n" + "="*80)
        print("3️⃣  COMPARISON")
        print("="*80)
        
        print(f"""
┌─────────────────────────────────────────────────────────────────┐
│                    CLUSTERING COMPARISON                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  K-MEANS:                                                       │
│    DBI: {result_kmeans['davies_bouldin']:.4f}                                              │
│    Iterations: {result_kmeans['n_iter']}                                                 │
│    Samples: {result_kmeans['n_samples']}                                                │
│                                                                 │
│  K-MEDOIDS:                                                     │
│    DBI: {result_kmedoids['davies_bouldin']:.4f}                                              │
│    Iterations: {result_kmedoids['n_iter']}                                                 │
│    Samples: {result_kmedoids['n_samples']}                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
        """)
        
        # Best algorithm
        if result_kmeans['davies_bouldin'] < result_kmedoids['davies_bouldin']:
            winner = "K-MEANS"
            diff = result_kmedoids['davies_bouldin'] - result_kmeans['davies_bouldin']
            pct = (diff / result_kmedoids['davies_bouldin']) * 100
        else:
            winner = "K-MEDOIDS"
            diff = result_kmeans['davies_bouldin'] - result_kmedoids['davies_bouldin']
            pct = (diff / result_kmeans['davies_bouldin']) * 100
        
        print(f"🏆 {winner} has better DBI (lower is better)")
        print(f"   Difference: {diff:.4f} ({pct:.1f}% better)\n")
    
    print("="*80)
    print("TEST COMPLETED")
    print("="*80)
