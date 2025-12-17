"""
Test apakah dashboard route menghasilkan data yang benar
"""
from app import create_app

app = create_app()

with app.test_client() as client:
    # Make request to dashboard
    response = client.get('/')
    
    if response.status_code == 200:
        html = response.data.decode('utf-8')
        
        # Check if clustering section exists
        if 'Hasil Analisis Clustering' in html:
            print("✓ Clustering section found in HTML")
            
            # Count data-tier attributes
            terlaris_count = html.count('data-tier="Terlaris"')
            sedang_count = html.count('data-tier="Sedang"')
            kurang_count = html.count('data-tier="Kurang Laris"')
            
            print(f"\ndata-tier attributes in HTML:")
            print(f"  Terlaris: {terlaris_count}")
            print(f"  Sedang: {sedang_count}")
            print(f"  Kurang Laris: {kurang_count}")
            print(f"  Total: {terlaris_count + sedang_count + kurang_count}")
            
            # Check if filter dropdown exists
            if 'id="tierFilter"' in html:
                print("\n✓ Filter dropdown found")
            else:
                print("\n✗ Filter dropdown NOT found")
            
            # Check if apply button exists
            if 'id="applyFilterBtn"' in html:
                print("✓ Apply button found")
            else:
                print("✗ Apply button NOT found")
            
            # Sample some data-tier lines
            print("\nSample data-tier attributes from HTML:")
            lines = html.split('\n')
            count = 0
            for line in lines:
                if 'data-tier=' in line:
                    print(f"  {line.strip()[:120]}")
                    count += 1
                    if count >= 5:
                        break
        else:
            print("✗ Clustering section NOT found in HTML")
            print("User likely sees: 'Belum Ada Hasil Clustering'")
    else:
        print(f"✗ Request failed with status code: {response.status_code}")
