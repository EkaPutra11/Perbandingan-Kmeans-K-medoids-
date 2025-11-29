from flask import Blueprint, render_template

main = Blueprint('main', __name__)

# Dashboard
@main.route('/')
def index():
    return render_template('index.html', active_page='dashboard')


# Upload Data
@main.route('/upload')
def upload_file():
    return render_template('upload.html', active_page='upload')


# Preprocessing KMeans
@main.route('/preprocessing/kmeans')
def preprocessing_kmeans():
    return render_template('preprocessing_kmeans.html', active_page='kmeans')


# Preprocessing KMedoids
@main.route('/preprocessing/kmedoids')
def preprocessing_kmedoids():
    return render_template('preprocessing_kmedoids.html', active_page='kmedoids')


# Elbow Method
@main.route('/elbow')
def elbow_page():
    return render_template('elbow.html', active_page='elbow')


# Hasil Clustering
@main.route('/results')
def results():
    return render_template('results.html', active_page='results')
