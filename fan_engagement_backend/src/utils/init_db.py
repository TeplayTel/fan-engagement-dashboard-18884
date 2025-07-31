from ..models.database import SessionLocal, engine, Base
from ..models.emoji import Emoji

# PUBLIC_INTERFACE
def create_tables():
    """
    Create all database tables.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("Tables will be created when database becomes available")

# PUBLIC_INTERFACE
def init_default_emojis():
    """
    Initialize database with default emoji set.
    Creates common emoji reactions if they don't already exist.
    """
    try:
        db = SessionLocal()
        try:
            # Default emojis for fan engagement
            default_emojis = [
                {"name": "heart", "unicode_char": "❤️", "category": "love"},
                {"name": "fire", "unicode_char": "🔥", "category": "excitement"},
                {"name": "laughing", "unicode_char": "😂", "category": "emotion"},
                {"name": "surprised", "unicode_char": "😮", "category": "emotion"},
                {"name": "crying", "unicode_char": "😢", "category": "emotion"},
                {"name": "thumbs_up", "unicode_char": "👍", "category": "approval"},
                {"name": "thumbs_down", "unicode_char": "👎", "category": "approval"},
                {"name": "clapping", "unicode_char": "👏", "category": "celebration"},
                {"name": "goal", "unicode_char": "⚽", "category": "sports"},
                {"name": "trophy", "unicode_char": "🏆", "category": "sports"},
                {"name": "star", "unicode_char": "⭐", "category": "quality"},
                {"name": "lightning", "unicode_char": "⚡", "category": "excitement"}
            ]
            
            for emoji_data in default_emojis:
                # Check if emoji already exists
                existing = db.query(Emoji).filter(Emoji.name == emoji_data["name"]).first()
                if not existing:
                    emoji = Emoji(**emoji_data)
                    db.add(emoji)
            
            db.commit()
            print(f"Initialized {len(default_emojis)} default emojis")
            
        except Exception as e:
            print(f"Error initializing emojis: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"Warning: Could not connect to database for emoji initialization: {e}")
        print("Emojis will be initialized when database becomes available")

# PUBLIC_INTERFACE  
def init_database():
    """
    Initialize the complete database with tables and default data.
    """
    print("Creating database tables...")
    create_tables()
    
    print("Initializing default emojis...")
    init_default_emojis()
    
    print("Database initialization complete!")

if __name__ == "__main__":
    init_database()
