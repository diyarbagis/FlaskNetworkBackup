# FlaskNetworkBackup
A free open-source Flask app for backup on switches,routers and firewalls. 

## Features
*  Creating a .cfg file and email the file as an attachment
*  Easy-to-use web interface
*  Add your device once and backup without re-enter again 
*  Store your email configuration, login data, backups on SQLite
*  Download configuration backup as cfg file 
*  Search devices and backups

## Prerequisites
* git
->sudo apt install git
* pip
-> sudo apt install python3-pip

## Usage
* $ git clone https://github.com/diyarbagis/FlaskNetworkBackup.git
* $ cd FlaskNetworkBackup
* $ pip install -r requirements.txt
* $ python3 fnetbackup.py 
* Open 0.0.0.0:6565 on your browser and get your backup.

## If you want to run as a service
#### Follow these instructions
* $ sudo nano /etc/systemd/system/fnetbackup.service

```bash
[Unit]
Description=Flask Network Backup Service
After=network.target

[Service]
User=<your_username>
WorkingDirectory=/path/to/file/location
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"
ExecStart=/usr/bin/python3 fnetbackup.py
Restart=always

[Install]
WantedBy=multi-user.target
```

* $ sudo systemctl daemon-reload
* $ sudo systemctl enable fnetbackup
* $ sudo systemctl start fnetbackup

* Open 0.0.0.0:6565 on your browser and get your backup.

## Screenshots

#### Add your device and get backup!
![add_device](https://user-images.githubusercontent.com/50266008/225598408-8636ef90-2af8-44fd-ae75-356b20aee5a4.jpg)

#### Configure your smtp settings and get email with your backup attached.
![email_config](https://user-images.githubusercontent.com/50266008/225902193-872921ef-010c-4d5b-8783-7fb42f2c263f.jpg)

#### List your devices
![devices](https://user-images.githubusercontent.com/50266008/225598964-20e7d82b-8755-4339-b4b2-205b6731a63d.jpg)

#### List your backups
![backups](https://user-images.githubusercontent.com/50266008/225598984-ad6ec638-0f9a-428f-8e73-324ce2b5ea8b.jpg)

#### Show Backup
![backups1](https://user-images.githubusercontent.com/50266008/225599111-7ee2a00a-385a-45bc-9167-7b37fec25ccb.jpg)

#### Download Backup
![backups1download](https://user-images.githubusercontent.com/50266008/225599129-fa81f3e6-c261-4ed6-bed2-f2f861cd1752.jpg)





