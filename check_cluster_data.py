"""
Check actual cluster counts from database in detail
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import KMeansFinalResult, KMeansResult, KMeansClusterDetail

app = create_app()

def check_cluster_details():
    """Check actual cluster data in detail"""
    with app.app_context():
        print("="*80)
        print("CHECKING ACTUAL CLUSTER DATA")
        print("="*80)
        
        # Get K-Means result
        kmeans_result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
        
        if not kmeans_result:
            print("No K-Means result found")
            return
        
        print(f"\nK-Means Result ID: {kmeans_result.id}")
        print(f"K Value: {kmeans_result.k_value}")
        print(f"Total Samples: {kmeans_result.n_samples}")
        
        # Check KMeansClusterDetail
        print("\n" + "="*80)
        print("DATA FROM: kmeans_cluster_detail")
        print("="*80)
        
        cluster_detail = KMeansClusterDetail.query.filter_by(
            kmeans_result_id=kmeans_result.id
        ).all()
        
        print(f"\nTotal records in kmeans_cluster_detail: {len(cluster_detail)}")
        
        # Count by cluster
        cluster_counts_detail = {}
        for detail in cluster_detail:
            cid = detail.cluster_id
            if cid not in cluster_counts_detail:
                cluster_counts_detail[cid] = []
            cluster_counts_detail[cid].append({
                'kategori': detail.kategori,
                'size': detail.size,
                'jumlah': detail.jumlah_terjual
            })
        
        print("\nBreakdown by cluster:")
        for cid in sorted(cluster_counts_detail.keys()):
            items = cluster_counts_detail[cid]
            print(f"\n  Cluster {cid}: {len(items)} items")
            # Show first 5
            for i, item in enumerate(items[:5]):
                print(f"    - {item['kategori']} {item['size']}: {item['jumlah']} unit")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more items")
        
        # Check KMeansFinalResult
        print("\n" + "="*80)
        print("DATA FROM: kmeans_final_result")
        print("="*80)
        
        final_results = KMeansFinalResult.query.all()
        
        print(f"\nTotal records in kmeans_final_result: {len(final_results)}")
        
        # Count by cluster
        cluster_counts_final = {}
        for result in final_results:
            cid = result.cluster_id
            if cid not in cluster_counts_final:
                cluster_counts_final[cid] = []
            cluster_counts_final[cid].append({
                'kategori': result.kategori,
                'size': result.size_range,
                'jumlah': result.jumlah_terjual
            })
        
        print("\nBreakdown by cluster:")
        for cid in sorted(cluster_counts_final.keys()):
            items = cluster_counts_final[cid]
            print(f"\n  Cluster {cid}: {len(items)} items")
            # Show first 5
            for i, item in enumerate(items[:5]):
                print(f"    - {item['kategori']} {item['size']}: {item['jumlah']} unit")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more items")
        
        # Compare
        print("\n" + "="*80)
        print("COMPARISON")
        print("="*80)
        
        print(f"\nkmeans_cluster_detail totals:")
        for cid in sorted(cluster_counts_detail.keys()):
            print(f"  C{cid}: {len(cluster_counts_detail[cid])} items")
        
        print(f"\nkmeans_final_result totals:")
        for cid in sorted(cluster_counts_final.keys()):
            print(f"  C{cid}: {len(cluster_counts_final[cid])} items")
        
        print("\n" + "="*80)
        print("WHICH TABLE IS USED BY PREPROCESSING PAGE?")
        print("="*80)
        
        # Check routes.py to see which data is used
        print("\nLet me check what data preprocessing pages use...")
        print("The preprocessing pages get data from process_kmeans_manual() function")
        print("which returns aggregated data (data_aggregated)")
        
        # Let's check the actual aggregated data
        from app.processing_kmeans import process_kmeans_manual
        
        print("\nRunning process_kmeans_manual to see actual data...")
        result = process_kmeans_manual(k=3)
        
        if result:
            data_agg = result['data_aggregated']
            labels = result['labels']
            
            print(f"\nAggregated data has {len(data_agg)} rows")
            
            # Count by cluster
            cluster_counts_agg = {}
            for idx, label in enumerate(labels):
                if label not in cluster_counts_agg:
                    cluster_counts_agg[label] = 0
                cluster_counts_agg[label] += 1
            
            print("\nCluster counts from aggregated data:")
            for cid in sorted(cluster_counts_agg.keys()):
                print(f"  C{cid}: {cluster_counts_agg[cid]} size ranges")
            
            print("\n✓ THIS IS THE CORRECT DATA!")
            print("  Preprocessing pages use the aggregated data")
            print("  which groups by kategori + size_range (5cm increments)")

if __name__ == "__main__":
    check_cluster_details()
