# Geonorge tegneregelassistent

Geonorge tegneregelassistent er en QGIS-plugin som hjelper deg med å implementere stiler/tegneregler basert på norske standarder som finnes i Geonorge. Denne pluginen kobler til Geonorge API for å hente og tildele stiler til lag i QGIS. Merk at Geonorge tegneregelassistent foreløpig bare fungerer med GML-filer.

## Funksjoner

- Hent stiler fra Geonorge basert på valgte lag og temaer.
- Tilpass stiler for spesifikke lag basert på norske tegneregler.
- Lagre rapporter over tildelte stiler for senere referanse.

## Installering

Følg disse trinnene for å installere Geonorge tegneregelassistent i QGIS:

1. Last ned `geonorge-tegneregelassistent_versjon.zip` fra [utgivelsessiden på GitHub](https://github.com/arkitektum/geonorge-tegneregelassistent/releases)).
2. Åpne QGIS, gå til `Plugins` -> `Manage and Install Plugins...`.
3. Klikk på `Install from ZIP` og velg den nedlastede `geonorge-tegneregelassistent_versjon.zip`-filen.
4. Klikk på `Install Plugin`.
5. Klikk på `Installed` og huk av for `geonorge-tegneregelassistent`.

## Bruk

1. **Åpne plugin**: Velg Geonorge-> Geonorge tegneregelassistent fra menyen for programtillegg i QGIS.
2. **Velg lag**: Marker lagene du ønsker å tilordne tegneregler.
3. **Søk etter tegneregler**: Klikk på `Søk` for å la pluginen finne relevante tegneregler fra Geonorge.
4. **Velg lag for oppdatering**: Velg blant lagene det er funnet tegneregler for hvilke som skal oppdateres.
5. **Bruk tegneregler**: Klikk på `Bruk` for å implementere tegnereglene på de valgte lagene.

## Konfigurasjon

Geonorge tegneregelassistent bruker to konfigurasjonsfiler for å tilpasse oppsettet: `qgis_config.json` og `resource_config.json`.

### qgis_config.json

Inneholder QGIS-spesifikke innstillinger som logging og rapportlagring.

```json
{
    "report": {
        "save_report": true,
        "report_base_path": null
    },
    "logging": {
        "enabled": true,
        "file_path": null,
        "level": "INFO",
        "format": null,
        "filemode": "w"
    },
    "endpoint_url": {
        "cartography": "https://register.geonorge.no/kartografi/api/cartography?",
        "schema": "https://register.geonorge.no/api/gml-applikasjonsskjema.json"
    }
}
```

## Logging
Logging kan aktiveres ved å sette "enabled" til `true` i qgis_config.json. Loggnivået kan justeres ved å endre "level"-verdien til ønsket nivå, for eksempel INFO, DEBUG, eller ERROR. Hvis "file_path" er satt til null, vil loggfilen automatisk bli opprettet i rotkatalogen under log-mappen.

* enabled: Aktiverer eller deaktiverer logging.
* file_path: Angir hvor loggfilen skal lagres. Hvis satt til null, lagres filen i rotkatalogen under log-mappen.
* level: Bestemmer detaljnivået på loggene (INFO, DEBUG, ERROR).
* format: Definerer formatet på logginnføringene. Hvis satt til null, brukes standardformat (tidspunkt - detaljnivå - melding).
* filemode: Angir om den samme loggfilen alltid skal oppdateres med nye innføringer i slutten (a), eller om den skal overskrives (w) for hver gang QGIS kjøres.

## Reportering
Genererer en rapport som gir en oversikt over tema, tegneregler og lag.

* GmlNode: Navnet på GML-noden som er behandlet.
* Geometry: Type geometri (punkt, linje, polygon, etc.).
* LayerName: Navn på laget i QGIS.
* StyleName: Navn på stilen som er brukt.
* Format: Stilformat (sld, qml).
* DatasetName: Navn på datasettet.
* Status: Status i Geonorge.
* FileUrl: URL for den tilhørende filen.

Rapporter kan genereres og lagres automatisk hvis "save_report" er satt til `true`. Du kan spesifisere en egendefinert lagringssti ved å sette "report_base_path". Hvis denne verdien er null, vil rapportene bli lagret i rotkatalogen under reports-mappen.

## Bidrag
Vi ønsker bidrag fra fellesskapet velkommen!

Ønsker du å bidra til å utvilke pluginen, kan du kommentere, lage pull request eller opprette issues i Git-repoet. Du kan også sende e-post til apps@arkitektum.no.

## Lisens

Denne programvaren er lisensiert med [GNU General Public License versjon 3.0 (GPL-3.0)](LICENSE)

For mer informasjon om GPL, se [GNU sitt offisielle nettsted](https://www.gnu.org/licenses/licenses.html#GPL).

## Kontakt
For spørsmål eller brukerstøtte, kontakt Arkitektum AS (apps@arkitektum.no).