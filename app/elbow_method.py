import numpy as np
import pandas as pd
from app.models import Penjualan
from app.processing_kmeans import KMeansManual, davies_bouldin_index_manual
from app.processing_kmedoids import KMedoidsManual


def calculate_elbow_kmeans(k_range=range(2, 11)):
    """Calculate elbow method for KMeans"""
    try:
        # Get data
        data = Penjualan.query.all()
        if not data:
            return None

        df = pd.DataFrame([{
            'jumlah_terjual': d.jumlah_terjual,
            'total_harga': float(d.total_harga) if d.total_harga else 0
        } for d in data])

        X = df[['jumlah_terjual', 'total_harga']].values.astype(float)
        
        # Normalize
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0)
        X_normalized = (X - X_mean) / (X_std + 1e-8)

        results = []
        for k in k_range:
            kmeans = KMeansManual(k=k, max_iterations=100, random_state=42)
            kmeans.fit(X_normalized)
            
            dbi = davies_bouldin_index_manual(X_normalized, kmeans.labels, kmeans.centroids)
            
            results.append({
                'k': k,
                'inertia': float(kmeans.inertia),
                'davies_bouldin': float(dbi)
            })

        return results
    except Exception as e:
        print(f'Error calculating elbow KMeans: {str(e)}')
        return None


def calculate_elbow_kmedoids(k_range=range(2, 11)):
    """Calculate elbow method for KMedoids"""
    try:
        # Get data
        data = Penjualan.query.all()
        if not data:
            return None

        df = pd.DataFrame([{
            'jumlah_terjual': d.jumlah_terjual,
            'total_harga': float(d.total_harga) if d.total_harga else 0
        } for d in data])

        X = df[['jumlah_terjual', 'total_harga']].values.astype(float)
        
        # Normalize
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0)
        X_normalized = (X - X_mean) / (X_std + 1e-8)

        results = []
        for k in k_range:
            kmedoids = KMedoidsManual(k=k, max_iterations=100, random_state=42)
            kmedoids.fit(X_normalized)
            
            # Import DBI function from kmedoids module
            from app.processing_kmedoids import davies_bouldin_index_manual as dbi_kmedoids
            dbi = dbi_kmedoids(X_normalized, kmedoids.labels, kmedoids.medoids)
            
            results.append({
                'k': k,
                'cost': float(kmedoids.cost),
                'davies_bouldin': float(dbi)
            })

        return results
    except Exception as e:
        print(f'Error calculating elbow KMedoids: {str(e)}')
        return None
