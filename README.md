![demo](https://github.com/KapiteinKrapBijKas/defender_schemas_to_kustainer/blob/main/demo.gif)

# Defender XDR schemas to Kustainer

Python script that maps Microsoft Defender XDR Schemas to a local Kustainer Data Explorer instance by parsing the open source Microsoft documentation. These schemas will be created as tables in the *AdvancedHunting* database.

## Requirements

- uv
- docker compose

## Start kustainer
You can use docker compose to start a persistent Kustainer instance. The persistent data will be mapped to the *kustodata* directory in the root of this project:

```bash
docker compose up -d
```

## Create venv and install dependencies
```bash
uv sync
```

## Run script

```bash
uv run main.py
```

## List created tables

```bash
curl -X post -H 'Content-Type: application/json' -d '{"db": "AdvancedHunting", "csl":".show tables"}' http://localhost:8080/v1/rest/mgmt | jq
```

## Query sample data

```bash
curl -X post -H 'Content-Type: application/json' -d '{"db": "AdvancedHunting", "csl":"EmailUrlInfo | take 1"}' http://localhost:8080/v2/rest/query | jq
```
