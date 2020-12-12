git clone --branch addmainpy git@github.com:city-of-baltimore/trafficstat.git
cd trafficstat
git clone git@github.com:city-of-baltimore/bcgeocoder.git geocoder-repo
python -m venv venv-trafficstat
venv-trafficstat\Scripts\python.exe -m pip install --upgrade pip wheel pylint flake8 bandit mypy
venv-trafficstat\Scripts\python.exe -m pip install --upgrade ./geocoder-repo
venv-trafficstat\Scripts\python.exe -m pip install -r requirements.txt
