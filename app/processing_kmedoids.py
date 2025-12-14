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
    def __init__(self, k=3, max_iterations=10, random_state=42):
        self.k = k
        self.max_iterations = max_iterations
        self.random_state = random_state
        self.medoids = None
        self.labels = None
        self.cost = None
        self.iteration_history = []  # Track iteration history
        self.distance_matrix = None  # Cache distance matrix
        self.n_iter = 0  # Track actual iterations used

    def _compute_distance_matrix(self, X):
        """Compute and cache the distance matrix once"""
        n_samples = X.shape[0]
        dist_matrix = np.zeros((n_samples, n_samples))
        for i in range(n_samples):
            for j in range(i, n_samples):
                dist = np.sum(np.abs(X[i] - X[j]))
                dist_matrix[i, j] = dist
                dist_matrix[j, i] = dist
        return dist_matrix

    def _medoid_initialization(self, X, distance_matrix):
        """Initialize medoids using total minimum distance approach (similar to K-Medoids++)"""
        np.random.seed(self.random_state)
        n_samples = X.shape[0]
        medoids = []
        
        # Choose first medoid: point with minimum total distance to all other points
        total_distances = distance_matrix.sum(axis=1)
        first_medoid = np.argmin(total_distances)
        medoids.append(first_medoid)
        
        # Choose remaining k-1 medoids
        for _ in range(self.k - 1):
            # Calculate distance to nearest medoid for each point
            min_distances = np.min(distance_matrix[medoids], axis=0)
            # Choose point with maximum distance to nearest medoid
            next_medoid = np.argmax(min_distances)
            medoids.append(next_medoid)
        
        return np.array(medoids)

    def fit(self, X):
        np.random.seed(self.random_state)
        n_samples = X.shape[0]

        # Compute distance matrix once and cache it
        self.distance_matrix = self._compute_distance_matrix(X)

        # Initialize medoids using smart initialization
        self.medoids = self._medoid_initialization(X, self.distance_matrix)
        old_medoids = None

        for iteration in range(self.max_iterations):
            # Assign clusters using cached distance matrix
            distances = self.distance_matrix[self.medoids].T
            self.labels = np.argmin(distances, axis=1)

            # Calculate current cost
            current_cost = np.sum(np.min(distances, axis=1))

            # Store iteration history
            iteration_data = {
                'iteration': int(iteration),
                'medoids': [int(m) for m in self.medoids],
                'medoid_points': X[self.medoids].copy().tolist(),
                'labels': self.labels.copy().tolist(),
                'cost': float(current_cost)
            }
            self.iteration_history.append(iteration_data)

            # Check convergence: if medoids haven't changed
            if old_medoids is not None and np.array_equal(self.medoids, old_medoids):
                self.n_iter = iteration
                self.cost = current_cost
                print(f"K-Medoids converged at iteration {iteration}")
                return
            
            old_medoids = self.medoids.copy()

            # Try swapping medoids - optimized version
            improved = False
            medoid_set = set(self.medoids)
            non_medoids = [i for i in range(n_samples) if i not in medoid_set]

            if len(non_medoids) == 0:
                break

            # Limit swap attempts for efficiency
            max_swap_attempts = min(len(non_medoids), min(10, n_samples // 5))
            if max_swap_attempts > 0:
                swap_candidates = np.random.choice(non_medoids, size=max_swap_attempts, replace=False)

                for new_medoid in swap_candidates:
                    for i, old_medoid in enumerate(self.medoids):
                        # Try swapping using cached distances
                        self.medoids[i] = new_medoid
                        distances = self.distance_matrix[self.medoids].T
                        new_cost = np.sum(np.min(distances, axis=1))

                        # Keep if better
                        if new_cost < current_cost:
                            current_cost = new_cost
                            improved = True
                            break
                        else:
                            self.medoids[i] = old_medoid

                    if improved:
                        break

            if not improved:
                self.n_iter = iteration + 1
                self.cost = current_cost
                print(f"K-Medoids converged at iteration {iteration + 1} (no improvement)")
                return

        # Final assignment
        self.n_iter = self.max_iterations
        distances = self.distance_matrix[self.medoids].T
        self.labels = np.argmin(distances, axis=1)
        self.cost = np.sum(np.min(distances, axis=1))
        print(f"K-Medoids reached max iterations: {self.max_iterations}")

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


def assign_tiers_by_percentile(df_aggregated, cluster_labels):
    """
    ✨ FITUR BARU: Assign tier labels based on PERCENTILE instead of cluster ID
    
    This ensures more balanced distribution:
    - Terlaris: Top 30% (P70-P100)
    - Sedang: Middle 40% (P30-P70)  
    - Kurang Laris: Bottom 30% (P0-P30)
    
    KOLOM TAMBAHAN YANG DIHITUNG:
    1. performance_score: Skor performa (60% jumlah_terjual + 40% total_harga)
    2. avg_price_per_unit: Harga rata-rata per unit terjual
    3. relative_performance: Performa relatif terhadap rata-rata
    """
    df = df_aggregated.copy()
    
    # KOLOM 1: Performance Score (weighted combination)
    # Normalize each feature to 0-1 range
    jumlah_min, jumlah_max = df['jumlah_terjual'].min(), df['jumlah_terjual'].max()
    harga_min, harga_max = df['total_harga'].min(), df['total_harga'].max()
    
    jumlah_norm = (df['jumlah_terjual'] - jumlah_min) / (jumlah_max - jumlah_min + 1e-8)
    harga_norm = (df['total_harga'] - harga_min) / (harga_max - harga_min + 1e-8)
    
    # Weighted score: prioritas lebih ke jumlah terjual (60%) vs harga (40%)
    df['performance_score'] = 0.6 * jumlah_norm + 0.4 * harga_norm
    
    # KOLOM 2: Average price per unit
    df['avg_price_per_unit'] = df['total_harga'] / (df['jumlah_terjual'] + 1e-8)
    
    # KOLOM 3: Relative performance (dibanding mean)
    mean_score = df['performance_score'].mean()
    df['relative_performance'] = (df['performance_score'] / mean_score) * 100
    
    # Calculate percentile thresholds
    p30 = df['performance_score'].quantile(0.30)
    p70 = df['performance_score'].quantile(0.70)
    
    print(f"\n📊 K-MEDOIDS PERCENTILE-BASED TIER ASSIGNMENT:")
    print(f"   P30 (threshold Sedang): {p30:.4f}")
    print(f"   P70 (threshold Terlaris): {p70:.4f}")
    
    # Assign tier labels based on percentile (RETURN INTEGER!)
    tier_labels = []
    tier_counts = {0: 0, 1: 0, 2: 0}
    
    for score in df['performance_score']:
        if score >= p70:
            tier_labels.append(0)  # Terlaris (Top 30%)
            tier_counts[0] += 1
        elif score >= p30:
            tier_labels.append(1)  # Sedang (Middle 40%)
            tier_counts[1] += 1
        else:
            tier_labels.append(2)  # Kurang Laris (Bottom 30%)
            tier_counts[2] += 1
    
    print(f"\n✅ DISTRIBUSI TIER (LEBIH MASUK AKAL):")
    print(f"   Terlaris: {tier_counts[0]} produk ({tier_counts[0]/len(df)*100:.1f}%)")
    print(f"   Sedang: {tier_counts[1]} produk ({tier_counts[1]/len(df)*100:.1f}%)")
    print(f"   Kurang Laris: {tier_counts[2]} produk ({tier_counts[2]/len(df)*100:.1f}%)")
    
    return np.array(tier_labels), df


def aggregate_data_by_size_range(df):
    """Aggregate data by 5cm size ranges and category before clustering"""
    # Group by category and size range, sum the values
    df['size_range'] = df['size'].apply(get_size_range)
    
    # Remove rows with Unknown size range
    df = df[df['size_range'] != 'Unknown'].copy()
    
    # Aggregate by kategori and size_range
    aggregated = df.groupby(['kategori', 'size_range']).agg({
        'jumlah_terjual': 'sum',
        'total_harga': 'sum'
    }).reset_index()
    
    # Keep track of original indices for later reference
    aggregated['original_rows'] = aggregated.apply(
        lambda row: df[(df['kategori'] == row['kategori']) & (df['size_range'] == row['size_range'])].index.tolist(),
        axis=1
    )
    
    return aggregated


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


def analyze_clustering_results_aggregated(df_aggregated, labels, medoid_indices):
    """Analyze clustering results from aggregated data (already grouped by 5cm size ranges)
    
    Returns data grouped by kategori+size_range with their tier assignments
    """
    analysis = {
        'standard': {},
        'non_standard': {}
    }

    # Map tier labels (now integers: 0, 1, 2) to standardized format
    tier_names_map = {
        0: 'terlaris',
        1: 'sedang',
        2: 'kurang_laris'
    }

    # Process aggregated data with tier labels
    # Each row is already a unique kategori+size_range combination
    for i, (idx, row) in enumerate(df_aggregated.iterrows()):
        # labels[i] is now an integer (0, 1, or 2) from percentile assignment
        tier_id = int(labels[i])  # Ensure it's integer
        tier_normalized = tier_names_map.get(tier_id, 'kurang_laris')
        cluster_id = tier_id  # cluster_id = tier_id for frontend (0=Terlaris, 1=Sedang, 2=Kurang Laris)
        
        kategori = row.get('kategori', 'Unknown')
        size_range = row.get('size_range', 'Unknown')
        jumlah = float(row.get('jumlah_terjual', 0)) if row.get('jumlah_terjual') else 0
        total_harga = float(row.get('total_harga', 0)) if row.get('total_harga') else 0

        # Skip if size is Unknown
        if size_range == 'Unknown':
            continue

        # Determine category type
        category_type = 'standard' if kategori.lower() in ['standar', 'standard'] else 'non_standard'

        # Create unique key for this kategori+size_range combination
        unique_key = f"{kategori}_{size_range}"
        
        # Store each kategori+size_range as separate entry
        if unique_key not in analysis[category_type]:
            analysis[category_type][unique_key] = {
                'kategori': kategori,
                'size_range': size_range,
                'total_terjual': jumlah,
                'total_harga': total_harga,
                'tier': tier_normalized,
                'cluster_id': cluster_id,  # Add integer cluster ID for frontend
                'dominant_cluster': cluster_id  # Use cluster_id for compatibility
            }
        else:
            # If somehow there's duplicate (shouldn't happen with aggregated data)
            # Just update the totals
            analysis[category_type][unique_key]['total_terjual'] += jumlah
            analysis[category_type][unique_key]['total_harga'] += total_harga

    return analysis


def process_kmedoids_manual(k=3):
    """Process data using KMedoids clustering with 5cm size range aggregation"""
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

        # Aggregate data by 5cm size ranges first
        df_aggregated = aggregate_data_by_size_range(df)
        
        # Prepare features for clustering (use aggregated data)
        X = df_aggregated[['jumlah_terjual', 'total_harga']].values.astype(float)

        # Normalize data
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0)
        X_normalized = (X - X_mean) / (X_std + 1e-8)

        # Perform KMedoids with optimized parameters
        kmedoids = KMedoidsManual(k=k, max_iterations=10, random_state=42)
        kmedoids.fit(X_normalized)
        cluster_labels = kmedoids.labels
        
        # Apply percentile-based tier assignment
        tier_labels, df_with_scores = assign_tiers_by_percentile(df_aggregated, cluster_labels)
        labels = tier_labels  # Override with percentile-based tiers
        df_aggregated = df_with_scores  # Now includes performance columns

        # Calculate metrics using original cluster labels
        davies_bouldin = davies_bouldin_index_manual(X_normalized, cluster_labels, kmedoids.medoids)

        # Create analysis from aggregated data with labels
        analysis = analyze_clustering_results_aggregated(df_aggregated, labels, kmedoids.medoids)
        
        # Convert numpy types for JSON serialization
        analysis = convert_numpy_types(analysis)

        return {
            'kmedoids': kmedoids,
            'labels': labels,
            'cluster_labels': cluster_labels,  # Keep original cluster labels for distance calculations
            'cost': float(kmedoids.cost),
            'davies_bouldin': float(davies_bouldin),
            'n_iter': kmedoids.n_iter,  # Use actual iterations instead of max
            'n_samples': len(df_aggregated),
            'medoids': kmedoids.medoids,
            'data': df,
            'data_aggregated': df_aggregated,
            'analysis': analysis,
            'X_mean': X_mean,
            'X_std': X_std,
            'X_normalized': X_normalized
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
        tier_labels = result['labels']  # Tier labels for final output
        cluster_labels = result['cluster_labels']  # Original cluster labels for indexing
        data = result['data']
        data_aggregated = result['data_aggregated']
        analysis = result['analysis']

        # Count tier distribution
        tier_counts = {
            'terlaris': int(np.sum(tier_labels == 'Terlaris')),
            'sedang': int(np.sum(tier_labels == 'Sedang')),
            'kurang_laris': int(np.sum(tier_labels == 'Kurang Laris'))
        }
        cluster_dist = tier_counts

        result_record = KMedoidsResult(
            k_value=kmedoids_result.k,
            cost=float(result['cost']),
            davies_bouldin_index=float(result['davies_bouldin']),
            n_iter=result['n_iter'],
            n_samples=result['n_samples'],
            max_iterations=10,
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

        # Prepare data for distance calculation
        X_normalized = result['X_normalized']
        
        # Save cluster details from aggregated data
        for idx, (agg_idx, agg_row) in enumerate(data_aggregated.iterrows()):
            is_medoid = idx in kmedoids_result.medoids
            
            # Calculate distance from point to its medoid using cluster labels
            point = X_normalized[idx]
            medoid_idx = kmedoids_result.medoids[cluster_labels[idx]]
            medoid_point = X_normalized[medoid_idx]
            distance = np.sqrt(np.sum((point - medoid_point) ** 2))
            
            # tier_labels[idx] is already an integer (0, 1, or 2) from percentile assignment
            cluster_id = int(tier_labels[idx])  # Use directly as integer
            
            detail = KMedoidsClusterDetail(
                kmedoids_result_id=result_record.id,
                cluster_id=cluster_id,
                jumlah_terjual=int(agg_row['jumlah_terjual']) if agg_row['jumlah_terjual'] else 0,
                total_harga=float(agg_row['total_harga']) if agg_row['total_harga'] else 0,
                kategori=agg_row['kategori'],
                size=agg_row['size_range'],
                is_medoid=is_medoid,
                distance_to_medoid=float(distance)
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
                'total_harga': float(d.total_harga) if d.total_harga else 0,
                'is_medoid': d.is_medoid
            } for d in details]
        }
    except Exception as e:
        print(f'Error getting KMedoids result: {str(e)}')
        return None
