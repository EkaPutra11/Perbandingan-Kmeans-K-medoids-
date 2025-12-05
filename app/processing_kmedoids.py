import pandas as pd
import numpy as np
from app.models import db, Penjualan, KMedoidsResult, KMedoidsClusterDetail


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


class KMedoidsManual:
    def __init__(self, k=3, max_iterations=100, random_state=42):
        self.k = k
        self.max_iterations = max_iterations
        self.random_state = random_state
        self.medoids = None
        self.labels = None
        self.cost = None

    def fit(self, X):
        np.random.seed(self.random_state)
        n_samples = X.shape[0]

        # Initialize medoids randomly
        medoid_indices = np.random.choice(n_samples, self.k, replace=False)
        self.medoids = medoid_indices.copy()

        for iteration in range(self.max_iterations):
            # Assign clusters
            distances = np.abs(X[self.medoids, :] - X[:, np.newaxis, :]).sum(axis=2)
            self.labels = np.argmin(distances, axis=1)

            # Calculate current cost
            old_cost = np.sum(np.min(distances, axis=1))

            # Try swapping medoids - OPTIMIZED: limit candidates to 10 random non-medoids
            improved = False
            medoid_set = set(self.medoids)
            non_medoids = [i for i in range(n_samples) if i not in medoid_set]

            if len(non_medoids) == 0:
                break

            # Limit swap attempts to 10 random candidates
            max_swap_attempts = min(len(non_medoids), 10)
            swap_candidates = np.random.choice(non_medoids, size=max_swap_attempts, replace=False)

            for new_medoid in swap_candidates:
                for i, old_medoid in enumerate(self.medoids):
                    # Try swapping
                    self.medoids[i] = new_medoid
                    
                    # Calculate new cost
                    distances = np.abs(X[self.medoids, :] - X[:, np.newaxis, :]).sum(axis=2)
                    new_cost = np.sum(np.min(distances, axis=1))

                    # Keep if better
                    if new_cost < old_cost:
                        old_cost = new_cost
                        improved = True
                        break
                    else:
                        self.medoids[i] = old_medoid

                if improved:
                    break

            if not improved:
                break

        # Final assignment
        distances = np.abs(X[self.medoids, :] - X[:, np.newaxis, :]).sum(axis=2)
        self.labels = np.argmin(distances, axis=1)
        self.cost = np.sum(np.min(distances, axis=1))

    def predict(self, X):
        distances = np.abs(X[self.medoids, :] - X[:, np.newaxis, :]).sum(axis=2)
        return np.argmin(distances, axis=1)


def davies_bouldin_index_manual(X, labels, medoids):
    """Calculate Davies-Bouldin Index for KMedoids"""
    n_clusters = len(np.unique(labels))

    if n_clusters <= 1:
        return 0.0

    # Calculate avg distance from points to medoid
    S = np.zeros(n_clusters)
    for i in range(n_clusters):
        cluster_points = X[labels == i]
        if len(cluster_points) > 0:
            S[i] = np.mean(np.linalg.norm(cluster_points - X[medoids[i]], axis=1))

    # Calculate Davies-Bouldin Index
    db_index = 0.0
    for i in range(n_clusters):
        max_ratio = 0.0
        for j in range(n_clusters):
            if i != j:
                medoid_distance = np.linalg.norm(X[medoids[i]] - X[medoids[j]])
                if medoid_distance > 0:
                    ratio = (S[i] + S[j]) / medoid_distance
                    max_ratio = max(max_ratio, ratio)
        db_index += max_ratio

    return db_index / n_clusters


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


def analyze_clustering_results(data, labels, medoid_indices):
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

        # Determine category type
        category_type = 'standard' if kategori.lower() in ['standar', 'standard'] else 'non_standard'

        # Initialize size range if not exists
        if size_range not in analysis[category_type]:
            analysis[category_type][size_range] = {
                'terlaris': 0,
                'sedang': 0,
                'kurang_laris': 0,
                'total_terjual': 0,
                'items': []
            }

        # Add to total
        analysis[category_type][size_range]['total_terjual'] += jumlah
        analysis[category_type][size_range]['items'].append({
            'cluster': cluster_id,
            'kategori': kategori,
            'size': size_str,
            'jumlah_terjual': jumlah
        })

    # Categorize each size range as terlaris/sedang/kurang_laris
    for category_type in ['standard', 'non_standard']:
        for size_range, data_dict in analysis[category_type].items():
            total = data_dict['total_terjual']
            if total >= 100:
                data_dict['tier'] = 'terlaris'
            elif total >= 50:
                data_dict['tier'] = 'sedang'
            else:
                data_dict['tier'] = 'kurang_laris'

    return analysis


def process_kmedoids_manual(k=3):
    """Process data using KMedoids clustering"""
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

        # Perform KMedoids
        kmedoids = KMedoidsManual(k=k, max_iterations=100, random_state=42)
        kmedoids.fit(X_normalized)
        labels = kmedoids.labels

        # Calculate metrics
        davies_bouldin = davies_bouldin_index_manual(X_normalized, labels, kmedoids.medoids)

        # Analyze results
        analysis = analyze_clustering_results(df, labels, kmedoids.medoids)
        
        # Convert numpy types for JSON serialization
        analysis = convert_numpy_types(analysis)

        return {
            'kmedoids': kmedoids,
            'labels': labels,
            'cost': float(kmedoids.cost),
            'davies_bouldin': float(davies_bouldin),
            'n_iter': kmedoids.max_iterations,
            'n_samples': len(data),
            'medoids': kmedoids.medoids,
            'data': df,
            'analysis': analysis,
            'X_mean': X_mean,
            'X_std': X_std
        }
    except Exception as e:
        print(f'Error processing KMedoids: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def save_kmedoids_manual_result(result):
    """Save KMedoids result to database"""
    try:
        if not result:
            return False

        # Delete previous results
        KMedoidsClusterDetail.query.delete()
        kmedoids_results = KMedoidsResult.query.all()
        for r in kmedoids_results:
            db.session.delete(r)
        db.session.commit()

        # Save result
        kmedoids_result = result['kmedoids']
        labels = result['labels']
        data = result['data']
        analysis = result['analysis']

        cluster_dist = {}
        for i in range(kmedoids_result.k):
            cluster_dist[f'cluster_{i}'] = int(np.sum(labels == i))

        result_record = KMedoidsResult(
            k_value=kmedoids_result.k,
            cost=float(result['cost']),
            davies_bouldin_index=float(result['davies_bouldin']),
            n_iter=result['n_iter'],
            n_samples=result['n_samples'],
            max_iterations=100,
            random_state=42,
            medoids=kmedoids_result.medoids.tolist(),
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
            is_medoid = idx in kmedoids_result.medoids
            detail = KMedoidsClusterDetail(
                kmedoids_result_id=result_record.id,
                penjualan_id=item.id,
                cluster_id=int(labels[idx]),
                jumlah_terjual=int(item.jumlah_terjual) if item.jumlah_terjual else 0,
                harga_satuan=float(item.harga_satuan) if item.harga_satuan else 0,
                total_harga=float(item.total_harga) if item.total_harga else 0,
                kategori=item.kategori,
                size=item.size,
                nama_penjual=item.nama_penjual,
                kota_tujuan=item.kota_tujuan,
                is_medoid=is_medoid
            )
            db.session.add(detail)

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f'Error saving KMedoids result: {str(e)}')
        import traceback
        traceback.print_exc()
        return False


def get_kmedoids_result():
    """Get last KMedoids result from database"""
    try:
        result = KMedoidsResult.query.order_by(KMedoidsResult.created_at.desc()).first()
        if not result:
            return None

        # Get detail clusters
        details = KMedoidsClusterDetail.query.filter_by(kmedoids_result_id=result.id).all()

        return {
            'id': result.id,
            'k_value': result.k_value,
            'cost': result.cost,
            'davies_bouldin_index': result.davies_bouldin_index,
            'n_iter': result.n_iter,
            'n_samples': result.n_samples,
            'medoids': result.medoids,
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
                'kota_tujuan': d.kota_tujuan,
                'is_medoid': d.is_medoid
            } for d in details]
        }
    except Exception as e:
        print(f'Error getting KMedoids result: {str(e)}')
        return None
