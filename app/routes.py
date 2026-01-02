from flask import Blueprint, render_template, request, jsonify, current_app
from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result, get_kmeans_result, get_kmeans_iteration_details, save_kmeans_final_result
from app.processing_kmedoids import process_kmedoids_manual, save_kmedoids_manual_result, get_kmedoids_result
from app.dbi_calculator import calculate_dbi_comparison, render_dbi_chart
from app.analysis_formatter import format_results_display, get_data_table, format_category_analysis
from app.models import db, Penjualan, KMeansResult, KMedoidsResult, KMeansClusterDetail, KMedoidsClusterDetail
import pandas as pd
import os
from werkzeug.utils import secure_filename
import base64
from io import BytesIO

main = Blueprint('main', __name__)


# Dashboard
@main.route('/')
def index():
    from app.models import KMeansFinalResult
    import numpy as np
    
    # Get stats
    total_records = Penjualan.query.count()
    standard_count = Penjualan.query.filter_by(kategori='Standard').count()
    non_standard_count = total_records - standard_count
    
    # Get data table
    data_table = get_data_table()
    
    # Get clustering results from kmeans_final_result
    clustering_results = []
    
    # Direct tier mapping: cluster_id now directly represents tier (from percentile assignment)
    tier_mapping = {
        0: 'Terlaris',
        1: 'Sedang', 
        2: 'Kurang Laris'
    }
    
    try:
        # Check if there's any data in kmeans_final_result
        has_final_results = KMeansFinalResult.query.first() is not None
        
        if has_final_results:
            # Get latest kmeans result
            latest_kmeans = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
            
            if latest_kmeans:
                # Get final results with tier
                final_results = KMeansFinalResult.query.filter_by(
                    kmeans_result_id=latest_kmeans.id
                ).all()
                
                print(f"Found {len(final_results)} records in kmeans_final_result")
                
                for result in final_results:
                    # cluster_id now directly maps to tier (from percentile-based assignment)
                    tier = tier_mapping.get(result.cluster_id, 'Unknown')
                    clustering_results.append({
                        'kategori': result.kategori,
                        'size_range': result.size_range,
                        'jumlah_terjual': result.jumlah_terjual,
                        'cluster_id': result.cluster_id,
                        'tier': tier
                    })
    except Exception as e:
        print(f"Error loading clustering results: {e}")
        import traceback
        traceback.print_exc()
    
    return render_template('index.html', active_page='dashboard', 
                         total_records=total_records,
                         standard_count=standard_count,
                         non_standard_count=non_standard_count,
                         data_table=data_table,
                         clustering_results=clustering_results)


# Upload Data
@main.route('/upload')
def upload_file():
    # Get all data for table
    data = Penjualan.query.all()
    
    # Format data for table
    data_table = []
    for idx, item in enumerate(data, start=1):
        data_table.append({
            'ID': idx,
            'Kategori': item.kategori,
            'Ukuran': item.size,
            'Jumlah Terjual': item.jumlah_terjual,
            'Total Harga': f"Rp {item.total_harga:,.0f}" if item.total_harga else "Rp 0"
        })
    
    return render_template('upload.html', active_page='upload', data_table=data_table)


# Upload CSV File
@main.route('/upload', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'})

        if not file.filename.endswith('.csv'):
            return jsonify({'status': 'error', 'message': 'File must be CSV format'})

        # Read CSV
        df = pd.read_csv(file)
        
        # Validate columns
        required_cols = ['Kategori', 'Size', 'Jumlah_Terjual', 'Harga_Satuan', 'Total_Harga', 'Nama_Penjual', 'Kota_Tujuan']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({'status': 'error', 'message': f'Missing columns: {", ".join(missing_cols)}'})

        # Clear existing data
        Penjualan.query.delete()
        db.session.commit()

        # Insert new data
        for idx, row in df.iterrows():
            try:
                penjualan = Penjualan(
                    kategori=row['Kategori'],
                    size=row['Size'],
                    jumlah_terjual=int(row['Jumlah_Terjual']) if row['Jumlah_Terjual'] else 0,
                    harga_satuan=float(str(row['Harga_Satuan']).replace('.', '')) if row['Harga_Satuan'] else 0,
                    total_harga=float(str(row['Total_Harga']).replace('.', '')) if row['Total_Harga'] else 0,
                    nama_penjual=row['Nama_Penjual'],
                    kota_tujuan=row['Kota_Tujuan']
                )
                db.session.add(penjualan)
            except Exception as e:
                print(f'Error inserting row {idx}: {str(e)}')
                continue

        db.session.commit()
        return jsonify({'status': 'success', 'message': f'✓ Upload berhasil! {len(df)} records imported'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Upload failed: {str(e)}'})


# Get Data Statistics
@main.route('/data/stats')
def data_stats():
    try:
        total = Penjualan.query.count()
        standard = Penjualan.query.filter_by(kategori='Standard').count()
        non_standard = total - standard

        return jsonify({
            'total_records': total,
            'standard_count': standard,
            'non_standard_count': non_standard
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# Preprocessing KMeans - GET (load previous results)
@main.route('/preprocessing/kmeans')
def preprocessing_kmeans():
    results = get_kmeans_result()
    return render_template('preprocessing_kmeans.html', active_page='kmeans', results=results)


# Preprocessing KMeans - POST (run clustering)
@main.route('/preprocessing/kmeans', methods=['POST'])
def process_kmeans():
    try:
        k = request.form.get('k', 3, type=int)
        result = process_kmeans_manual(k=k)
        if result:
            save_kmeans_manual_result(result)
            
            # Save to kmeans_final_result table
            latest_result = KMeansResult.query.order_by(KMeansResult.created_at.desc()).first()
            if latest_result:
                save_kmeans_final_result(latest_result.id)
            
            # Get tier distribution from saved result (already calculated in save function)
            tier_distribution = latest_result.cluster_distribution if latest_result else {}
            
            return jsonify({
                'status': 'success',
                'inertia': float(result.get('inertia', 0)),
                'davies_bouldin': float(result.get('davies_bouldin', 0)),
                'n_iter': int(result.get('n_iter', 0)),
                'max_iterations': int(result.get('max_iterations', 10)),
                'analysis': result.get('analysis', {}),
                'cluster_distribution': tier_distribution
            })
        return jsonify({'status': 'error', 'error': 'Failed to process data'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


# Preprocessing KMeans - Get iteration details
@main.route('/preprocessing/kmeans/iterations', methods=['GET'])
def kmeans_iterations():
    """Get detailed iteration steps for KMeans clustering"""
    try:
        from app.processing_kmeans import KMeansManual, analyze_clustering_results, aggregate_data_by_size_range, convert_numpy_types
        from scipy.spatial.distance import euclidean
        import numpy as np
        
        # Get all data
        data = Penjualan.query.all()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data available'})
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'id': d.id,
            'kategori': d.kategori,
            'size': d.size,
            'jumlah_terjual': float(d.jumlah_terjual),
            'total_harga': float(d.total_harga) if d.total_harga else 0
        } for d in data])
        
        # Aggregate data by 5cm size ranges like in process_kmeans_manual
        df_aggregated = aggregate_data_by_size_range(df)
        
        # Prepare features for clustering (aggregated data)
        # ✨ CLUSTERING DENGAN 2 FITUR: jumlah_terjual dan jumlah_transaksi
        X = df_aggregated[['jumlah_terjual', 'jumlah_transaksi']].values.astype(float)
        
        # Normalize data
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0)
        X_normalized = (X - X_mean) / (X_std + 1e-8)
        
        # Run KMeans with tracking
        kmeans = KMeansManual(k=3, max_iterations=100, random_state=42)
        kmeans.fit(X_normalized)
        
        # Enrich iteration history with cluster assignments and distances
        iterations = []
        if kmeans.iteration_history:
            for iter_data in kmeans.iteration_history:
                # Skip initial iteration (no labels yet)
                if iter_data['labels'] is None:
                    continue
                
                # Calculate distances from each point to each centroid
                centroids = iter_data['centroids']
                labels = iter_data['labels']
                
                # Format centroids as objects with cluster info
                centroids_formatted = []
                for c_id, centroid in enumerate(centroids):
                    centroids_formatted.append({
                        'cluster_id': int(c_id),
                        'jumlah_terjual': float(centroid[0]),
                        'jumlah_transaksi': float(centroid[1])
                    })
                
                cluster_assignments = []
                for idx, row in df_aggregated.iterrows():
                    distances = {}
                    for c_id, centroid in enumerate(centroids):
                        dist = euclidean(X_normalized[idx], centroid)
                        distances[f'C{c_id}'] = float(dist)
                    
                    cluster_assignments.append({
                        'kategori': row['kategori'],
                        'size_range': row['size_range'],
                        'jumlah_terjual': int(row['jumlah_terjual']),
                        'distances': distances,
                        'assigned_cluster': f"C{int(labels[idx])}"
                    })
                
                # Convert for JSON serialization
                iter_data_copy = iter_data.copy()
                iter_data_copy['centroids'] = centroids_formatted
                iter_data_copy['labels'] = labels.tolist() if hasattr(labels, 'tolist') else labels
                if iter_data_copy.get('distances') is not None:
                    iter_data_copy['distances'] = iter_data_copy['distances'].tolist() if hasattr(iter_data_copy['distances'], 'tolist') else iter_data_copy['distances']
                iter_data_copy['cluster_assignments'] = cluster_assignments
                iterations.append(iter_data_copy)
        
        return jsonify({
            'status': 'success',
            'iterations': iterations,
            'total_iterations': len(iterations),
            'data_count': len(df_aggregated)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'error': str(e)})


# View KMeans Iterations Page
@main.route('/kmeans-iterations')
def view_kmeans_iterations():
    """Display KMeans iterations visualization page"""
    return render_template('kmeans_iterations.html', active_page='kmeans_iterations')


# Preprocessing KMedoids - GET (load previous results)
@main.route('/preprocessing/kmedoids')
def preprocessing_kmedoids():
    # Check if JSON is requested
    if request.headers.get('Accept') == 'application/json':
        results = get_kmedoids_result()
        if results:
            # Get metadata from database
            last_result = KMedoidsResult.query.order_by(KMedoidsResult.created_at.desc()).first()
            if last_result:
                # Format results array for frontend
                results_array = [
                    {
                        'id': d['id'],
                        'cluster_id': d['cluster_id'],
                        'kategori': d['kategori'],
                        'size_range': d['size'],
                        'jumlah_terjual': d['jumlah_terjual'],
                        'total_harga': d['total_harga'],
                        'is_medoid': d['is_medoid']
                    } for d in results.get('details', [])
                ]
                
                return jsonify({
                    'status': 'success',
                    'cost': float(last_result.cost),
                    'davies_bouldin': float(last_result.davies_bouldin_index),
                    'results': results_array
                })
        return jsonify({
            'status': 'success',
            'cost': None,
            'davies_bouldin': None,
            'results': []
        })
    
    # Otherwise render template
    results = get_kmedoids_result()
    return render_template('preprocessing_kmedoids.html', active_page='kmedoids', results=results)


# Preprocessing KMedoids - POST (run clustering)
@main.route('/preprocessing/kmedoids', methods=['POST'])
def process_kmedoids():
    try:
        k = request.form.get('k', 3, type=int)
        result = process_kmedoids_manual(k=k)
        if result:
            save_kmedoids_manual_result(result)
            
            # Get tier distribution from saved result (already calculated in save function)
            latest_result = KMedoidsResult.query.order_by(KMedoidsResult.created_at.desc()).first()
            tier_distribution = latest_result.cluster_distribution if latest_result else {}
            
            return jsonify({
                'status': 'success',
                'cost': float(result.get('cost', 0)),
                'davies_bouldin': float(result.get('davies_bouldin', 0)),
                'n_iter': int(result.get('n_iter', 0)),
                'max_iterations': int(result.get('max_iterations', 10)),
                'medoids': result.get('medoids', []).tolist() if hasattr(result.get('medoids', []), 'tolist') else result.get('medoids', []),
                'analysis': result.get('analysis', {}),
                'cluster_distribution': tier_distribution
            })
        return jsonify({'status': 'error', 'error': 'Failed to process data'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


# Preprocessing KMedoids - GET iteration details
@main.route('/preprocessing/kmedoids/iterations', methods=['GET'])
def kmedoids_iterations():
    """Get detailed iteration steps for KMedoids clustering with aggregated data"""
    try:
        from app.processing_kmedoids import KMedoidsManual, aggregate_data_by_size_range
        import numpy as np
        from scipy.spatial.distance import euclidean
        
        # Get all data
        data = Penjualan.query.all()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data available'})
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'id': d.id,
            'kategori': d.kategori,
            'size': d.size,
            'jumlah_terjual': float(d.jumlah_terjual),
            'total_harga': float(d.total_harga) if d.total_harga else 0
        } for d in data])
        
        # Aggregate data by 5cm size ranges like in process_kmedoids_manual
        df_aggregated = aggregate_data_by_size_range(df)
        
        # Prepare features for clustering (aggregated data)
        # ✨ CLUSTERING DENGAN 2 FITUR: jumlah_terjual dan jumlah_transaksi
        X = df_aggregated[['jumlah_terjual', 'jumlah_transaksi']].values.astype(float)
        
        # Normalize data
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0)
        X_normalized = (X - X_mean) / (X_std + 1e-8)
        
        # Run KMedoids with tracking
        kmedoids = KMedoidsManual(k=3, max_iterations=100, random_state=42)
        kmedoids.fit(X_normalized)
        
        # Enrich iteration history with cluster assignments and distances
        iterations = []
        if kmedoids.iteration_history:
            for iter_data in kmedoids.iteration_history:
                # Calculate distances from each point to each medoid
                medoid_points = iter_data['medoid_points']
                labels = iter_data['labels']
                
                # Format medoids as objects with cluster info
                medoids_formatted = []
                for c_id, medoid in enumerate(medoid_points):
                    medoids_formatted.append({
                        'cluster_id': int(c_id),
                        'jumlah_terjual': float(medoid[0]),
                        'jumlah_transaksi': float(medoid[1])
                    })
                
                cluster_assignments = []
                for idx, row in df_aggregated.iterrows():
                    distances = {}
                    for c_id, medoid_point in enumerate(medoid_points):
                        dist = euclidean(X_normalized[idx], medoid_point)
                        distances[f'C{c_id}'] = float(dist)
                    
                    cluster_assignments.append({
                        'kategori': row['kategori'],
                        'size_range': row['size_range'],
                        'jumlah_terjual': int(row['jumlah_terjual']),
                        'distances': distances,
                        'assigned_cluster': f"C{int(labels[idx])}"
                    })
                
                # Convert to JSON-serializable format
                iter_data_copy = iter_data.copy()
                iter_data_copy['medoid_points'] = medoids_formatted
                iter_data_copy['labels'] = labels.tolist() if hasattr(labels, 'tolist') else labels
                iter_data_copy['cluster_assignments'] = cluster_assignments
                iterations.append(iter_data_copy)
        
        return jsonify({
            'status': 'success',
            'iterations': iterations,
            'total_iterations': len(iterations),
            'data_count': len(df_aggregated)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'error': str(e), 'message': 'Failed to get iterations'})


# Delete All Data
@main.route('/delete/data', methods=['POST'])
def delete_data():
    try:
        # Delete all from penjualan table
        Penjualan.query.delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'All data deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})


# Delete Clustering Results
@main.route('/delete/results', methods=['POST'])
def delete_results():
    try:
        from app.models import KMeansFinalResult
        
        # Delete in correct order to avoid foreign key constraints
        # 1. Delete child tables first
        KMeansFinalResult.query.delete()  # Delete final results first!
        KMeansClusterDetail.query.delete()
        KMedoidsClusterDetail.query.delete()
        
        # 2. Delete parent tables
        KMeansResult.query.delete()
        KMedoidsResult.query.delete()
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'All clustering results deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})


# Hasil Clustering
@main.route('/results')
def results():
    kmeans = get_kmeans_result()
    kmedoids = get_kmedoids_result()
    
    # Format results for display
    if kmeans and kmedoids:
        formatted_results = format_results_display(kmeans, kmedoids)
    else:
        formatted_results = None
    
    return render_template('results.html', active_page='results', 
                         kmeans=kmeans, kmedoids=kmedoids,
                         formatted_results=formatted_results)


# Davies-Bouldin Index Comparison
@main.route('/dbi', methods=['GET', 'POST'])
def dbi_comparison():
    try:
        if request.method == 'GET':
            # Show form
            return render_template('dbi.html', active_page='dbi')
        
        # POST request - process DBI calculation
        data = request.get_json() if request.is_json else request.form
        k_min = int(data.get('k_min', 2))
        k_max = int(data.get('k_max', 10))
        max_iter = int(data.get('max_iter', 100))
        
        # Validate inputs
        if k_min < 2 or k_max < k_min or k_max > 20:
            return jsonify({
                'status': 'error',
                'message': 'K minimal harus >= 2, K maksimal >= K minimal, dan <= 20'
            })
        
        # Calculate DBI comparison
        result = calculate_dbi_comparison(k_min=k_min, k_max=k_max, max_iterations=max_iter)
        
        if result['status'] != 'success':
            return jsonify(result)
        
        # Render chart
        chart_base64 = render_dbi_chart(
            result['list_k'],
            result['list_dbi_kmeans'],
            result['list_dbi_kmedoids']
        )
        
        if not chart_base64:
            return jsonify({
                'status': 'error',
                'message': 'Failed to render chart'
            })
        
        return jsonify({
            'status': 'success',
            'list_k': result['list_k'],
            'list_dbi_kmeans': result['list_dbi_kmeans'],
            'list_dbi_kmedoids': result['list_dbi_kmedoids'],
            'chart': chart_base64
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })
