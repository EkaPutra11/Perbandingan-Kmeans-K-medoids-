"""
Script untuk memeriksa apakah tier data ada di kmeans_final_result
"""
from app import create_app, db
from app.models import KMeansFinalResult, KMeansResult, KMeansClusterDetail

app = create_app()

with app.app_context():
    # Check if there's data in kmeans_final_result
    final_count = KMeansFinalResult.query.count()
    print(f"Total records in kmeans_final_result: {final_count}")
    
    if final_count > 0:
        # Get latest kmeans result
        latest_kmeans = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
        print(f"\nLatest KMeans Result ID: {latest_kmeans.id}")
        print(f"Created at: {latest_kmeans.created_at}")
        
        # Calculate tier mapping (same logic as routes.py)
        cluster_details = KMeansClusterDetail.query.filter_by(
            kmeans_result_id=latest_kmeans.id
        ).all()
        
        cluster_totals = {}
        cluster_counts = {}
        
        for detail in cluster_details:
            cid = detail.cluster_id
            if cid not in cluster_totals:
                cluster_totals[cid] = 0
                cluster_counts[cid] = 0
            cluster_totals[cid] += detail.jumlah_terjual
            cluster_counts[cid] += 1
        
        # Calculate average and rank
        cluster_scores = []
        for cid in cluster_totals:
            avg = cluster_totals[cid] / cluster_counts[cid] if cluster_counts[cid] > 0 else 0
            cluster_scores.append({'cluster_id': cid, 'score': avg})
            print(f"Cluster {cid}: avg = {avg:.2f}, count = {cluster_counts[cid]}")
        
        # Sort by score descending
        cluster_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Assign tiers
        tier_mapping = {}
        if len(cluster_scores) >= 3:
            tier_mapping[cluster_scores[0]['cluster_id']] = 'Terlaris'
            tier_mapping[cluster_scores[1]['cluster_id']] = 'Sedang'
            tier_mapping[cluster_scores[2]['cluster_id']] = 'Kurang Laris'
        
        print(f"\nTier Mapping:")
        for cid, tier in tier_mapping.items():
            print(f"  Cluster {cid} -> {tier}")
        
        # Get final results and show with tier
        final_results = KMeansFinalResult.query.filter_by(
            kmeans_result_id=latest_kmeans.id
        ).limit(10).all()
        
        print(f"\nSample data with tier assignment (first 10):")
        for result in final_results:
            tier = tier_mapping.get(result.cluster_id, 'Unknown')
            print(f"  {result.kategori} {result.size_range} | Cluster {result.cluster_id} | Tier: {tier}")
        
        # Count by tier
        tier_counts = {'Terlaris': 0, 'Sedang': 0, 'Kurang Laris': 0}
        all_results = KMeansFinalResult.query.filter_by(
            kmeans_result_id=latest_kmeans.id
        ).all()
        
        for result in all_results:
            tier = tier_mapping.get(result.cluster_id, 'Unknown')
            if tier in tier_counts:
                tier_counts[tier] += 1
        
        print(f"\nTier Distribution:")
        for tier, count in tier_counts.items():
            print(f"  {tier}: {count} products")
    else:
        print("\nNo data in kmeans_final_result table!")
        print("Please run K-Means clustering first.")
