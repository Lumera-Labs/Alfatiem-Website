# Al Fatiem Alarabi Website

Django website with an admin panel

_Requires Python 3.10 or newer._

Local setup (macOS / Linux)
bash

`./install.sh dev`


The installer sets up the project and creates an admin account on the first run.

To launch open:

Website: http://127.0.0.1:8000

OR

Admin: http://127.0.0.1:8000/admin/


Production setup (Proxmox LXC, Debian/Ubuntu)

`
git clone https://github.com/Lumera-Labs/Alfatiem-Website /opt/alfatiem && cd /opt/alfatiem
sudo ./install.sh prod`


The installer asks for the domain name, admin URL path (use something other than admin so AI Agents can't find that using the rules of the robots.txt).

It creates the .env file, configures the system user and Gunicorn service for automatic scripting, and creates the admin account.

### Useful commands:

Update:

`
git pull && sudo ./install.sh prod
`

View logs:

`
journalctl -u alfatiem -f
`

Create a backup:

`
sudo ./install.sh backup
`

Backups are stored in backups/, with the 14 most recent copies retained.


Create another admin account:

`
sudo ./install.sh admin
`


To modify seeded content without overwriting existing edits:

`
python manage.py seed_site
`

To restore all page texts to the seeded content:

`
python manage.py seed_site --reset-texts
`

*Note that the reset command overwrites edited page texts.*


### Project Structure

```text
project/
├── config/
├── core/
├── news/
├── projects/
├── templates/
├── static/
├── media/
└── db.sqlite3