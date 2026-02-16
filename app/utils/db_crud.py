from datetime import datetime
import sqlite3
from PySide6.QtCore import QStandardPaths
from pathlib import Path
import traceback
import uuid
import keyring # type: ignore
import secrets
from sqlcipher3 import dbapi2 as sqlite

source_dir = "database crud"

# --- APP INFO ---
APP_NAME = "Shield Eye (log analyzer) Desktop"
APP_VERSION = "1.0.0"

# --- DATABASE ---
DB_NAME = "shield_eye_database.db"
REQUIRED_SQLITE_VERSION = (3, 50, 2)

    # development mode
# current_dir = Path(__file__).resolve().parent 
# STORAGE = current_dir.parent / "storage" / DB_NAME

    # production mode
data_dir = Path(
    QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
)
data_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
STORAGE = data_dir / DB_NAME

# --- PRAGMA KEY ---
APPNAME = "ShieldEyeDesktop"
db_key = keyring.get_password(APPNAME, "db_encryption_key")
if not db_key:
    db_key = secrets.token_hex(32)
    keyring.set_password(APPNAME, "db_encryption_key", db_key)

def init_db():
        try:
            """Creates the schema if it doesn't exist."""
            
            global STORAGE
            conn = sqlite.connect(STORAGE)
            conn.execute(f"PRAGMA key = '{db_key}';")
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_logs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    level TEXT,
                    category TEXT,
                    event_type TEXT,
                    source TEXT,
                    message TEXT,
                    stack TEXT,
                    tags TEXT,
                    app_name TEXT,
                    app_version TEXT,
                    user_id TEXT,
                    user_ip TEXT,
                    user_method TEXT,
                    user_endpoint TEXT,
                    user_status TEXT,
                    user_agent TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_logs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    level TEXT,
                    category TEXT,
                    event_type TEXT,
                    message TEXT,
                    log_id TEXT,
                    status TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preference_settings (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    warn TEXT,
                    error TEXT,
                    critical TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    level TEXT,
                    event_type TEXT,
                    source TEXT,
                    message TEXT,
                    stack TEXT,
                    tags TEXT,
                    app_name TEXT,
                    app_version TEXT
                );
            """)

            conn.commit()
            return
        except sqlite3.Error as e:
            return "An error occured while initialing database!"

def execute_query(query, params=(), fetchone=False, fetchall=False, bulkyinsert=False, dict_data = False):
    try:
        global STORAGE
        conn = sqlite.connect(STORAGE)
        conn.execute(f"PRAGMA key = '{db_key}';")
        if dict_data:
            conn.row_factory = sqlite.Row
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA key = '{db_key}';")
        if bulkyinsert:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = True
        conn.close()
        return result
    except sqlite3.Error as e:
        log_activity("error", type(e).__name__, source_dir, f"Database error: {e}", traceback.format_exc(), "execute_query func")

def log_activity(level, event_type, source, message, stack, tags):
    global STORAGE
    id = str(uuid.uuid4())
    timestamp = datetime.now()
    app_name = APP_NAME
    app_version = APP_VERSION
    query = "INSERT INTO activity_logs (id, timestamp, level, event_type, source, message, stack, tags, app_name, app_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    params = (id, timestamp, level, event_type, source, message, stack, tags, app_name, app_version)
    execute_query(query, params)

# LOGS
def append_log(logs):
    query = "INSERT OR IGNORE INTO event_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    params = logs
    result = execute_query(query, params, False, False, True)
    if result:
        log_activity("info","event log creation", source_dir, "Successfully appended event logs", "", "append_log func")
        return True
    else:
        log_activity("error","event log creation", source_dir, "Failed to append event logs", "", "append_log func")

#! operation not available in this version
def delete_single_log(id):
    query = "DELETE FROM event_logs WHERE id = ?"
    params = (id,)
    result = execute_query(query, params)
    if result:
        log_activity("info","event log deletion", source_dir, f"Successfully deleted event log {id}", "", "delete_single_log func")
        return True
    else:
        log_activity("error","event log deletion", source_dir, f"Failed to delete event log {id}", "", "delete_single_log func")

#! operation not available in this version
def delete_range_logs(start_date, end_date):
    query = "DELETE FROM event_logs WHERE timestamp BETWEEN ? AND ?"
    params = (start_date, end_date)
    result = execute_query(query, params)
    if result:
        log_activity("info","event log deletion", source_dir, f"Successfully deleted event logs from {start_date} to {end_date}", "", "delete_range_logs func")
        return True
    else:
        log_activity("error","event log deletion", source_dir, f"Failed to delete event logs from {start_date} to {end_date}", "", "delete_range_logs func")

def fetch_log():
    query = "SELECT * FROM event_logs ORDER BY timestamp"
    result = execute_query(query, (), False, True, False, True)
    if result:
        return result
    
# PREFERENCE SETTINGS
def save_prefs_settings(id, timestamp, warn, error, critical):
    query = "INSERT OR IGNORE INTO preference_settings VALUES (?, ?, ?, ?, ?)"
    params = (id, timestamp, warn, error, critical)
    result = execute_query(query, params, False, False, False, False)
    if result:
        log_activity("info","preferences creation", source_dir, "Successfully updated account preference settings", "", "save_prefs_settings func")
        return True
    else:
        log_activity("error","preferences creation", source_dir, "Failed to updated account preference settings", "", "save_prefs_settings func")

def fetch_prefs_settings():
    query = "SELECT warn, error, critical FROM preference_settings"
    result = execute_query(query, (), True, False, False, True)
    if result:
        return result

def update_prefs_settings(warn, error, critical):
    query = "UPDATE preference_settings SET warn = ?, error = ?, critical = ?"
    params = (warn, error, critical)
    result = execute_query(query, params)
    if result:
        log_activity("info","alert status", source_dir, f"Successfully updated account preference settings", "", "update_prefs_settings func")
        return True
    else:
        log_activity("error","alert status", source_dir, f"Failed to updated account preference settings", "", "update_prefs_settings func")

# ALERT
def create_alert(alert):
    query = "INSERT OR IGNORE INTO alert_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    params = alert
    result = execute_query(query, params, False, False, True)
    if result:
        log_activity("info","alert creation", source_dir, "Successfully created alert", "", "create_alert func")
        return True
    else:
        log_activity("error","alert creation", source_dir, "Failed to create alert", "", "create_alert func")

def delete_alert(id):
    query = "DELETE FROM alert_logs WHERE id = ?"
    params = (id,)
    result = execute_query(query, params)
    if result:
        log_activity("info","alert deletion", source_dir, f"Successfully deleted alert {id}", "", "delete_alert func")
        return True
    else:
        log_activity("error","alert deletion", source_dir, f"Failed to delete alert {id}", "", "delete_alert func")
    

def delete_all_alerts():
    query = "DELETE FROM alert_logs"
    result = execute_query(query, ())
    if result:
        log_activity("info","alert deletion", source_dir, f"Successfully deleted all alerts", "", "delete_all_alerts func")
        return True
    else:
        log_activity("error","alert deletion", source_dir, f"Failed to delete all alerts", "", "delete_all_alerts func")

def mark_alert_as_read(id):
    status = "read"
    query = "UPDATE alert_logs SET status = ? WHERE id = ?"
    params = (status, id)
    result = execute_query(query, params)
    if result:
        log_activity("info","alert status", source_dir, f"Successfully marked alert {id} as read", "", "mark_alert_as_read func")
        return True
    else:
        log_activity("error","alert status", source_dir, f"Failed to mark alert {id} as read", "", "mark_alert_as_read func")

def mark_all_alert():
    status = "read"
    condition = "unread"
    query = "UPDATE alert_logs SET status = ? WHERE status = ?"
    params = (status, condition)
    result = execute_query(query, params)
    if result:
        log_activity("info","alert status", source_dir, f"Successfully marked all alerts as read", "", "mark_all_alert func")
        return True
    else:
        log_activity("error","alert status", source_dir, f"Failed to mark all alerts as read", "", "mark_all_alert func")

def fetch_alert_log():
    query = "SELECT * FROM alert_logs ORDER BY timestamp"
    result = execute_query(query, (), False, True, False, True)
    if result:
        return result
    
# GENERAL
def select_date_interval():
    query = "SELECT datetime(MIN(timestamp)), datetime(MAX(timestamp)) FROM event_logs"
    result = execute_query(query, (), True)
    if result:
        first, last = result
        return result

def verify_sql_version():
    sql_version = sqlite3.sqlite_version_info
    if sql_version < REQUIRED_SQLITE_VERSION:
        # print(f"CRITICAL: SQLite version {sql_version} is outdated. Risk of CVE-2025-6965.")
        return f"CRITICAL: SQLite version {sql_version} is outdated. Risk of CVE-2025-6965."
    return True
