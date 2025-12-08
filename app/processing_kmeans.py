import pandas as pd
import numpy as np
from app.models import db, Penjualan, KMeansResult, KMeansClusterDetail


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


class KMeansManual:
    def __init__(self, k=3, max_iterations=100, random_state=42):
        self.k = k
        self.max_iterations = max_iterations
        self.random_state = random_state
        self.centroids = None
        self.labels = None
        self.inertia = None
        self.iteration_history = []

    def fit(self, X):
        np.random.seed(self.random_state)
        n_samples, n_features = X.shape

        # Initialize centroids randomly
        random_indices = np.random.choice(n_samples, self.k, replace=False)
        self.centroids = X[random_indices].copy()
        
        # Store initial centroids
        self.iteration_history.append({
            'iteration': 0,
            'centroids': self.centroids.copy(),
            'distances': None,
            'labels': None
        })

        for iteration in range(self.max_iterations):
            # Assign clusters
            distances = np.sqrt(((X - self.centroids[:, np.newaxis])**2).sum(axis=2))
            self.labels = np.argmin(distances, axis=0)

            # Store iteration data
            self.iteration_history.append({
                'iteration': iteration + 1,
                'centroids': self.centroids.copy(),
                'distances': distances.copy(),
                'labels': self.labels.copy()
            })

            # Update centroids
            new_centroids = np.array([X[self.labels == i].mean(axis=0) if np.sum(self.labels == i) > 0 else self.centroids[i] for i in range(self.k)])

            # Check convergence
            if np.allclose(self.centroids, new_centroids):
                break

            self.centroids = new_centroids

        # Calculate inertia
        distances = np.sqrt(((X - self.centroids[self.labels])**2).sum(axis=1))
        self.inertia = np.sum(distances**2)

    def predict(self, X):
        distances = np.sqrt(((X - self.centroids[:, np.newaxis])**2).sum(axis=2))
        return np.argmin(distances, axis=0)


def davies_bouldin_index_manual(X, labels, centroids):
    """Calculate Davies-Bouldin Index"""
    n_clusters = len(np.unique(labels))
    
    if n_clusters <= 1:
        return 0.0

    # Calculate avg distance from points to centroid
    S = np.zeros(n_clusters)
    for i in range(n_clusters):
        cluster_points = X[labels == i]
        if len(cluster_points) > 0:
            S[i] = np.mean(np.linalg.norm(cluster_points - centroids[i], axis=1))

    # Calculate Davies-Bouldin Index
    db_index = 0.0
    for i in range(n_clusters):
        max_ratio = 0.0
        for j in range(n_clusters):
            if i != j:
                centroid_distance = np.linalg.norm(centroids[i] - centroids[j])
                if centroid_distance > 0:
                    ratio = (S[i] + S[j]) / centroid_distance
                    max_ratio = max(max_ratio, ratio)
        db_index += max_ratio

    return db_index / n_clusters


def get_size_range(harga):
    """Categorize price into size category"""
    try:
        harga = float(harga)
        if harga < 50000:
            return 'Small'
        elif harga < 100000:
            return 'Medium'
        else:
            return 'Large'
    except:
        return 'Unknown'


def get_size_range(size_str):
    """Extract size in cm and group by 5cm ranges"""
    try:
        # Extract number from "XX cm" format
        size_num = int(size_str.replace('cm', '').strip())
        # Group by 5cm: 0-4, 5-9, 10-14, 15-19, 20-24, etc
        range_start = (size_num // 5) * 5
        range_end = range_start + 4
        return f"{range_start}-{range_end} cm"
    except:
        return "Unknown"


def analyze_clustering_results(data, labels, centroids):
    """Analyze clustering results - Standard and Non-Standard breakdown by 5cm size ranges"""
    analysis = {
        'standard': {},
        'non_standard': {}
    }

    # Group data by category and size range
    for i, (idx, row) in enumerate(data.iterrows()):
        cluster_id = labels[i]
        kategori = row.get('kategori', 'Unknown')
        size_str = row.get('size', 'Unknown')
        jumlah = float(row.get('jumlah_terjual', 0)) if row.get('jumlah_terjual') else 0

        # Get size range
        size_range = get_size_range(size_str)
        
        # Skip if size is Unknown
        if size_range == 'Unknown':
            continue

        # Determine category type
        category_type = 'standard' if kategori.lower() in ['standar', 'standard'] else 'non_standard'

        # Initialize size range if not exists
        if size_range not in analysis[category_type]:
            analysis[category_type][size_range] = {
                'terlaris': 0,
                'sedang': 0,
                'kurang_laris': 0,
                'total_terjual': 0,
                'items': [],
                'cluster_totals': {}
            }

        # Add to total
        analysis[category_type][size_range]['total_terjual'] += jumlah
        analysis[category_type][size_range]['items'].append({
            'cluster': cluster_id,
            'kategori': kategori,
            'size': size_str,
            'jumlah_terjual': jumlah
        })
        
        # Sum cluster penjualan for this size range
        if cluster_id not in analysis[category_type][size_range]['cluster_totals']:
            analysis[category_type][size_range]['cluster_totals'][cluster_id] = 0
        analysis[category_type][size_range]['cluster_totals'][cluster_id] += jumlah

    # Categorize based on dominant cluster and remove cluster_totals
    for category_type in ['standard', 'non_standard']:
        for size_range, data_dict in analysis[category_type].items():
            # Get dominant cluster (cluster with highest total penjualan for this size range)
            dominant_cluster = None
            if data_dict['cluster_totals']:
                dominant_cluster = max(data_dict['cluster_totals'], key=data_dict['cluster_totals'].get)
                data_dict['dominant_cluster'] = dominant_cluster
            
            # Determine tier based on cluster ID
            # C0 = Terlaris, C1 = Sedang, C2 = Kurang Laris
            if dominant_cluster == 0:
                data_dict['tier'] = 'terlaris'
            elif dominant_cluster == 1:
                data_dict['tier'] = 'sedang'
            elif dominant_cluster == 2:
                data_dict['tier'] = 'kurang_laris'
            else:
                data_dict['tier'] = 'kurang_laris'  # Default
            
            # Remove cluster_totals from output (no longer needed)
            del data_dict['cluster_totals']

    return analysis


def process_kmeans_manual(k=3):
    """Process data using KMeans clustering"""
    try:
        # Get data from database
        data = Penjualan.query.all()
        if not data:
            return None

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

        # Prepare features for clustering
        X = df[['jumlah_terjual', 'total_harga']].values.astype(float)

        # Normalize data
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0)
        X_normalized = (X - X_mean) / (X_std + 1e-8)

        # Perform KMeans
        kmeans = KMeansManual(k=k, max_iterations=100, random_state=42)
        kmeans.fit(X_normalized)
        labels = kmeans.labels

        # Calculate metrics
        davies_bouldin = davies_bouldin_index_manual(X_normalized, labels, kmeans.centroids)

        # Analyze results
        analysis = analyze_clustering_results(df, labels, kmeans.centroids)
        
        # Convert numpy types for JSON serialization
        analysis = convert_numpy_types(analysis)

        return {
            'kmeans': kmeans,
            'labels': labels,
            'inertia': float(kmeans.inertia),
            'davies_bouldin': float(davies_bouldin),
            'n_iter': kmeans.max_iterations,
            'n_samples': len(data),
            'centroids': kmeans.centroids,
            'data': df,
            'analysis': analysis,
            'X_mean': X_mean,
            'X_std': X_std
        }
    except Exception as e:
        print(f'Error processing KMeans: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def save_kmeans_manual_result(result):
    """Save KMeans result to database"""
    try:
        if not result:
            return False

        # Delete previous results
        KMeansClusterDetail.query.delete()
        kmeans_results = KMeansResult.query.all()
        for r in kmeans_results:
            db.session.delete(r)
        db.session.commit()

        # Save result
        kmeans_result = result['kmeans']
        labels = result['labels']
        data = result['data']
        analysis = result['analysis']

        cluster_dist = {}
        for i in range(result['kmeans'].k):
            cluster_dist[f'cluster_{i}'] = int(np.sum(labels == i))  # Explicitly convert to int

        result_record = KMeansResult(
            k_value=kmeans_result.k,
            inertia=float(result['inertia']),
            davies_bouldin_index=float(result['davies_bouldin']),
            n_iter=result['n_iter'],
            n_samples=result['n_samples'],
            max_iterations=100,
            random_state=42,
            cluster_distribution=cluster_dist,
            analysis_data=analysis,
            data_kategori_count=data['kategori'].nunique(),
            data_size_count=data['size'].nunique(),
            data_penjual_count=data['nama_penjual'].nunique(),
            data_kota_count=data['kota_tujuan'].nunique()
        )
        db.session.add(result_record)
        db.session.flush()

        # Save cluster details
        for idx, item in enumerate(data.itertuples()):
            detail = KMeansClusterDetail(
                kmeans_result_id=result_record.id,
                penjualan_id=item.id,
                cluster_id=int(labels[idx]),
                jumlah_terjual=int(item.jumlah_terjual) if item.jumlah_terjual else 0,
                harga_satuan=float(item.harga_satuan) if item.harga_satuan else 0,
                total_harga=float(item.total_harga) if item.total_harga else 0,
                kategori=item.kategori,
                size=item.size,
                nama_penjual=item.nama_penjual,
                kota_tujuan=item.kota_tujuan
            )
            db.session.add(detail)

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f'Error saving KMeans result: {str(e)}')
        import traceback
        traceback.print_exc()
        return False


def get_kmeans_result():
    """Get last KMeans result from database"""
    try:
        result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
        if not result:
            return None

        # Get detail clusters
        details = KMeansClusterDetail.query.filter_by(kmeans_result_id=result.id).all()

        return {
            'id': result.id,
            'k_value': result.k_value,
            'inertia': result.inertia,
            'davies_bouldin_index': result.davies_bouldin_index,
            'n_iter': result.n_iter,
            'n_samples': result.n_samples,
            'cluster_distribution': result.cluster_distribution,
            'analysis': result.analysis_data,
            'created_at': result.created_at.strftime('%d-%m-%Y %H:%M:%S') if result.created_at else None,
            'details': [{
                'id': d.id,
                'cluster_id': d.cluster_id,
                'kategori': d.kategori,
                'size': d.size,
                'jumlah_terjual': d.jumlah_terjual,
                'harga_satuan': float(d.harga_satuan) if d.harga_satuan else 0,
                'total_harga': float(d.total_harga) if d.total_harga else 0,
                'nama_penjual': d.nama_penjual,
                'kota_tujuan': d.kota_tujuan
            } for d in details]
        }
    except Exception as e:
        print(f'Error getting KMeans result: {str(e)}')
        return None


def get_kmeans_iteration_details(data_df, X_normalized, kmeans_model):
    """Generate detailed iteration information for KMeans"""
    iterations = []
    
    for iter_data in kmeans_model.iteration_history:
        iteration_num = iter_data['iteration']
        centroids = iter_data['centroids']
        distances = iter_data['distances']
        labels = iter_data['labels']
        
        # Build iteration detail
        iter_detail = {
            'iteration': iteration_num,
            'centroids': [
                {
                    'cluster_id': i,
                    'jumlah_terjual': float(centroids[i][0]),
                    'total_harga': float(centroids[i][1])
                }
                for i in range(len(centroids))
            ] if distances is not None else None,
            'cluster_assignments': []
        }
        
        # If distances exist, build assignment details
        if distances is not None and labels is not None:
            distance_data = []
            
            for idx, (data_idx, row) in enumerate(data_df.iterrows()):
                kategori = row.get('kategori', 'Unknown')
                size_str = row.get('size', 'Unknown')
                size_range = get_size_range(size_str)
                
                # Skip unknown sizes
                if size_range == 'Unknown':
                    continue
                
                # Get distances to all centroids for this point
                dist_to_clusters = {
                    f'C{i}': round(float(distances[i][idx]), 2)
                    for i in range(len(centroids))
                }
                
                # Assigned cluster
                assigned_cluster = f'C{labels[idx]}'
                
                distance_data.append({
                    'kategori': kategori,
                    'size': size_range,
                    'jumlah_terjual': float(row.get('jumlah_terjual', 0)),
                    'total_harga': float(row.get('total_harga', 0)),
                    'distances': dist_to_clusters,
                    'assigned_cluster': assigned_cluster
                })
            
            iter_detail['cluster_assignments'] = distance_data
        
        iterations.append(iter_detail)
    
    return iterations
