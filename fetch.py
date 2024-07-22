import mysql.connector
from mysql.connector import Error
import re
import winreg as reg

def create_connection():
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'MYSQL_PASSWORD',
            database = 'installed_software'
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def save_to_mysql(data, connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS software (Name VARCHAR(255), Vendor VARCHAR(255), InstallDate VARCHAR(255), Version VARCHAR(255))")
    cursor.execute("DELETE FROM software")
    for software in data:
        cursor.execute("INSERT INTO software (Name, Vendor, InstallDate, Version) VALUES (%s, %s, %s, %s)",
                       (software['Name'], software['Vendor'], software['InstallDate'], software['Version']))
    connection.commit()
    cursor.close()

def format_date(date_str):
    return f"{date_str[6:8]}-{date_str[4:6]}-{date_str[:4]}" if len(date_str) == 8 else "Unknown"

def clean_name(name):
    name = re.sub(r'\s+\d+(\.\d+)*', '', name)
    name = re.sub(r' - x\d{2,3}', '', name)
    name = re.sub(r'\s+\([^)]*\)', '', name)
    name = re.sub(r'\s*-\s*$', '', name)
    return name.strip()

def fetch_registry_software(hive, path, flags):
    software_list = []
    with reg.ConnectRegistry(None, hive) as root:
        with reg.OpenKey(root, path, 0, reg.KEY_READ | flags) as key:
            i = 0
            while True:
                try:
                    subkey_name = reg.EnumKey(key, i)
                    with reg.OpenKey(key, subkey_name) as subkey:
                        try:
                            name = reg.QueryValueEx(subkey, "DisplayName")[0]
                            vendor = reg.QueryValueEx(subkey, "Publisher")[0]
                            install_date = reg.QueryValueEx(subkey, "InstallDate")[0]
                            version = reg.QueryValueEx(subkey, "DisplayVersion")[0]
                            software_list.append({
                                'Name': clean_name(name),
                                'Vendor': vendor,
                                'InstallDate': format_date(install_date),
                                'Version': version
                            })
                        except FileNotFoundError:
                            pass
                except OSError:
                    break
                i += 1
    return software_list

def main():
    connection = create_connection()
    if connection:
        software_list = []
        paths_flags = [
            (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", reg.KEY_WOW64_64KEY),
            (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", reg.KEY_WOW64_32KEY),
            (reg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", reg.KEY_READ),
            (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\Installer\Products", reg.KEY_WOW64_64KEY),
            (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\Installer\Products", reg.KEY_WOW64_32KEY)
        ]

        for hive, path, flags in paths_flags:
            software_list.extend(fetch_registry_software(hive, path, flags))

        save_to_mysql(software_list, connection)
        print("Software details saved to MySQL database.")
        connection.close()
    else:
        print("Failed to connect to the database.")

if __name__ == '__main__':
    main()