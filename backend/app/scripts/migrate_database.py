# backend/app/scripts/migrate_database.py
from app.db.session import SessionLocal, engine
from app.db.models import Base
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP
from sqlalchemy import text

def migrate_database():
    """Ajoute les nouvelles colonnes à la base existante"""
    db = SessionLocal()
    
    try:
        # Pour MonitoredFile
        try:
            db.execute(text("ALTER TABLE monitored_files ADD COLUMN baseline_hash VARCHAR"))
            db.execute(text("ALTER TABLE monitored_files ADD COLUMN current_hash VARCHAR"))
            db.execute(text("ALTER TABLE monitored_files ADD COLUMN last_scan DATETIME"))
            print("✓ Colonnes ajoutées à monitored_files")
        except Exception as e:
            print(f"✓ Colonnes déjà présentes dans monitored_files: {e}")

        # Pour MonitoredFolder
        try:
            db.execute(text("ALTER TABLE monitored_folders ADD COLUMN folder_hash VARCHAR"))
            db.execute(text("ALTER TABLE monitored_folders ADD COLUMN file_count INTEGER DEFAULT 0"))
            db.execute(text("ALTER TABLE monitored_folders ADD COLUMN last_scan DATETIME"))
            print("✓ Colonnes ajoutées à monitored_folders")
        except Exception as e:
            print(f"✓ Colonnes déjà présentes dans monitored_folders: {e}")

        # Pour MonitoredIP
        try:
            db.execute(text("ALTER TABLE monitored_ips ADD COLUMN last_status JSON"))
            db.execute(text("ALTER TABLE monitored_ips ADD COLUMN last_scan DATETIME"))
            print("✓ Colonnes ajoutées à monitored_ips")
        except Exception as e:
            print(f"✓ Colonnes déjà présentes dans monitored_ips: {e}")

        db.commit()
        print("✓ Migration de la base de données terminée avec succès")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Erreur lors de la migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database()