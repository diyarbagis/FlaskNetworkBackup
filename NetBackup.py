# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Author: Diyar Bagis
# Email: diyarbagis@gmail.com
# Twitter: bagisdiyar
# GitHub: https://github.com/diyarbagis
# Description: A free open-source Flask app for backup on switches,routers and firewalls. 
# Version: 1.0
# Copyleft: Zed Teknoloji


import smtplib
import os
import sqlite3
import datetime
from netmiko import ConnectHandler
from flask import Flask, request, render_template
from flask import Flask, redirect, render_template, url_for
from flask import make_response
from flask import send_file, request
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

app = Flask(__name__)


# route for the index page
@app.route('/')
def index():
  if not os.path.isfile('devices.db'):
    return redirect(url_for('add_device'))
   
    # redirect to the device list page
  else:
    return redirect(url_for('devices'))
     
@app.route("/add_device", methods=["GET", "POST"])
def add_device():
    if request.method == "POST":
        ip_address = request.form["ip_address"]
        username = request.form["username"]
        password = request.form["password"]
        enable_password = request.form.get("enable_password")
        device_type = request.form["device_type"]

        try:
            device = {
                "device_type": device_type,
                "ip": ip_address,
                "username": username,
                "password": password,
                "secret": enable_password,
            }

            connection = ConnectHandler(**device)
            if device_type == "cisco_ios":
                connection.enable()
                config = connection.send_command("show run")
            elif device_type == "aruba_os":
                 connection.enable()
                 config = connection.send_command("show config")
            elif device_type == "fortinet":
                config = connection.send_command("show full-configuration")
            elif device_type == "dell_force10":
                connection.enable()
                config = connection.send_command("show running-config")
            elif device_type == "brocade_icx":
                connection.enable()
                config = connection.send_command("show config")
            elif device_type == "ruijie":
                connection.enable()
                config = connection.send_command("display current-configuration")
            elif device_type == "juniper":
                connection.enable()
                config = connection.send_command("show configuration")        
            elif device_type == "huawei":
                connection.enable()
                config = connection.send_command("display current-configuration")  
            elif device_type == "paloalto_panos":
                connection.enable()
                config = connection.send_command("show running-config")                 
                
            # Store the configuration data in an SQLite database
            conn = sqlite3.connect("config_backup.db")
            c = conn.cursor()
            c.execute(
                "CREATE TABLE IF NOT EXISTS backups (id INTEGER PRIMARY KEY AUTOINCREMENT, device_type TEXT, ip_address TEXT, username TEXT, password TEXT, enable_password TEXT, config TEXT, date_added TEXT, hostname TEXT)"
            )

            device_hostname = get_device_hostname(connection, device_type)      
            now = datetime.datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")

            c.execute(
                "INSERT INTO backups (device_type, ip_address, config, date_added, hostname) VALUES (?,?,?,?,?)",
                (
                    device_type,
                    ip_address,
                    config,
                    date_time,
                    device_hostname,
                ),
            )
            conn.commit()
            
            
            # Store the devices data in an SQLite database
            conn = sqlite3.connect("devices.db")
            c = conn.cursor()
            c.execute(
                "CREATE TABLE IF NOT EXISTS devices (id INTEGER PRIMARY KEY AUTOINCREMENT, device_type TEXT, ip_address TEXT, username TEXT, password TEXT, enable_password TEXT, date_added TEXT, hostname TEXT)"
            )
            
            device_hostname = get_device_hostname(connection, device_type)
            
            # Check if the entry already exists in the database
            c.execute("SELECT COUNT(*) FROM devices WHERE device_type=? AND ip_address=? AND username=? AND password=? AND enable_password=? AND hostname=?", 
            (device_type, ip_address, username, password, enable_password, device_hostname))
            result = c.fetchone()[0]
           
            now = datetime.datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")           
           
            if result == 0:
                c.execute(
                    "INSERT INTO devices (device_type, ip_address, username, password, enable_password, hostname, date_added) VALUES (?,?,?,?,?,?,?)",
                  (
                    device_type,
                    ip_address,
                    username,
                    password,
                    enable_password,
                    device_hostname,
                    date_time,
                  ),
                )
                conn.commit()
            else:  
              print("Device data already exists in the database")

            return render_template("getbackup.html")

        except Exception as e:
            return str(e)

    return render_template("add_device.html")

@app.route("/devices")
def devices():
  if not os.path.isfile('devices.db'):
    return render_template("nodevice.html")
  else:
    device_id = request.args.get('id')
    conn = sqlite3.connect("devices.db")
    c = conn.cursor()

    search_query = request.args.get("search_query")

    if search_query:
        c.execute("SELECT * FROM devices WHERE device_type LIKE ? OR ip_address LIKE ? OR hostname LIKE ? ",
                  ('%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%', ))
        devices = c.fetchall()
    else:
        c.execute("SELECT * FROM devices")
        devices = c.fetchall()

    return render_template("devices.html", devices=devices)   
    
@app.route("/backups")
def backups():
  if not os.path.isfile('config_backup.db'):
    return render_template("nobackup.html")
  else:
    conn = sqlite3.connect("config_backup.db")
    c = conn.cursor()

    search_query = request.args.get("search_query")

    if search_query:
        c.execute("SELECT * FROM backups WHERE device_type LIKE ? OR ip_address LIKE ? OR hostname LIKE ? OR config LIKE ? OR date_added LIKE ?",
                  ('%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%', ))
        backups = c.fetchall()
    else:
        c.execute("SELECT * FROM backups")
        backups = c.fetchall()

    return render_template("backups.html", backups=backups)
        
@app.route('/backups/<int:id>', methods=['GET'])
def show_backup(id):
    conn = sqlite3.connect('config_backup.db')
    c = conn.cursor()
    c.execute("SELECT config FROM backups WHERE id=?", (id,))
    config = c.fetchone()[0]
    conn.close()
    return render_template('show_backup.html', id=id, config=config)

@app.route('/backups/delete/<int:id>', methods=['GET', 'POST'])
def delete_backup(id):
    if request.method == 'GET':
        return render_template('confirm_delete.html', id=id)
    elif request.method == 'POST':
        conn = sqlite3.connect('config_backup.db')
        c = conn.cursor()
        c.execute("DELETE FROM backups WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('backups'))
        
@app.route('/devices/<int:id>', methods=['GET' , 'POST'])
def get_backup(id):
    conn = sqlite3.connect('devices.db')
    c = conn.cursor()
    c.execute("SELECT ip_address, username, password, enable_password, device_type FROM devices WHERE id=?", (id,))
    result = c.fetchone()
    if result is None:
        return "Device not found"
    ip_address, username, password, enable_password, device_type = result
    device = {
        "device_type": device_type,
        "ip": ip_address,
        "username": username,
        "password": password,
        "secret": enable_password,
    }

    connection = ConnectHandler(**device)
    if device_type == "cisco_ios":
        connection.enable()
        config = connection.send_command("show run")
    elif device_type == "aruba_os":
        connection.enable()
        config = connection.send_command("show config")
    elif device_type == "fortinet":
        config = connection.send_command("execute full-config")
    elif device_type == "dell_force10":
        connection.enable()
        config = connection.send_command("show running-config")
    elif device_type == "brocade_icx":
        connection.enable()
        config = connection.send_command("show config")
    elif device_type == "ruijie":
        connection.enable()
        config = connection.send_command("display current-configuration")
    elif device_type == "juniper":
        connection.enable()
        config = connection.send_command("show configuration")        
    elif device_type == "huawei":
        connection.enable()
        config = connection.send_command("display current-configuration")  
    elif device_type == "paloalto_panos":
        connection.enable()
        config = connection.send_command("show running-config")         
    else:
        return "Device type not found"
        
    # Insert the backup configuration into the config_backup table
    conn = sqlite3.connect("config_backup.db")
    c = conn.cursor()
    c.execute(
              "CREATE TABLE IF NOT EXISTS backups (id INTEGER PRIMARY KEY AUTOINCREMENT, device_type TEXT, ip_address TEXT, username TEXT, password TEXT, enable_password TEXT, config TEXT, date_added TEXT, hostname TEXT)"
            )
            
    device_hostname = get_device_hostname(connection, device_type)
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")


    c.execute(
              "INSERT INTO backups (device_type, ip_address, config, date_added, hostname) VALUES (?,?,?,?,?)",
                (
                    device_type,
                    ip_address,
                    config,
                    date_time,
                    device_hostname,
                ),
            )
    conn.commit()          
    conn.close()
    return render_template('getbackup.html', get_backup=config)

@app.route('/devices/delete/<int:id>', methods=['GET', 'POST'])
def delete_device(id):
    if request.method == 'GET':
        return render_template('confirm_delete_device.html', id=id)
    elif request.method == 'POST':
        conn = sqlite3.connect('devices.db')
        c = conn.cursor()
        c.execute("DELETE FROM devices WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('devices'))

@app.route('/devices/backups/<string:ip_address>', methods=['GET'])
def devicebackups(ip_address):
        conn = sqlite3.connect('config_backup.db')
        c = conn.cursor()
        c.execute("SELECT * FROM backups WHERE ip_address=?", (ip_address,))
        backups = c.fetchall()
        conn.commit()
        conn.close()
        return render_template('devicebackups.html', backups=backups)

@app.route('/backups/download/<int:id>')
def download_backup(id):
    conn = sqlite3.connect('config_backup.db')
    cursor = conn.cursor()
    cursor.execute("SELECT config, device_type, hostname, date_added FROM backups WHERE id=?", (id,))
    getconfdev = cursor.fetchone()
    config = getconfdev[0]
    device_type = getconfdev[1]
    hostname = getconfdev[2]    
    date_added = getconfdev[3]
    conn.close()
    filename = f'{device_type}_{hostname}_{date_added}.cfg' 
    return send_file(BytesIO(config.encode('utf-8')),
                     mimetype='text/plain',
                     as_attachment=True,
                     attachment_filename=filename,
                     cache_timeout=0)
                              
def get_device_hostname(connection, device_type):
    if device_type == "fortinet":
        command = "get system global | grep -f hostname"
        index = 5
    elif device_type == "aruba_os":
        command = "show running-config | include hostname"
        index = 1
    elif device_type == "dell_force10":
        command = "show running-config | grep hostname"
        index = 1
    elif device_type == "cisco_ios":
        command = "show run | include hostname"
        index = 1
    elif device_type == "ruijie":
        command = "display run | include hostname"
        index = 1
    elif device_type == "juniper":
        command = "show configuration system host-name"
        index = 1        
    elif device_type == "huawei":
        command = "display current-configuration | include sysname"
        index = 1   
    elif device_type == "paloalto_panos":
        command = "show system info | match hostname"
        index = 1                      
    else:
        raise ValueError("Invalid device type")

    output = connection.send_command(command)
    device_hostname = output.split()[index]
    return device_hostname
   
@app.route('/email_config', methods=['GET', 'POST'])
def email_config():
    if request.method == 'POST': 
        username = request.form['username']
        password = request.form['password']
        smtp_server = request.form['smtp_server']
        smtp_port = request.form['smtp_port']
        sender_email = request.form['sender_email']
        rcv_email = request.form['rcv_email']        

        conn = sqlite3.connect('email_config.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS smtp
                          (username text, password text, smtp_server text, smtp_port integer, sender_email text, rcv_email text)''')
        cursor.execute('INSERT INTO smtp VALUES (?, ?, ?, ?, ?, ?)', (username, password, smtp_server, smtp_port, sender_email, rcv_email))
        conn.commit()
        return render_template("save_email_config.html")

    return render_template('email_config.html')
      
@app.route('/send_email/<int:id>')
def send_email(id):
    conn = sqlite3.connect('email_config.db')
    cursor = conn.cursor()

    # Fetch email configuration from database
    cursor.execute('SELECT * FROM smtp')
    email_config = cursor.fetchone()

    username = email_config[0]
    password = email_config[1]
    smtp_server = email_config[2]
    smtp_port = email_config[3]
    sender_email = email_config[4]
    rcv_email = email_config[5]

    # Fetch backup file name
    conn = sqlite3.connect('config_backup.db')
    cursor = conn.cursor()
    cursor.execute('SELECT config, device_type, hostname, date_added FROM backups WHERE id = ?', (id,))
    backup_data = cursor.fetchone()
    backup_file_data = backup_data[0]
    device_type = backup_data[1]
    hostname = backup_data[2]  
    date_added = backup_data[3]     
    backup_file_name = f'{device_type}_{hostname}_{date_added}.cfg'

    
    # Write backup data to file
    with open(backup_file_name, 'w') as f:
        f.write(backup_file_data)

    # Compose email message
    msg = MIMEMultipart()
    msg['Subject'] = "[Success] Network Backup Configuration - " f"{backup_file_name}"
    msg['From'] = sender_email
    msg['To'] = rcv_email

    # Attach backup file to email
    with open(backup_file_name, "rb") as attachment:
        part = MIMEApplication(
            attachment.read(),
            Name=os.path.basename(backup_file_name)
        )
    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(backup_file_name)}"'
    msg.attach(part)
    
    # Add body to email
    body = "The backup has been taken successfully, you can access it in the attachment."
    body_part = MIMEText(body, 'plain')
    msg.attach(body_part)

    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
      # server.starttls()  # you can use depend on your smtpserver.
        server.login(username, password)
        server.sendmail(sender_email, rcv_email, msg.as_string())
        server.quit()
        return render_template("email_sent.html")
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)


