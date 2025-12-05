"""
Format clustering results into category-tier analysis
"""
import pandas as pd
from app.models import Penjualan, KMeansResult, KMedoidsResult, KMeansClusterDetail, KMedoidsClusterDetail
import numpy as np


def get_kmeans_labels():
    """Get labels from latest KMeans result"""
    try:
        result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
        if not result:
            return None
        
        # Get all data points with their cluster assignments from details
        details = KMeansClusterDetail.query.filter_by(kmeans_result_id=result.id).all()
        data = Penjualan.query.all()
        
        if len(details) != len(data):
            return None
        
        # Map details by ID
        details_map = {d.penjualan_id: d.cluster_id for d in details}
        labels = np.array([details_map.get(d.id, 0) for d in data])
        return labels
    except:
        return None


def get_kmedoids_labels():
    """Get labels from latest KMedoids result"""
    try:
        result = KMedoidsResult.query.order_by(KMedoidsResult.created_at.desc()).first()
        if not result:
            return None
        
        # Get all data points with their cluster assignments from details
        details = KMedoidsClusterDetail.query.filter_by(kmedoids_result_id=result.id).all()
        data = Penjualan.query.all()
        
        if len(details) != len(data):
            return None
        
        # Map details by ID
        details_map = {d.penjualan_id: d.cluster_id for d in details}
        labels = np.array([details_map.get(d.id, 0) for d in data])
        return labels
    except:
        return None


def get_analysis_by_category(labels, k=3):
    """
    Analyze clustering results by category and tier
    Returns data grouped by Standard/Non-Standard, then by sales tier
    """
    if labels is None:
        return None
    
    data = Penjualan.query.all()
    
    if len(labels) != len(data):
        return None
    
    # Create dataframe
    df = pd.DataFrame([{
        'kategori': d.kategori,
        'size': d.size,
        'jumlah_terjual': d.jumlah_terjual,
        'cluster': labels[i]
    } for i, d in enumerate(data)])
    
    # Categorize by size range (5cm increments)
    def get_size_range(size_str):
        try:
            size = float(size_str)
            lower = int(size // 5) * 5
            upper = lower + 5
            return f"{lower}-{upper - 1} cm"
        except:
            return "Unknown"
    
    df['size_range'] = df['size'].apply(get_size_range)
    
    # Group by kategori_type (Standard/Non-Standard), then by cluster and size_range
    result = {}
    
    # Separate Standard and Non-Standard
    standard_df = df[df['kategori'] == 'Standard']
    non_standard_df = df[df['kategori'] != 'Standard']
    
    # Process Standard
    if len(standard_df) > 0:
        result['STANDARD'] = format_category_analysis(standard_df, k)
    
    # Process Non-Standard
    if len(non_standard_df) > 0:
        result['NON-STANDARD'] = format_category_analysis(non_standard_df, k)
    
    return result


def format_category_analysis(df, k=3):
    """
    Format a category's data by clusters (tiers)
    """
    tiers = {
        0: 'Terlaris',
        1: 'Sedang', 
        2: 'Kurang Laris'
    }
    
    result = {}
    
    for cluster_id in range(k):
        cluster_df = df[df['cluster'] == cluster_id]
        if len(cluster_df) == 0:
            continue
        
        tier_name = tiers.get(cluster_id, f'Tier {cluster_id}')
        
        # Group by kategori and size_range, sum jumlah_terjual
        grouped = cluster_df.groupby(['kategori', 'size_range'])['jumlah_terjual'].sum().sort_values(ascending=False)
        
        items = []
        for (kategori, size_range), total in grouped.items():
            items.append({
                'kategori': kategori,
                'size_range': size_range,
                'total': float(total)
            })
        
        result[tier_name] = items
    
    return result


def format_results_display(kmeans_result, kmedoids_result):
    """
    Format both kmeans and kmedoids results for display
    """
    k = 3  # Fixed to 3 clusters
    
    # Get labels from database
    kmeans_labels = get_kmeans_labels()
    kmedoids_labels = get_kmedoids_labels()
    
    # Get analysis for KMeans
    kmeans_analysis = get_analysis_by_category(kmeans_labels, k)
    kmeans_dbi = kmeans_result.get('davies_bouldin_index', 0) if kmeans_result else 0
    kmeans_inertia = kmeans_result.get('inertia', 0) if kmeans_result else 0
    
    # Get analysis for KMedoids
    kmedoids_analysis = get_analysis_by_category(kmedoids_labels, k)
    kmedoids_dbi = kmedoids_result.get('davies_bouldin_index', 0) if kmedoids_result else 0
    kmedoids_cost = kmedoids_result.get('cost', 0) if kmedoids_result else 0
    
    return {
        'kmeans': {
            'analysis': kmeans_analysis,
            'dbi': kmeans_dbi,
            'inertia': kmeans_inertia
        },
        'kmedoids': {
            'analysis': kmedoids_analysis,
            'dbi': kmedoids_dbi,
            'cost': kmedoids_cost
        }
    }


def get_data_table():
    """
    Get all data from database as table format
    """
    data = Penjualan.query.all()
    
    records = []
    for d in data:
        records.append({
            'ID': d.id,
            'Kategori': d.kategori,
            'Ukuran': d.size,
            'Jumlah Terjual': d.jumlah_terjual,
            'Total Harga': f"Rp {d.total_harga:,.0f}" if d.total_harga else 'N/A'
        })
    
    return records
