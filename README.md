# Installation
0. Take care of initial server setup. Guide for Ubuntu 20.04:
	https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04
1. Install dependencies.
	`sudo apt update`
	`sudo apt install build-essential git postgresql python3-dev nginx python3-venv redis`
1. Clone repo.
	`git clone https://github.com/geroko/KCArchive.git /var/www/KCArchive`
1. Create venv inside KCArchive folder.
	`cd /var/www/KCArchive`
	`python3 -m venv venv`
1. Activate venv and install required packages.
	`source venv/bin/activate`
	`pip install -r deployment/requirements.txt`
1. Create postgres user and database. Replace $username with your username.
	`sudo -u postgres psql`
	`CREATE USER $username;`
	`\password $username`
	`CREATE DATABASE kcarchive OWNER $username;`
	`\q`
1. Run install script.
	`./install.sh`
1. Edit application config file. Make sure to edit the one in the instance directory.
	`nano instance/config.json`
1. Edit nginx config, replace 'example.com' with your domain.
	`nano /etc/nginx/conf.d/kcarchive.conf`
1. Setup cronjob for scraper.
	`crontab -e`
	Add the following line to the bottom of the file.
	`*/30 */1 * * * cd /var/www/KCArchive && /var/www/KCArchive/venv/bin/python3 scraper.py`

# Issues
1. Both the Thread and Post tables use a post number as their primary key, should be a serial.
1. Can only scrape a single board, add a Board table
1. Full images are not supported
1. Spoilered thumbs don't always get downloaded
1. Pagination is messy, is there a better solution?
1. Generating reply backlinks is slow for large threads
1. Searching by file hash doesn't always work. Add a 'hash' column?
