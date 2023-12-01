![script output](https://github.com/KapiteinKrapBijKas/defender_schemas_to_kustainer/blob/main/screen.png?raw=true)

# MS Docs schemas to Kustainer

Python script that maps Microsoft Defender XDR Schemas to a local Kustainer Data Explorer instance by scraping the open source Microsoft documentation. These schemas will be created as tables in the *AdvancedHunting* database.


## Clone repository
Clone this repository including submodules:

```bash
$ git clone --recursive-submodules https://github.com/KapiteinKrapBijKas/defender_schemas_to_kustainer
```

## Start kustainer
You can use docker compose to start a persistent Kustainer instances. The persistent data will be mapped to the *kustodata* directory in the root of this project:

```bash
$ docker compose up -d
```

## Install pip requirements
```bash
$ python3 -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```

## Run script

```bash
$ python3 main.py
```
