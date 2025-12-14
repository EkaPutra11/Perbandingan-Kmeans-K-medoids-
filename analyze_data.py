"""
Analisis kenapa hasil clustering tidak masuk akal
"""
from app import create_app
from app.models import Penjualan
import pandas as pd
import numpy as np

app = create_app()
with app.app_context():
    data = Penjualan.query.all()
    df = pd.DataFrame([{
        'kategori': d.kategori,
        'size': d.size,
        'jumlah_terjual': d.jumlah_terjual,
        'total_harga': float(d.total_harga)
    } for d in data])
    
    print("="*70)
    print("ANALISIS DATA PENJUALAN")
    print("="*70)
    
    print(f"\nTotal records: {len(df)}")
    
    # Statistik jumlah terjual
    print(f"\n📊 JUMLAH TERJUAL:")
    print(f"   Min: {df['jumlah_terjual'].min()}")
    print(f"   Max: {df['jumlah_terjual'].max()}")
    print(f"   Mean: {df['jumlah_terjual'].mean():.2f}")
    print(f"   Median: {df['jumlah_terjual'].median():.2f}")
    print(f"   Std: {df['jumlah_terjual'].std():.2f}")
    
    # Percentile
    print(f"\n📈 PERCENTILE JUMLAH TERJUAL:")
    for p in [25, 50, 75, 90, 95]:
        val = np.percentile(df['jumlah_terjual'], p)
        print(f"   P{p}: {val:.0f}")
    
    # Distribusi kategori
    print(f"\n📦 KATEGORI:")
    print(df['kategori'].value_counts())
    
    # Top 10 produk terlaris
    print(f"\n🏆 TOP 10 TERLARIS:")
    top10 = df.nlargest(10, 'jumlah_terjual')[['kategori', 'size', 'jumlah_terjual', 'total_harga']]
    for idx, row in top10.iterrows():
        print(f"   {row['kategori']:20s} {row['size']:10s} - {row['jumlah_terjual']:3d} terjual - Rp {row['total_harga']:,.0f}")
    
    # Bottom 10 produk
    print(f"\n📉 BOTTOM 10:")
    bottom10 = df.nsmallest(10, 'jumlah_terjual')[['kategori', 'size', 'jumlah_terjual', 'total_harga']]
    for idx, row in bottom10.iterrows():
        print(f"   {row['kategori']:20s} {row['size']:10s} - {row['jumlah_terjual']:3d} terjual - Rp {row['total_harga']:,.0f}")
    
    # Distribusi penjualan
    print(f"\n📊 DISTRIBUSI BERDASARKAN JUMLAH TERJUAL:")
    bins = [0, 5, 10, 20, 50, 100, 1000]
    labels = ['0-5', '6-10', '11-20', '21-50', '51-100', '100+']
    df['range'] = pd.cut(df['jumlah_terjual'], bins=bins, labels=labels, include_lowest=True)
    print(df['range'].value_counts().sort_index())
    
    print("\n" + "="*70)
