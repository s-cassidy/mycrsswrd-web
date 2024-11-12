import subprocess
import os

bin = "/home/sites/39b/4/4030d5c045/mycrsswrd-web/venv/bin/python3"
dir = "/home/sites/39b/4/4030d5c045/mycrsswrd-web"
script = "/home/sites/39b/4/4030d5c045/mycrsswrd-web/main.py"
os.chdir(dir)

subprocess.Popen([bin,script])
