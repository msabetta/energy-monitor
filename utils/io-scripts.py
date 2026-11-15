import os
import requests
from datetime import datetime, timedelta, timezone
import sys

BASE_URL = "https://web-api.tp.entsoe.eu/api"


## Funzioni di utilità per la lettura di file di testo
##example: get_line_from_file("config.txt", 2)  # legge la seconda riga del file
def get_line_from_file(file_path: str, line_number: int) -> str:
    """Restituisce la riga specificata da un file di testo, o None se non esiste."""
    try:
        with open(file_path, "r") as f:
            for current_line_number, line in enumerate(f, start=1):
                if current_line_number == line_number:
                    return line.rstrip("\n")
    except FileNotFoundError:
        print(f"File non trovato: {file_path}")
    return None


##example: set_env_variable_from_file("ENTSOE_TOKEN", "config.txt", 2)  # imposta ENTSOE_TOKEN leggendo la seconda riga del file
##example config.txt:
##ENTSOE_TOKEN=your_token_here
def set_env_variable_from_file(var_name: str, file_path: str, line_number: int) -> None:
    """Imposta una variabile d'ambiente leggendo una riga specifica da un file."""
    value = get_line_from_file(file_path, line_number)
    if value is not None:
        os.environ[var_name] = value
        print(f"Variabile d'ambiente '{var_name}' impostata da {file_path}:{line_number}")
    else:
        print(f"Impossibile impostare '{var_name}': riga {line_number} non trovata in {file_path}")
        

##example: fetch_actual_load("10Y1001A1001A73I", datetime.now(), datetime.now() + timedelta(hours=1))  # scarica il carico reale per la zona specificata
def fetch_actual_load(zone: str, start: datetime, end: datetime) -> str:
    """Carico reale (documentType A65, processType A16), restituisce XML grezzo."""
    token = os.environ.get("ENTSOE_TOKEN")
    if not token:
        raise ValueError("La variabile d'ambiente ENTSOE_TOKEN non è impostata.")
    
    params = {
        "securityToken": token,
        "documentType": "A65",
        "processType": "A16",
        "outBiddingZone_Domain": zone,
        "periodStart": start.strftime("%Y%m%d%H%M"),
        "periodEnd": end.strftime("%Y%m%d%H%M"),
    }
    resp = requests.get(BASE_URL, params=params, timeout=60)
    resp.raise_for_status()
    return resp.text  # il dato grezzo va salvato così com'è nella raw zone

##example: open_file_for_writing("output/data.txt")  # apre il file per la scrittura, creando eventuali directory mancanti
def open_file_for_writing(file_path: str):
    """Apre un file per la scrittura, creando eventuali directory mancanti."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    return open(file_path, "w")

##example: write_to_file("output/data.txt", "Contenuto da scrivere")  # scrive il contenuto in un file, creando eventuali directory mancanti
def write_to_file(file_path: str, content: str) -> None:
    """Scrive il contenuto in un file, creando eventuali directory mancanti."""
    with open_file_for_writing(file_path) as f:
        f.write(content)
        
def get_env_variable(var_name: str) -> str:
    """Restituisce il valore di una variabile d'ambiente, o None se non esiste."""
    return os.environ.get(var_name)

