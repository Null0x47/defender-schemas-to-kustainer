![script output](https://github.com/KapiteinKrapBijKas/defender_schemas_to_kustainer/blob/main/screen.png?raw=true)

# Defender XDR schemas to Kustainer

Python script that maps Microsoft Defender XDR Schemas to a local Kustainer Data Explorer instance by parsing the open source Microsoft documentation. These schemas will be created as tables in the *AdvancedHunting* database.


## Clone repository
Clone this repository including submodules:

```bash
git clone --recurse-submodules https://github.com/KapiteinKrapBijKas/defender_schemas_to_kustainer
```

## Start kustainer
You can use docker compose to start a persistent Kustainer instance. The persistent data will be mapped to the *kustodata* directory in the root of this project:

```bash
docker compose up -d
```

## Install pip requirements
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Run script

```bash
python3 main.py
```
