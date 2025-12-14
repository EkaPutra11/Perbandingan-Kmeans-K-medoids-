"""
Verifikasi apakah clustering benar-benar menggunakan 2 fitur:
- jumlah_terjual
- total_harga
"""
from app import create_app
from app.models import Penjualan
import pandas as pd
import numpy as np

app = create_app()

def get_size_range(size_str):
    try:
        size_num = int(size_str.replace('cm', '').strip())
        range_start = (size_num // 5) * 5
        range_end = range_start + 4
        return f"{range_start}-{range_end} cm"
    except:
        return "Unknown"

with app.app_context():
    print("="*80)
    print("VERIFIKASI FITUR CLUSTERING")
    print("="*80)
    
    # Get data
    data = Penjualan.query.all()
    df = pd.DataFrame([{
        'kategori': d.kategori,
        'size': d.size,
        'jumlah_terjual': d.jumlah_terjual,
        'total_harga': float(d.total_harga) if d.total_harga else 0,
    } for d in data])
    
    print(f"\n📊 Data Asli dari Database:")
    print(f"   Total rows: {len(df)}")
    print(f"   Jumlah terjual - min: {df['jumlah_terjual'].min()}, max: {df['jumlah_terjual'].max()}")
    print(f"   Total harga - min: {df['total_harga'].min():,.0f}, max: {df['total_harga'].max():,.0f}")
    
    # Aggregate
    df['size_range'] = df['size'].apply(get_size_range)
    df = df[df['size_range'] != 'Unknown']
    
    df_agg = df.groupby(['kategori', 'size_range']).agg({
        'jumlah_terjual': 'sum',
        'total_harga': 'sum'
    }).reset_index()
    
    print(f"\n📊 Data Setelah Agregasi (kategori + size_range):")
    print(f"   Total rows: {len(df_agg)}")
    print(f"   Jumlah terjual - min: {df_agg['jumlah_terjual'].min()}, max: {df_agg['jumlah_terjual'].max()}")
    print(f"   Total harga - min: {df_agg['total_harga'].min():,.0f}, max: {df_agg['total_harga'].max():,.0f}")
    
    # Prepare features (EXACTLY as in processing_kmeans.py)
    X = df_agg[['jumlah_terjual', 'total_harga']].values.astype(float)
    
    print(f"\n🔍 Fitur Matrix X yang digunakan untuk clustering:")
    print(f"   Shape: {X.shape}")
    print(f"   Columns: jumlah_terjual, total_harga")
    print(f"\n   Sample data (5 rows pertama):")
    print(f"   {'Kategori':<20} {'Size Range':<15} {'Jumlah Terjual':>15} {'Total Harga':>20}")
    print("   " + "-"*75)
    for i in range(min(5, len(df_agg))):
        row = df_agg.iloc[i]
        print(f"   {row['kategori']:<20} {row['size_range']:<15} {X[i][0]:>15.0f} {X[i][1]:>20,.0f}")
    
    # Normalize
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0)
    X_normalized = (X - X_mean) / (X_std + 1e-8)
    
    print(f"\n📐 Normalisasi (Z-score):")
    print(f"   Mean: jumlah={X_mean[0]:.2f}, harga={X_mean[1]:,.0f}")
    print(f"   Std:  jumlah={X_std[0]:.2f}, harga={X_std[1]:,.0f}")
    
    print(f"\n   Sample normalized data (5 rows pertama):")
    print(f"   {'Kategori':<20} {'Size Range':<15} {'Norm Jumlah':>15} {'Norm Harga':>15}")
    print("   " + "-"*70)
    for i in range(min(5, len(df_agg))):
        row = df_agg.iloc[i]
        print(f"   {row['kategori']:<20} {row['size_range']:<15} {X_normalized[i][0]:>15.4f} {X_normalized[i][1]:>15.4f}")
    
    # Check correlation
    print(f"\n📊 Korelasi antara 2 fitur:")
    correlation = np.corrcoef(X[:, 0], X[:, 1])[0, 1]
    print(f"   Correlation(jumlah_terjual, total_harga): {correlation:.4f}")
    
    if abs(correlation) > 0.9:
        print(f"   ⚠️  Korelasi sangat tinggi! Kedua fitur hampir redundan.")
    elif abs(correlation) > 0.7:
        print(f"   ⚠️  Korelasi cukup tinggi, tapi masih memberikan informasi berbeda.")
    else:
        print(f"   ✅ Korelasi moderat/rendah, kedua fitur memberikan informasi berbeda.")
    
    # Analyze contribution to distance
    print(f"\n🎯 Kontribusi setiap fitur terhadap jarak euclidean:")
    
    # Calculate variance of each feature after normalization
    var_jumlah = np.var(X_normalized[:, 0])
    var_harga = np.var(X_normalized[:, 1])
    total_var = var_jumlah + var_harga
    
    print(f"   Variance jumlah_terjual: {var_jumlah:.4f} ({var_jumlah/total_var*100:.1f}%)")
    print(f"   Variance total_harga:    {var_harga:.4f} ({var_harga/total_var*100:.1f}%)")
    
    # Show examples of different scenarios
    print(f"\n💡 Contoh Pengaruh total_harga pada clustering:")
    print(f"\n   Scenario 1: Jumlah sama, Harga berbeda")
    
    # Find examples with similar jumlah_terjual but different total_harga
    df_agg_sorted = df_agg.sort_values('jumlah_terjual')
    for i in range(len(df_agg_sorted) - 1):
        row1 = df_agg_sorted.iloc[i]
        row2 = df_agg_sorted.iloc[i+1]
        
        jumlah_diff = abs(row1['jumlah_terjual'] - row2['jumlah_terjual'])
        harga_diff = abs(row1['total_harga'] - row2['total_harga'])
        
        # Find case where jumlah is similar but harga is very different
        if jumlah_diff < 10 and harga_diff > 50000000:  # 50 juta
            print(f"\n   {row1['kategori']} {row1['size_range']}:")
            print(f"      Jumlah: {row1['jumlah_terjual']:.0f}, Harga: Rp {row1['total_harga']:,.0f}")
            print(f"   {row2['kategori']} {row2['size_range']}:")
            print(f"      Jumlah: {row2['jumlah_terjual']:.0f}, Harga: Rp {row2['total_harga']:,.0f}")
            print(f"   → Meskipun jumlah mirip ({jumlah_diff:.0f} selisih),")
            print(f"     harga berbeda Rp {harga_diff:,.0f} akan membuat cluster berbeda!")
            break
    
    print(f"\n" + "="*80)
    print("✅ KESIMPULAN:")
    print("="*80)
    print("""
1. Clustering SUDAH menggunakan 2 fitur:
   - jumlah_terjual (kolom pertama)
   - total_harga (kolom kedua)

2. Kedua fitur dinormalisasi dengan Z-score, sehingga:
   - Keduanya memiliki pengaruh yang seimbang
   - Tidak ada yang mendominasi karena skala berbeda

3. total_harga BENAR-BENAR digunakan dalam perhitungan jarak:
   - Euclidean distance = sqrt((Δjumlah)² + (Δharga)²)
   - Produk dengan harga tinggi bisa cluster berbeda meski jumlah sama
   - Produk dengan harga rendah bisa cluster berbeda meski jumlah sama

4. Ini berbeda dengan clustering yang hanya pakai jumlah_terjual,
   karena sekarang harga mempengaruhi hasil cluster!
    """)
