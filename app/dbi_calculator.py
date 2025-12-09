import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
from app.models import Penjualan
from app.processing_kmeans import KMeansManual, davies_bouldin_index_manual as davies_bouldin_kmeans, aggregate_data_by_size_range
from app.processing_kmedoids import KMedoidsManual, davies_bouldin_index_manual as davies_bouldin_kmedoids
import base64
from io import BytesIO


def get_clustering_data():
    """Get data from database, aggregate per 5cm, and normalize it"""
    try:
        # Get data from database
        data = Penjualan.query.all()
        if not data:
            return None, None, None
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'id': d.id,
            'kategori': d.kategori,
            'size': d.size,
            'jumlah_terjual': d.jumlah_terjual,
            'harga_satuan': float(d.harga_satuan) if d.harga_satuan else 0,
            'total_harga': float(d.total_harga) if d.total_harga else 0,
            'nama_penjual': d.nama_penjual,
            'kota_tujuan': d.kota_tujuan
        } for d in data])
        
        # AGGREGATE DATA BY 5CM SIZE RANGE (like processing_kmeans.py does)
        df = aggregate_data_by_size_range(df)
        
        # Prepare features for clustering
        X = df[['jumlah_terjual', 'total_harga']].values.astype(float)
        
        # Normalize
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0)
        X_normalized = (X - X_mean) / (X_std + 1e-8)
        
        return X_normalized, X_mean, X_std
    except Exception as e:
        print(f'Error getting clustering data: {str(e)}')
        return None, None, None


def calculate_dbi_comparison(k_min=2, k_max=10, max_iterations=100):
    """
    Calculate Davies-Bouldin Index for both KMeans and KMedoids
    Using EXACTLY the same method as processing_kmeans.py
    
    Returns:
        dict with keys:
            - list_k: list of K values
            - list_dbi_kmeans: DBI scores for KMeans
            - list_dbi_kmedoids: DBI scores for KMedoids
            - error: error message if any
    """
    try:
        X_normalized, X_mean, X_std = get_clustering_data()
        if X_normalized is None:
            return {
                'status': 'error',
                'message': 'No data available in database'
            }
        
        list_k = []
        list_dbi_kmeans = []
        list_dbi_kmedoids = []
        
        # Validate K range
        if k_min < 2 or k_max < k_min or k_max > 20:
            return {
                'status': 'error',
                'message': 'K minimal harus >= 2, K maksimal >= K minimal, dan <= 20'
            }
        
        # Iterate through K values - EXACTLY like processing_kmeans.py
        for k in range(k_min, k_max + 1):
            # KMeans clustering - EXACTLY like processing_kmeans.py
            kmeans = KMeansManual(k=k, max_iterations=max_iterations, random_state=42)
            kmeans.fit(X_normalized)
            dbi_kmeans = davies_bouldin_kmeans(X_normalized, kmeans.labels, kmeans.centroids)
            
            # KMedoids clustering - EXACTLY like processing_kmedoids.py
            kmedoids = KMedoidsManual(k=k, max_iterations=max_iterations, random_state=42)
            kmedoids.fit(X_normalized)
            dbi_kmedoids = davies_bouldin_kmedoids(X_normalized, kmedoids.labels, kmedoids.medoids)
            
            list_k.append(k)
            list_dbi_kmeans.append(float(dbi_kmeans))
            list_dbi_kmedoids.append(float(dbi_kmedoids))
        
        return {
            'status': 'success',
            'list_k': list_k,
            'list_dbi_kmeans': list_dbi_kmeans,
            'list_dbi_kmedoids': list_dbi_kmedoids
        }
    
    except Exception as e:
        print(f'Error calculating DBI comparison: {str(e)}')
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'message': str(e)
        }


def render_dbi_chart(list_k, list_dbi_kmeans, list_dbi_kmedoids):
    """
    Render DBI comparison chart to Base64 image
    
    Args:
        list_k: list of K values
        list_dbi_kmeans: DBI scores for KMeans
        list_dbi_kmedoids: DBI scores for KMedoids
    
    Returns:
        Base64 encoded PNG image string
    """
    try:
        plt.figure(figsize=(12, 6))
        
        # Plot both lines
        plt.plot(list_k, list_dbi_kmeans, 'o-', color='#0d6efd', linewidth=2.5, markersize=8, label='K-Means')
        plt.plot(list_k, list_dbi_kmedoids, 's-', color='#dc3545', linewidth=2.5, markersize=8, label='K-Medoids')
        
        # Labels and title
        plt.xlabel('Jumlah Cluster (K)', fontsize=12, fontweight='bold')
        plt.ylabel('Davies-Bouldin Index (DBI)', fontsize=12, fontweight='bold')
        plt.title('Perbandingan Davies-Bouldin Index: KMeans vs KMedoids', fontsize=14, fontweight='bold')
        
        # Grid and legend
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11, loc='best')
        plt.xticks(list_k)
        
        # Format y-axis
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.2f}'))
        
        plt.tight_layout()
        
        # Convert to Base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    except Exception as e:
        print(f'Error rendering DBI chart: {str(e)}')
        plt.close()
        return None
