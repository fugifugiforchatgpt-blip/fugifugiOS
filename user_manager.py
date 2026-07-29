import json
import hashlib
import os
import shutil

USERS_FILE = "users.json"
USERS_DIR = "users"
DEFAULT_USER = "SystemX"
DEFAULT_PASSWORD = ""

def init_users():
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)
    if not os.path.exists(os.path.join(USERS_DIR, "shared")):
        os.makedirs(os.path.join(USERS_DIR, "shared"))
    if not os.path.exists(USERS_FILE):
        user_data = {
            DEFAULT_USER: {
                "password_hash": hashlib.sha256(DEFAULT_PASSWORD.encode()).hexdigest(),
                "home": os.path.join(USERS_DIR, DEFAULT_USER).replace("\\", "/")
            }
        }
        with open(USERS_FILE, "w") as f:
            json.dump(user_data, f, indent=4)
        user_home = os.path.join(USERS_DIR, DEFAULT_USER)
        if not os.path.exists(user_home):
            os.makedirs(user_home)
        files_dir = os.path.join(user_home, "files")
        if not os.path.exists(files_dir):
            os.makedirs(files_dir)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return False
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return users[username]["password_hash"] == hashed

def create_user(username, password):
    users = load_users()
    if username in users:
        return False
    user_home = os.path.join(USERS_DIR, username)
    os.makedirs(user_home)
    os.makedirs(os.path.join(user_home, "files"))
    with open(os.path.join(user_home, "session.json"), "w") as f:
        json.dump([], f)
    with open(os.path.join(user_home, "settings.json"), "w") as f:
        json.dump({"bg_color": "lightblue", "theme": "light"}, f)
    users[username] = {
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "home": user_home.replace("\\", "/")
    }
    save_users(users)
    return True

def delete_user(username):
    if username == DEFAULT_USER:
        return False
    users = load_users()
    if username not in users:
        return False
    shutil.rmtree(users[username]["home"])
    del users[username]
    save_users(users)
    return True

def change_password(username, new_password):
    users = load_users()
    if username not in users:
        return False
    users[username]["password_hash"] = hashlib.sha256(new_password.encode()).hexdigest()
    save_users(users)
    return True

def get_user_list():
    return list(load_users().keys())