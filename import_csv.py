"""
Helper script to import CSV data into database
"""
import pandas as pd
import sys
sys.path.insert(0, r'c:\Users\LENOVO\Documents\Project_Ta_Skripsi')

from app import create_app
from app.models import db, Penjualan

app = create_app()

def import_csv(csv_path):
    """Import CSV file into database"""
    with app.app_context():
        try:
            print(f"Reading CSV: {csv_path}")
            df = pd.read_csv(csv_path)
            print(f"Total rows: {len(df)}")
            
            # Clear existing data
            Penjualan.query.delete()
            db.session.commit()
            print("✓ Cleared existing data")
            
            # Insert data
            success_count = 0
            for idx, row in df.iterrows():
                try:
                    # Parse harga (remove dots)
                    harga_satuan = str(row['Harga_Satuan']).replace('.', '') if row['Harga_Satuan'] else '0'
                    total_harga = str(row['Total_Harga']).replace('.', '') if row['Total_Harga'] else '0'
                    
                    penjualan = Penjualan(
                        kategori=row['Kategori'],
                        size=row['Size'],
                        jumlah_terjual=int(row['Jumlah_Terjual']) if row['Jumlah_Terjual'] else 0,
                        harga_satuan=float(harga_satuan),
                        total_harga=float(total_harga),
                        nama_penjual=row['Nama_Penjual'],
                        kota_tujuan=row['Kota_Tujuan']
                    )
                    db.session.add(penjualan)
                    success_count += 1
                    
                    if idx % 100 == 0:
                        print(f"  Processed {idx} rows...")
                        
                except Exception as e:
                    print(f"  ⚠ Error row {idx}: {str(e)}")
                    continue
            
            db.session.commit()
            print(f"✅ Imported {success_count} records successfully!")
            
            # Show stats
            total = Penjualan.query.count()
            standard = Penjualan.query.filter(Penjualan.kategori.contains('Standard')).count()
            non_standard = total - standard
            print(f"\nStatistics:")
            print(f"  Total: {total}")
            print(f"  Standard: {standard}")
            print(f"  Non-Standard: {non_standard}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    csv_file = r'c:\Users\LENOVO\Documents\Project_Ta_Skripsi\upload\hasil_data_Penjualan_CvPutraRizkyAroindo_2023-2025.csv'
    import_csv(csv_file)
