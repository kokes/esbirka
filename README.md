# Konverze dat z e-Sbírky do lidského formátu

V tuhle chvíli jsou [otevřená data e-Sbírky](https://opendata.eselpoint.cz/datove-sady-esbirka/) tak epicky nepoužitelná, že jsem se jal to trochu upravit. Největší ze souborů má více jak 25 GB po dekompresi, jde ale o JSON slovník (který má v sobě velmi dlouhý seznam objektů), což je věc, která se poměrně nekomfortně zpracovává v drtivé většině nástrojů.

Místní `od.py` skript je poměrně přímočarý - data stahuje přímo od zdroje a konvertuje tyto divnoseznamy do něčeho, co jde zpracovat streamem - NDJSON, neboli co řádek, to JSON objekt (jelikož každý JSON objekt jde serializovat do jednořádkové podoby). Po této konverzi jde pak napsat skript ne nepodobný následujícímu:

```python
import gzip
import json

with gzip.open("002PravniAkt.jsonld.gz", "rt") as f:
    for line in f:
        data = json.loads(line)
```

Skript tak bude brát nula nula nic co do paměti, poběží poměrně rychle a vůbec to bude větší pohoda na práci. Ideální by byl tabulkový formát (jelikož data nejspíš poputují někam do relační databáze), ale to zas možná někdy jindy.
