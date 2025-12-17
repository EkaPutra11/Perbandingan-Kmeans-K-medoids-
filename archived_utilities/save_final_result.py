"""
Create kmeans_final_result table and save best K-Means result
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import db, KMeansFinalResult, KMeansResult
from app.processing_kmeans import save_kmeans_final_result, get_kmeans_final_results

# Create Flask app instance
app = create_app()

def create_final_result_table():
    """Create kmeans_final_result table"""
    with app.app_context():
        try:
            # Create table
            db.create_all()
            print("✓ Table 'kmeans_final_result' created successfully")
            return True
        except Exception as e:
            print(f"✗ Error creating table: {str(e)}")
            return False

def save_best_kmeans_result():
    """Save the best K-Means result (k=3 with best DBI) to final result table"""
    with app.app_context():
        try:
            # Get the latest K-Means result with k=3
            kmeans_result = KMeansResult.query.filter_by(k_value=3).order_by(
                KMeansResult.created_at.desc()
            ).first()
            
            if not kmeans_result:
                print("✗ No K-Means result found with k=3")
                print("  Running K-Means with k=3 first...")
                
                # Run K-Means with k=3
                from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result
                result = process_kmeans_manual(k=3)
                
                if result:
                    # Save to database
                    if save_kmeans_manual_result(result):
                        print("✓ K-Means result saved successfully")
                        # Get the newly created result
                        kmeans_result = KMeansResult.query.filter_by(k_value=3).order_by(
                            KMeansResult.created_at.desc()
                        ).first()
                    else:
                        print("✗ Failed to save K-Means result")
                        return False
                else:
                    print("✗ Failed to run K-Means")
                    return False
            
            print(f"\nBest K-Means Result (k={kmeans_result.k_value}):")
            print(f"  - ID: {kmeans_result.id}")
            print(f"  - Davies-Bouldin Index: {kmeans_result.davies_bouldin_index:.4f}")
            print(f"  - Inertia: {kmeans_result.inertia:.4f}")
            print(f"  - Iterations: {kmeans_result.n_iter}")
            print(f"  - Samples: {kmeans_result.n_samples}")
            print(f"  - Created: {kmeans_result.created_at}")
            
            # Save to final result table
            print(f"\nSaving to kmeans_final_result table...")
            if save_kmeans_final_result(kmeans_result.id):
                print("✓ Successfully saved best K-Means result to final table!")
                
                # Display final results
                final_results = get_kmeans_final_results()
                if final_results:
                    print(f"\nFinal Results Summary ({len(final_results)} records):")
                    print(f"{'Cluster':<10} {'Kategori':<20} {'Size Range':<15} {'Jumlah Terjual':<15}")
                    print("-" * 70)
                    for r in final_results[:10]:  # Show first 10
                        print(f"{r['cluster_id']:<10} {r['kategori']:<20} {r['size_range']:<15} {r['jumlah_terjual']:<15}")
                    
                    if len(final_results) > 10:
                        print(f"... and {len(final_results) - 10} more records")
                
                return True
            else:
                print("✗ Failed to save to final table")
                return False
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("="*80)
    print("CREATING KMEANS FINAL RESULT TABLE AND SAVING BEST RESULT")
    print("="*80)
    
    # Step 1: Create table
    print("\nStep 1: Creating table...")
    if create_final_result_table():
        # Step 2: Save best result
        print("\nStep 2: Saving best K-Means result...")
        save_best_kmeans_result()
    
    print("\n" + "="*80)
    print("COMPLETED")
    print("="*80)
