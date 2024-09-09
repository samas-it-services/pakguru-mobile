from firebase_database import FirebaseDatabase

def authenticate_user():
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    db = FirebaseDatabase()
    if db.authenticate_user(email, password):
        print("User authenticated successfully!")
    else:
        print("Authentication failed.")
