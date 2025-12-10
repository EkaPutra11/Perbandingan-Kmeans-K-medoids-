from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Penjualan(db.Model):
    __tablename__ = 'penjualan'

    id = db.Column(db.Integer, primary_key=True)
    tanggal_terjual = db.Column(db.Date, nullable=False)
    kategori = db.Column(db.String(100))
    size = db.Column(db.String(50))
    jumlah_terjual = db.Column(db.Integer)
    harga_satuan = db.Column(db.Numeric(15, 0))
    total_harga = db.Column(db.Numeric(18, 0))
    nama_penjual = db.Column(db.String(100))
    kota_tujuan = db.Column(db.String(100))


class KMeansResult(db.Model):
    __tablename__ = 'kmeans_result'

    id = db.Column(db.Integer, primary_key=True)
    k_value = db.Column(db.Integer, nullable=False)
    inertia = db.Column(db.Float, nullable=False)
    davies_bouldin_index = db.Column(db.Float, nullable=False)
    n_iter = db.Column(db.Integer)
    n_samples = db.Column(db.Integer)
    max_iterations = db.Column(db.Integer)
    random_state = db.Column(db.Integer)
    cluster_distribution = db.Column(db.JSON)
    analysis_data = db.Column(db.JSON)
    data_kategori_count = db.Column(db.Integer)
    data_size_count = db.Column(db.Integer)
    data_penjual_count = db.Column(db.Integer)
    data_kota_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship dengan detail cluster
    detail_clusters = db.relationship('KMeansClusterDetail', backref='kmeans_result', cascade='all, delete-orphan')


class KMedoidsResult(db.Model):
    __tablename__ = 'kmedoids_result'

    id = db.Column(db.Integer, primary_key=True)
    k_value = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    davies_bouldin_index = db.Column(db.Float, nullable=False)
    n_iter = db.Column(db.Integer)
    n_samples = db.Column(db.Integer)
    max_iterations = db.Column(db.Integer)
    random_state = db.Column(db.Integer)
    medoids = db.Column(db.JSON)
    cluster_distribution = db.Column(db.JSON)
    analysis_data = db.Column(db.JSON)
    data_kategori_count = db.Column(db.Integer)
    data_size_count = db.Column(db.Integer)
    data_penjual_count = db.Column(db.Integer)
    data_kota_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship dengan detail cluster
    detail_clusters = db.relationship('KMedoidsClusterDetail', backref='kmedoids_result', cascade='all, delete-orphan')


class KMeansClusterDetail(db.Model):
    __tablename__ = 'kmeans_cluster_detail'

    id = db.Column(db.Integer, primary_key=True)
    kmeans_result_id = db.Column(db.Integer, db.ForeignKey('kmeans_result.id'), nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)
    kategori = db.Column(db.String(100))
    size = db.Column(db.String(50))
    jumlah_terjual = db.Column(db.Integer)
    total_harga = db.Column(db.Numeric(18, 0))
    distance_to_centroid = db.Column(db.Float)


class KMedoidsClusterDetail(db.Model):
    __tablename__ = 'kmedoids_cluster_detail'

    id = db.Column(db.Integer, primary_key=True)
    kmedoids_result_id = db.Column(db.Integer, db.ForeignKey('kmedoids_result.id'), nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)
    kategori = db.Column(db.String(100))
    size = db.Column(db.String(50))
    jumlah_terjual = db.Column(db.Integer)
    total_harga = db.Column(db.Numeric(18, 0))
    distance_to_medoid = db.Column(db.Float)
    is_medoid = db.Column(db.Boolean)


class KMeansFinalResult(db.Model):
    __tablename__ = 'kmeans_final_result'

    id = db.Column(db.Integer, primary_key=True)
    kmeans_result_id = db.Column(db.Integer, db.ForeignKey('kmeans_result.id'), nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)
    kategori = db.Column(db.String(100))
    size_range = db.Column(db.String(50))
    jumlah_terjual = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    kmeans_result = db.relationship('KMeansResult', backref='final_results')
