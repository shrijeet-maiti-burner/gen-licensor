import pandas as pd
import smtplib
from email.message import EmailMessage
import subprocess
import winreg

def send_email(recipient, subject, body, sender_email, sender_password):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient

    with smtplib.SMTP('smtp.office365.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
    print(f"Email sent to {recipient}.")

def fetch_uninstaller_path(software_name):
    try:
        uninstall_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_key, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    try:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        if software_name.lower() in name.lower():
                            command = winreg.QueryValueEx(subkey, "UninstallString")[0]
                            return command
                    except WindowsError:
                        continue
    except Exception as e:
        print(f"Error fetching uninstaller path: {e}")
    return None

def uninstall_software(uninstall_command):
    try:
        result = subprocess.run(uninstall_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            print(f"Uninstallation failed: {result.stderr}")
    except Exception as e:
        print(f"Error during uninstallation: {e}")
    return False

def manage_software(csv_path, sender_email, sender_password):
    df = pd.read_csv(csv_path)
    df['Reminders Sent'] = df.get('Reminders Sent', pd.Series([0]*len(df.index)))
    df['Is Uninstalled'] = df.get('Is Uninstalled', pd.Series(['No']*len(df.index)))

    recipient_email = "SYSTEM_USER_EMAIL"

    for index, row in df.iterrows():
        if row['Is Safe'].lower() == 'no' and row['Is Uninstalled'].lower() == 'no':
            if row['Reminders Sent'] < 3:
                subject = f"Reminder {row['Reminders Sent'] + 1}: Please Uninstall {row['Name']}"
                body = (f"Dear User,\n\n"
                        f"You are receiving this email because the software '{row['Name']}' installed on your system "
                        f"has been marked as unsafe. Please uninstall it immediately. This is reminder {row['Reminders Sent'] + 1}.\n\n"
                        "Regards,\n"
                        "John Kopperfield")
                send_email(recipient_email, subject, body, sender_email, sender_password)
                df.at[index, 'Reminders Sent'] += 1
            if row['Reminders Sent'] == 3:
                uninstall_command = fetch_uninstaller_path(row['Name'])
                if uninstall_command and uninstall_software(uninstall_command):
                    df.at[index, 'Is Uninstalled'] = 'Yes'
                    subject = "Final Notice: Software Uninstalled Automatically"
                    body = (f"Dear User,\n\n"
                            f"The software '{row['Name']}' has been automatically uninstalled from your system "
                            "as you did not comply with our previous uninstallation requests. Please contact support "
                            "if you believe this is an error.\n\n"
                            "Regards,\n"
                            "John Kopperfield")
                    send_email(recipient_email, subject, body, sender_email, sender_password)
    df.to_csv(csv_path, index=False)
    print("CSV updated with the latest software management details.")

def main():
    csv_path = 'to_be_uninstalled.csv'
    sender_email = 'johnkopperfieldsaysuninstall@outlook.com'
    sender_password = 'JohnK0pperfieldsendshisregards'
    manage_software(csv_path, sender_email, sender_password)

if __name__ == '__main__':
    main()