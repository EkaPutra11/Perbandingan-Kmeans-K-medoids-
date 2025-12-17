"""
Analisis perbandingan clustering:
1. Standard + Non-Standard DIGABUNG (kondisi saat ini)
2. Standard dan Non-Standard DIPISAH
"""
from app import create_app, db
from app.models import Penjualan
import pandas as pd
import numpy as np

app = create_app()

def get_size_range(size_str):
    """Extract size in cm and group by 5cm ranges"""
    try:
        size_num = int(size_str.replace('cm', '').strip())
        range_start = (size_num // 5) * 5
        range_end = range_start + 4
        return f"{range_start}-{range_end} cm"
    except:
        return "Unknown"

with app.app_context():
    # Get all data
    data = Penjualan.query.all()
    
    df = pd.DataFrame([{
        'kategori': d.kategori,
        'size': d.size,
        'jumlah_terjual': d.jumlah_terjual,
        'total_harga': float(d.total_harga) if d.total_harga else 0,
    } for d in data])
    
    # Add size_range
    df['size_range'] = df['size'].apply(get_size_range)
    df = df[df['size_range'] != 'Unknown'].copy()
    
    # Aggregate
    df_agg = df.groupby(['kategori', 'size_range']).agg({
        'jumlah_terjual': 'sum',
        'total_harga': 'sum'
    }).reset_index()
    
    # Separate Standard and Non-Standard
    df_agg['type'] = df_agg['kategori'].apply(
        lambda x: 'Standard' if x.lower() in ['standard', 'standar'] else 'Non-Standard'
    )
    
    print("="*80)
    print("📊 ANALISIS DATA PENJUALAN")
    print("="*80)
    
    # Overview
    print(f"\n1. TOTAL DATA SETELAH AGREGASI:")
    print(f"   Total records: {len(df_agg)}")
    print(f"   Standard: {len(df_agg[df_agg['type'] == 'Standard'])}")
    print(f"   Non-Standard: {len(df_agg[df_agg['type'] == 'Non-Standard'])}")
    
    # Statistics for Standard
    std_data = df_agg[df_agg['type'] == 'Standard']
    nonstd_data = df_agg[df_agg['type'] == 'Non-Standard']
    
    print(f"\n2. STATISTIK STANDARD:")
    print(f"   Jumlah Terjual:")
    print(f"     - Min: {std_data['jumlah_terjual'].min()}")
    print(f"     - Max: {std_data['jumlah_terjual'].max()}")
    print(f"     - Mean: {std_data['jumlah_terjual'].mean():.2f}")
    print(f"     - Median: {std_data['jumlah_terjual'].median():.2f}")
    print(f"   Total Harga:")
    print(f"     - Min: Rp {std_data['total_harga'].min():,.0f}")
    print(f"     - Max: Rp {std_data['total_harga'].max():,.0f}")
    print(f"     - Mean: Rp {std_data['total_harga'].mean():,.0f}")
    print(f"     - Median: Rp {std_data['total_harga'].median():,.0f}")
    
    print(f"\n3. STATISTIK NON-STANDARD:")
    print(f"   Jumlah Terjual:")
    print(f"     - Min: {nonstd_data['jumlah_terjual'].min()}")
    print(f"     - Max: {nonstd_data['jumlah_terjual'].max()}")
    print(f"     - Mean: {nonstd_data['jumlah_terjual'].mean():.2f}")
    print(f"     - Median: {nonstd_data['jumlah_terjual'].median():.2f}")
    print(f"   Total Harga:")
    print(f"     - Min: Rp {nonstd_data['total_harga'].min():,.0f}")
    print(f"     - Max: Rp {nonstd_data['total_harga'].max():,.0f}")
    print(f"     - Mean: Rp {nonstd_data['total_harga'].mean():,.0f}")
    print(f"     - Median: Rp {nonstd_data['total_harga'].median():,.0f}")
    
    # Price per unit comparison
    std_data['harga_per_unit'] = std_data['total_harga'] / std_data['jumlah_terjual']
    nonstd_data['harga_per_unit'] = nonstd_data['total_harga'] / nonstd_data['jumlah_terjual']
    
    print(f"\n4. HARGA PER UNIT (RATA-RATA):")
    print(f"   Standard: Rp {std_data['harga_per_unit'].mean():,.0f}")
    print(f"   Non-Standard: Rp {nonstd_data['harga_per_unit'].mean():,.0f}")
    print(f"   Rasio: {std_data['harga_per_unit'].mean() / nonstd_data['harga_per_unit'].mean():.2f}x")
    
    # Distribution analysis
    print(f"\n5. DISTRIBUSI RANGE NILAI:")
    print(f"\n   Standard - Jumlah Terjual:")
    print(f"     < 10: {len(std_data[std_data['jumlah_terjual'] < 10])}")
    print(f"     10-50: {len(std_data[(std_data['jumlah_terjual'] >= 10) & (std_data['jumlah_terjual'] < 50)])}")
    print(f"     50-100: {len(std_data[(std_data['jumlah_terjual'] >= 50) & (std_data['jumlah_terjual'] < 100)])}")
    print(f"     >= 100: {len(std_data[std_data['jumlah_terjual'] >= 100])}")
    
    print(f"\n   Non-Standard - Jumlah Terjual:")
    print(f"     < 10: {len(nonstd_data[nonstd_data['jumlah_terjual'] < 10])}")
    print(f"     10-50: {len(nonstd_data[(nonstd_data['jumlah_terjual'] >= 10) & (nonstd_data['jumlah_terjual'] < 50)])}")
    print(f"     50-100: {len(nonstd_data[(nonstd_data['jumlah_terjual'] >= 50) & (nonstd_data['jumlah_terjual'] < 100)])}")
    print(f"     >= 100: {len(nonstd_data[nonstd_data['jumlah_terjual'] >= 100])}")
    
    # Top and bottom products
    print(f"\n6. TOP 5 PRODUK (BERDASARKAN JUMLAH TERJUAL):")
    top_5 = df_agg.nlargest(5, 'jumlah_terjual')
    for idx, row in top_5.iterrows():
        print(f"   {row['kategori']} {row['size_range']}: {row['jumlah_terjual']} unit, Rp {row['total_harga']:,.0f}")
    
    print(f"\n7. BOTTOM 5 PRODUK (BERDASARKAN JUMLAH TERJUAL):")
    bottom_5 = df_agg.nsmallest(5, 'jumlah_terjual')
    for idx, row in bottom_5.iterrows():
        print(f"   {row['kategori']} {row['size_range']}: {row['jumlah_terjual']} unit, Rp {row['total_harga']:,.0f}")
    
    # Normalization impact
    print(f"\n8. DAMPAK NORMALISASI (Z-SCORE):")
    
    # Combined normalization (current approach)
    X_combined = df_agg[['jumlah_terjual', 'total_harga']].values
    X_mean_combined = X_combined.mean(axis=0)
    X_std_combined = X_combined.std(axis=0)
    print(f"\n   GABUNG (Standard + Non-Standard):")
    print(f"     Mean jumlah_terjual: {X_mean_combined[0]:.2f}")
    print(f"     Std jumlah_terjual: {X_std_combined[0]:.2f}")
    print(f"     Mean total_harga: Rp {X_mean_combined[1]:,.0f}")
    print(f"     Std total_harga: Rp {X_std_combined[1]:,.0f}")
    
    # Separate normalization
    X_std = std_data[['jumlah_terjual', 'total_harga']].values
    X_mean_std = X_std.mean(axis=0)
    X_std_std = X_std.std(axis=0)
    print(f"\n   STANDARD SAJA:")
    print(f"     Mean jumlah_terjual: {X_mean_std[0]:.2f}")
    print(f"     Std jumlah_terjual: {X_std_std[0]:.2f}")
    print(f"     Mean total_harga: Rp {X_mean_std[1]:,.0f}")
    print(f"     Std total_harga: Rp {X_std_std[1]:,.0f}")
    
    X_nonstd = nonstd_data[['jumlah_terjual', 'total_harga']].values
    X_mean_nonstd = X_nonstd.mean(axis=0)
    X_std_nonstd = X_nonstd.std(axis=0)
    print(f"\n   NON-STANDARD SAJA:")
    print(f"     Mean jumlah_terjual: {X_mean_nonstd[0]:.2f}")
    print(f"     Std jumlah_terjual: {X_std_nonstd[0]:.2f}")
    print(f"     Mean total_harga: Rp {X_mean_nonstd[1]:,.0f}")
    print(f"     Std total_harga: Rp {X_std_nonstd[1]:,.0f}")
    
    print("\n" + "="*80)
