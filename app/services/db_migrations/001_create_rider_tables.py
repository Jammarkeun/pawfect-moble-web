from app.services.database import Database

def create_rider_applications_table():
    db = Database()
    query = """
    CREATE TABLE IF NOT EXISTS rider_applications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        vehicle_type VARCHAR(255),
        vehicle_plate_number VARCHAR(255),
        vehicle_model VARCHAR(255),
        government_id VARCHAR(255),
        vehicle_registration VARCHAR(255),
        profile_photo VARCHAR(255),
        clearance VARCHAR(255),
        status VARCHAR(255) DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        admin_notes TEXT,
        reviewed_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    db.execute_query(query)
    print("Table 'rider_applications' created successfully (if it didn't exist).")

def create_rider_training_table():
    db = Database()
    query = """
    CREATE TABLE IF NOT EXISTS rider_training (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(255) DEFAULT 'completed',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (user_id)
    );
    """
    db.execute_query(query)
    print("Table 'rider_training' created successfully (if it didn't exist).")

def create_rider_availability_table():
    db = Database()
    query = """
    CREATE TABLE IF NOT EXISTS rider_availability (
        id INT AUTO_INCREMENT PRIMARY KEY,
        rider_id INT NOT NULL,
        is_online BOOLEAN DEFAULT FALSE,
        is_available BOOLEAN DEFAULT FALSE,
        last_online DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (rider_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (rider_id)
    );
    """
    db.execute_query(query)
    print("Table 'rider_availability' created successfully (if it didn't exist).")

if __name__ == "__main__":
    create_rider_applications_table()
    create_rider_training_table()
    create_rider_availability_table()
    print("All rider related tables checked/created.")