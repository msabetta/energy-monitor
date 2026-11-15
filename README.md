# Energy Monitor

Piattaforma di monitoraggio dei consumi di energia elettrica e gas, pensata per il perimetro nazionale italiano e predisposta per l'integrazione di dati di sito (telelettura, contatori) quando disponibili.

## Stato del progetto

In sviluppo. Implementati finora:

- Connettore ENTSO-E per il carico reale (documentType A65) sulla zona IT_NORD
- Salvataggio del payload grezzo nella raw zone
- Parser XML in record normalizzati
- Scrittura nella trusted zone con `MERGE INTO` (riscarichi sicuri)
- Job orario e backfill
- DAG Airflow per l'esecuzione programmata

In attesa:

- Token Web API ENTSO-E (richiesto al supporto, in attesa di attivazione)
- Codici EIC per le altre zone italiane
- Connettori GME, Terna, Snam, ARERA
- Data quality (completezza, buchi, valori fuori range)
- Curated zone e API/dashboard

## Architettura

```
Fonti esterne            Ingestione            Storage (Iceberg)            Elaborazione       Consumo
ENTSO-E API     ─┐
Terna open data ─┼─► NiFi / Airflow ─► raw ─► trusted ─► curated ─►  Spark  ─►  Dashboard, API, alert
GME prezzi      ─┤
Snam / ARERA    ─┘
Dati di sito (futuro) ─► Kafka / NiFi ─► stesso schema, zona "site"
```

Principi:

- **Tre zone**: raw (payload invariato), trusted (dati normalizzati e deduplicati), curated (metriche e baseline).
- **Schema comune** per le serie temporali: timestamp UTC, zona, fonte, valore, unità.
- **Riproducibilità**: ogni riga trusted conserva il riferimento al payload grezzo.

## Struttura del repository

```
energy-monitor/
├── config/
│   └── sources.yaml          # endpoint, frequenza, licenza per ogni fonte
├── dags/
│   └── energy_entsoe_hourly.py   # DAG Airflow orario
├── ingestion/
│   ├── entsoe_client.py      # download carico reale
│   ├── parse_entsoe.py       # XML -> record normalizzati
│   ├── write_trusted.py      # MERGE INTO sulla trusted zone
│   ├── job_entsoe_hourly.py  # download, raw, parsing, merge per una finestra oraria
│   └── backfill.py           # recupero di giorni passati
├── storage/
│   └── schema.sql            # DDL tabelle Iceberg
├── tests/
│   └── test_parse_entsoe.py
├── deploy/
│   └── ansible/              # playbook per il cluster (da completare)
└── docs/
    └── data_sources.md       # documentazione fonti
```

## Requisiti

- Python 3.10+
- PySpark con supporto Iceberg e Hive
- Accesso a un cluster Spark/Iceberg (on-premise)
- Token ENTSO-E Web API, esportato come variabile d'ambiente

## Configurazione

Il token non va inserito nel codice o nel repository:

```bash
export ENTSOE_TOKEN=...
```

Le fonti e i codici zona sono in `config/sources.yaml`.

## Uso

Esecuzione per l'ultima ora completa:

```bash
python -m ingestion.job_entsoe_hourly
```

Esecuzione per un'ora specifica (ISO 8601, UTC):

```bash
python -m ingestion.job_entsoe_hourly 2026-11-14T10:00:00+00:00
```

Backfill degli ultimi giorni:

```bash
python -m ingestion.backfill 7
```

Test:

```bash
pytest tests/
```

## Note operative

- I dati ENTSO-E arrivano con ritardo: il job lavora su una finestra di circa 3 ore fa.
- Il `MERGE` sulla chiave `(zone, source, timestamp_utc)` rende sicuri i riscarichi.
- Con dati a 15 minuti attese 4 righe per ora, con dati orari 1.

## Fonti dati e licenze

Le licenze e i termini di riutilizzo vanno verificati per ogni fonte prima di un uso commerciale. Vedi `config/sources.yaml` e `docs/data_sources.md`.

## Sicurezza e compliance

Il progetto è pensato per deployment on-premise. Prima di proporlo a clienti del settore energetico vanno considerati ISO 27001, NIS2 e la gestione dei dati sensibili.

## Licenza

Da definire.
