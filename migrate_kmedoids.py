#!/usr/bin/env python
from app import create_app, db

app = create_app()
app.app_context().push()

print("Checking/Adding missing columns to kmedoids_result table...")

try:
    # Add medoids column if missing
    db.session.execute(db.text("""
        ALTER TABLE kmedoids_result ADD COLUMN medoids JSON AFTER random_state;
    """))
    print("✓ Added medoids column")
except Exception as e:
    if "Duplicate column" in str(e):
        print("✓ medoids column already exists")
    else:
        print(f"✗ Error adding medoids column: {e}")

db.session.commit()
print("Migration completed!")
