from flask import Blueprint, render_template, request, jsonify, current_app
from app.processing_kmeans import process_kmeans_manual, save_kmeans_manual_result, get_kmeans_result, get_kmeans_iteration_details
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
    # Get stats
    total_records = Penjualan.query.count()
    standard_count = Penjualan.query.filter_by(kategori='Standard').count()
    non_standard_count = total_records - standard_count
    
    # Get data table
    data_table = get_data_table()
    
    return render_template('index.html', active_page='dashboard', 
                         total_records=total_records,
                         standard_count=standard_count,
                         non_standard_count=non_standard_count,
                         data_table=data_table)


# Upload Data
@main.route('/upload')
def upload_file():
    return render_template('upload.html', active_page='upload')


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
            # Get cluster distribution from result directly
            labels = result.get('labels', [])
            import numpy as np
            cluster_dist = {}
            for i in range(k):
                count = int(np.sum(labels == i)) if hasattr(labels, '__iter__') else 0
                cluster_dist[str(i)] = count
            
            return jsonify({
                'status': 'success',
                'inertia': float(result.get('inertia', 0)),
                'davies_bouldin': float(result.get('davies_bouldin', 0)),
                'analysis': result.get('analysis', {}),
                'cluster_distribution': cluster_dist
            })
        return jsonify({'status': 'error', 'error': 'Failed to process data'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


# Preprocessing KMeans - Get iteration details
@main.route('/preprocessing/kmeans/iterations', methods=['GET'])
def kmeans_iterations():
    """Get detailed iteration steps for KMeans clustering"""
    try:
        from app.processing_kmeans import KMeansManual, analyze_clustering_results, convert_numpy_types
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
        
        # Prepare features for clustering
        X = df[['jumlah_terjual', 'total_harga']].values.astype(float)
        
        # Normalize data
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0)
        X_normalized = (X - X_mean) / (X_std + 1e-8)
        
        # Run KMeans with tracking
        kmeans = KMeansManual(k=3, max_iterations=100, random_state=42)
        kmeans.fit(X_normalized)
        
        # Get iteration details
        iterations = get_kmeans_iteration_details(df, X_normalized, kmeans)
        
        # Get analysis
        analysis = analyze_clustering_results(df, kmeans.labels, kmeans.centroids)
        analysis = convert_numpy_types(analysis)
        
        return jsonify({
            'status': 'success',
            'iterations': iterations,
            'total_iterations': len(iterations),
            'data_count': len(df),
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


# View KMeans Iterations Page
@main.route('/kmeans-iterations')
def view_kmeans_iterations():
    """Display KMeans iterations visualization page"""
    return render_template('kmeans_iterations.html', active_page='kmeans_iterations')



# Preprocessing KMedoids - GET (load previous results)
@main.route('/preprocessing/kmedoids')
def preprocessing_kmedoids():
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
            # Get cluster distribution from result directly
            labels = result.get('labels', [])
            import numpy as np
            cluster_dist = {}
            for i in range(k):
                count = int(np.sum(labels == i)) if hasattr(labels, '__iter__') else 0
                cluster_dist[str(i)] = count
                
            return jsonify({
                'status': 'success',
                'cost': float(result.get('cost', 0)),
                'davies_bouldin': float(result.get('davies_bouldin', 0)),
                'analysis': result.get('analysis', {}),
                'cluster_distribution': cluster_dist
            })
        return jsonify({'status': 'error', 'error': 'Failed to process data'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


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
        # Delete KMeans results and details
        KMeansClusterDetail.query.delete()
        KMeansResult.query.delete()
        
        # Delete KMedoids results and details
        KMedoidsClusterDetail.query.delete()
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
