# Fonti dati

Questo documento descrive le fonti usate dal progetto, con endpoint, formato, frequenza, licenza e responsabile. Le informazioni marcate "da verificare" vanno completate prima di un uso commerciale.

Le stesse informazioni in forma strutturata sono in `config/sources.yaml`. In caso di discordanza, fa fede il portale della fonte.

## Riepilogo

| Fonte | Tipo | Stato | Formato | Frequenza |
|---|---|---|---|---|
| ENTSO-E - carico reale | Elettricità | Implementata (zona IT_NORD) | XML | Oraria, con ritardo |
| ENTSO-E - generazione per fonte | Elettricità | Pianificata | XML | Oraria, con ritardo |
| GME - PUN e mercati | Elettricità, prezzi | Pianificata | CSV | Giornaliera |
| Terna - dati di sistema | Elettricità | Pianificata | CSV / XLSX | Da verificare |
| Snam Rete Gas - flussi | Gas | Pianificata | Da verificare | Da verificare |
| ARERA - open data | Regolazione, tariffe | Pianificata | Da verificare | Da verificare |

## ENTSO-E Transparency Platform

**Descrizione.** Piattaforma europea che pubblica dati di carico, generazione, scambi e prezzi per le zone di mercato.

**Portale e API.** Portale: `https://transparency.entsoe.eu`. Endpoint Web API: `https://web-api.tp.entsoe.eu/api`.

**Autenticazione.** Web API Security Token, passato come parametro `securityToken`. Il token è personale, non va inserito nel codice né nel repository, e viene letto dalla variabile d'ambiente `ENTSOE_TOKEN`.

**Dataset utilizzati.**

- Carico reale: `documentType=A65`, `processType=A16`. Implementato.
- Generazione per fonte: `documentType=A75`, `processType=A16`. Pianificato.

**Zone italiane.** I codici EIC sono da verificare nella documentazione ENTSO-E. Quello del Nord è `10Y1001A1001A73I`. Le altre zone (Centro-Nord, Centro-Sud, Sud, Sicilia, Sardegna) sono da completare.

**Formato di risposta.** XML con namespace IEC 62325. Il parser in `ingestion/parse_entsoe.py` assume il namespace `urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0`, da verificare sui file reali.

**Frequenza e ritardo.** I dati arrivano con ritardo di alcune ore. Il job lavora su una finestra di circa 3 ore fa.

**Licenza e termini.** Da verificare sui termini d'uso del portale, in particolare per usi commerciali.

**Accesso al token.** Il token non compare nel menu My Account del portale. È stata inviata richiesta di attivazione a transparency@entsoe.eu. Stato: in attesa.

**Responsabile.** Da definire.

## GME - Gestore dei Mercati Energetici

**Descrizione.** Prezzi del PUN e dei mercati day-ahead e intraday dell'energia elettrica, e prezzi del gas (mercato MGAS / PSV).

**Portale.** `https://www.mercatoelettrico.org`.

**Formato.** CSV scaricabili dal portale. Accesso programmatico da verificare.

**Frequenza.** Giornaliera.

**Licenza e termini.** Da verificare sulle condizioni di riutilizzo del GME.

**Responsabile.** Da definire.

## Terna - Trasparenza e Open Data

**Descrizione.** Dati di sistema: domanda, produzione, saldo di scambio con l'estero.

**Portale.** `https://www.terna.it`, sezione Trasparenza e Open Data.

**Formato.** CSV e XLSX. Accesso programmatico in parte disponibile, da verificare.

**Frequenza.** Da verificare per ogni dataset.

**Licenza e termini.** Da verificare sulla licenza open data di Terna.

**Responsabile.** Da definire.

## Snam Rete Gas

**Descrizione.** Flussi e dati di trasporto gas sulla rete nazionale.

**Portale.** `https://www.snam.it`.

**Formato, frequenza, licenza.** Da verificare.

**Responsabile.** Da definire.

## ARERA - Open data

**Descrizione.** Tariffe, offerte, switching e indicatori di qualità del servizio elettrico e gas. Utile per il contesto normativo e per la parte di bolletta.

**Portale.** `https://www.arera.it`.

**Formato, frequenza, licenza.** Da verificare.

**Responsabile.** Da definire.

## Dati di misura di sito

Telelettura e consumi per punto di prelievo non sono dati pubblici. Si ottengono tramite accordi con i distributori (per esempio E-Distribuzione, A2A, Italgas) o con il cliente finale. Questa fonte non è ancora attiva e richiede un accordo specifico, con termini di riutilizzo e protezione dei dati da definire.

## Note di governance

- Ogni fonte va aggiornata in questo documento e in `config/sources.yaml` quando cambiano endpoint, formato o licenza.
- Le licenze vanno verificate per ogni fonte prima di proporre il prodotto a un cliente.
- Il dato grezzo è conservato nella raw zone senza modifiche, così ogni calcolo è riproducibile.
