"""
Test script untuk membandingkan DBI dengan dan tanpa grouping per 5cm
"""
import pandas as pd
import numpy as np
from app import create_app
from app.models import Penjualan, db
from app.processing_kmeans import (
    KMeansManual, 
    davies_bouldin_index_manual,
    get_size_range
)

app = create_app()
app.app_context().push()

print("=" * 80)
print("COMPARISON: DBI dengan grouping 5cm vs tanpa grouping")
print("=" * 80)

# Load data dari database
penjualan_records = Penjualan.query.all()
print(f"\n✓ Loaded {len(penjualan_records)} records dari database")

# Convert ke DataFrame
data_list = []
for p in penjualan_records:
    data_list.append({
        'kategori': p.kategori,
        'size': p.size,
        'jumlah_terjual': p.jumlah_terjual,
        'harga_satuan': p.harga_satuan,
        'total_harga': p.total_harga,
        'nama_penjual': p.nama_penjual,
        'kota_tujuan': p.kota_tujuan
    })

df_original = pd.DataFrame(data_list)
print(f"✓ DataFrame shape: {df_original.shape}")
print(f"✓ Columns: {df_original.columns.tolist()}")

# ===== SCENARIO 1: WITH 5cm GROUPING (CURRENT) =====
print("\n" + "=" * 80)
print("SCENARIO 1: WITH 5cm SIZE RANGE GROUPING (CURRENT)")
print("=" * 80)

# Add size_range column
df_with_grouping = df_original.copy()
df_with_grouping['size_range'] = df_with_grouping['size'].apply(get_size_range)

print(f"\n✓ Size ranges created:")
print(f"  Unique size ranges: {df_with_grouping['size_range'].nunique()}")
print(f"  Sample size ranges: {df_with_grouping['size_range'].unique()[:5]}")

# Group by size_range and sum jumlah_terjual
df_grouped = df_with_grouping.groupby('size_range')['jumlah_terjual'].sum().reset_index()
print(f"\n✓ Grouped by size_range:")
print(f"  Number of groups: {len(df_grouped)}")
print(f"  Total penjualan after grouping: {df_grouped['jumlah_terjual'].sum()}")

# Prepare data for clustering (using grouped data)
# Create feature matrix from grouped data - use jumlah_terjual as single feature
X_grouped = df_grouped[['jumlah_terjual']].values
print(f"\n✓ Feature matrix shape (with grouping): {X_grouped.shape}")
print(f"  Min jumlah_terjual: {X_grouped.min():.2f}")
print(f"  Max jumlah_terjual: {X_grouped.max():.2f}")
print(f"  Mean jumlah_terjual: {X_grouped.mean():.2f}")

# Standardize features for better clustering
from sklearn.preprocessing import StandardScaler
scaler_grouped = StandardScaler()
X_grouped_scaled = scaler_grouped.fit_transform(X_grouped)

# Run KMeans with grouping (K=3)
print(f"\n✓ Running KMeans with K=3 on GROUPED data...")
kmeans_grouped = KMeansManual(k=3, max_iterations=100, random_state=42)
kmeans_grouped.fit(X_grouped_scaled)
labels_grouped = kmeans_grouped.predict(X_grouped_scaled)

# Calculate DBI with grouping
dbi_grouped = davies_bouldin_index_manual(X_grouped_scaled, labels_grouped, kmeans_grouped.centroids)
inertia_grouped = kmeans_grouped.inertia

print(f"  Inertia (grouped): {inertia_grouped:.4f}")
print(f"  DBI (grouped): {dbi_grouped:.4f}")
print(f"  Cluster distribution: {np.bincount(labels_grouped)}")

# ===== SCENARIO 2: WITHOUT 5cm GROUPING =====
print("\n" + "=" * 80)
print("SCENARIO 2: WITHOUT 5cm GROUPING (USING RAW INDIVIDUAL SIZE)")
print("=" * 80)

df_without_grouping = df_original.copy()

print(f"\n✓ Using raw data without grouping:")
print(f"  Number of records: {len(df_without_grouping)}")
print(f"  Unique sizes: {df_without_grouping['size'].nunique()}")
print(f"  Sample sizes: {df_without_grouping['size'].unique()[:5]}")

# Prepare data for clustering (using individual records)
X_ungrouped = df_without_grouping[['jumlah_terjual']].values
print(f"\n✓ Feature matrix shape (without grouping): {X_ungrouped.shape}")
print(f"  Min jumlah_terjual: {X_ungrouped.min():.2f}")
print(f"  Max jumlah_terjual: {X_ungrouped.max():.2f}")
print(f"  Mean jumlah_terjual: {X_ungrouped.mean():.2f}")

# Standardize features
scaler_ungrouped = StandardScaler()
X_ungrouped_scaled = scaler_ungrouped.fit_transform(X_ungrouped)

# Run KMeans without grouping (K=3)
print(f"\n✓ Running KMeans with K=3 on UNGROUPED data...")
kmeans_ungrouped = KMeansManual(k=3, max_iterations=100, random_state=42)
kmeans_ungrouped.fit(X_ungrouped_scaled)
labels_ungrouped = kmeans_ungrouped.predict(X_ungrouped_scaled)

# Calculate DBI without grouping
dbi_ungrouped = davies_bouldin_index_manual(X_ungrouped_scaled, labels_ungrouped, kmeans_ungrouped.centroids)
inertia_ungrouped = kmeans_ungrouped.inertia

print(f"  Inertia (ungrouped): {inertia_ungrouped:.4f}")
print(f"  DBI (ungrouped): {dbi_ungrouped:.4f}")
print(f"  Cluster distribution: {np.bincount(labels_ungrouped)}")

# ===== COMPARISON =====
print("\n" + "=" * 80)
print("📊 HASIL PERBANDINGAN")
print("=" * 80)

comparison_data = {
    'Metric': ['Inertia', 'DBI', 'Data Points', 'Kualitas Clustering'],
    'With 5cm Grouping': [
        f'{inertia_grouped:.4f}',
        f'{dbi_grouped:.4f}',
        f'{len(df_grouped)} groups',
        'Sangat Baik (DBI < 1.0)' if dbi_grouped < 1.0 else 'Baik (DBI 1.0-1.5)' if dbi_grouped < 1.5 else 'Perlu Peningkatan'
    ],
    'Without Grouping': [
        f'{inertia_ungrouped:.4f}',
        f'{dbi_ungrouped:.4f}',
        f'{len(df_without_grouping)} records',
        'Sangat Baik (DBI < 1.0)' if dbi_ungrouped < 1.0 else 'Baik (DBI 1.0-1.5)' if dbi_ungrouped < 1.5 else 'Perlu Peningkatan'
    ]
}

comparison_df = pd.DataFrame(comparison_data)
print("\n" + comparison_df.to_string(index=False))

# Calculate difference
dbi_diff = dbi_ungrouped - dbi_grouped
inertia_diff = inertia_ungrouped - inertia_grouped
pct_diff = (dbi_diff / dbi_grouped) * 100 if dbi_grouped != 0 else 0

print("\n" + "=" * 80)
print("📈 ANALISIS PERBEDAAN")
print("=" * 80)
print(f"\nInertia Difference: {inertia_diff:.4f}")
print(f"DBI Difference: {dbi_diff:.4f}")
print(f"DBI % Change: {pct_diff:.2f}%")

if dbi_ungrouped < dbi_grouped:
    print(f"\n✓ Tanpa grouping menghasilkan DBI LEBIH BAIK (lebih rendah)")
    print(f"  Improvement: {abs(pct_diff):.2f}%")
elif dbi_ungrouped > dbi_grouped:
    print(f"\n✗ Tanpa grouping menghasilkan DBI LEBIH BURUK (lebih tinggi)")
    print(f"  Degradation: {pct_diff:.2f}%")
else:
    print(f"\n⚖ DBI sama persis")

# Additional insights
print("\n" + "=" * 80)
print("💡 INSIGHTS")
print("=" * 80)
print(f"""
1. DENGAN 5CM GROUPING (CURRENT):
   - Mengurangi dimensi data dari {len(df_without_grouping)} menjadi {len(df_grouped)} observasi
   - DBI: {dbi_grouped:.4f} - {'SANGAT BAIK' if dbi_grouped < 1.0 else 'BAIK' if dbi_grouped < 1.5 else 'PERLU PENINGKATAN'}
   - Interpretasi: Cluster-cluster terpisah dengan baik
   
2. TANPA GROUPING (RAW DATA):
   - Menggunakan semua {len(df_without_grouping)} records mentah
   - DBI: {dbi_ungrouped:.4f} - {'SANGAT BAIK' if dbi_ungrouped < 1.0 else 'BAIK' if dbi_ungrouped < 1.5 else 'PERLU PENINGKATAN'}
   - Interpretasi: {'Cluster-cluster lebih terpisah' if dbi_ungrouped < dbi_grouped else 'Cluster-cluster lebih overlap'}

3. REKOMENDASI:
   {'✓ Tetap gunakan 5cm grouping - lebih stabil dan menghasilkan DBI lebih baik' if dbi_grouped < dbi_ungrouped else '✓ Pertimbangkan menggunakan raw data - menghasilkan DBI lebih baik'}
   - Grouping membantu mengurangi noise dan dimensionalitas
   - DBI {dbi_grouped:.4f} menunjukkan clustering berkualitas {'sangat' if dbi_grouped < 1.0 else ''} baik
""")

print("\n" + "=" * 80)
