
# Dokumentasjon for `resource_config.json`

`resource_config.json` brukes i Geonorge Tegneregelassistent-pluginen for å knytte GML-skjemaer som ikke finnes i Geonorges [skjema-register](https://register.geonorge.no/gml-applikasjonsskjema?register=GML+applikasjonsskjema), med tilpassede tegneregler. Siden det kan være forskjeller mellom navnene på [tegneregler](https://register.geonorge.no/register/kartografi) og GML-kildenoder, hjelper denne filen med å lage nødvendige koblinger.

## Struktur og Felter

### 1. `schemas` (liste over skjema-koblinger)
   Inneholder en liste over GML-skjemaer der hvert objekt representerer et spesifikt GML-skjema.

   - **`documentreference`**: URL til GML-skjemaet.
   - **`label`**: Beskrivende navn på skjemaet, brukt for identifisering.
   - **`DatasetUuid`**: UUID for datasettet i Geonorge (valgfritt).

   **Eksempel:**
   ```json
   {
       "documentreference": "https://skjema.geonorge.no/SOSI/produktspesifikasjon/MaritimInfrastruktur/20201020/MaritimInfrastruktur.xsd",
       "label": "Sjøkart - Maritim infrastruktur",
       "DatasetUuid": null
   }
   ```

### 2. `schemaOverrides` (tilpasset navneoverstyring for skjemaer)
   I tilfeller hvor tegneregel-navnet avviker fra GML-kilden, gir `schemaOverrides` mulighet for å tilpasse denne koblingen.

   - **`sourceLabel`**: Navnet på skjemaet fra kildedataene.
   - **`targetLabel`**: Navnet på tegneregelen i Geonorge.
   - **`exactMatch`**: Angir om `sourceLabel` og `targetLabel` må samsvare nøyaktig (true) eller om en delvis match er tillatt (false).

   **Eksempel:**
   ```json
   {
       "sourceLabel": "Administrative enheter",
       "targetLabel": "Administrative enheter kommuner",
       "exactMatch": false
   }
   ```

### 3. `schemaNodeOverrides` (overstyringer for individuelle GML-noder)
   Brukes til å knytte spesifikke noder i et GML-skjema til tilpassede tegneregler i Geonorge. Dette er spesielt nyttig når en enkelt GML-kildenode skal ha en spesifikk tegneregler stil.

   - **`sourceNode`**: Navnet på GML-noden som trenger en tilpasset stil.
   - **`styleName`**: Tegneregelen som skal brukes for denne noden.
   - **`exactMatch`**: Angir om det må være en eksakt match mellom `sourceNode` og `styleName` (true) eller om det kan være en fleksibel match (false).

   **Eksempel:**
   ```json
   "schemaNodeOverrides": {
       "Sjøkart - Maritim infrastruktur": [
           {
               "sourceNode": "HavbrukForankret",
               "styleName": "Havbruk - forankret / Akvakultur",
               "exactMatch": true
           }
       ]
   }
   ```

## Eksempelkonfigurasjon
```json
{
    "schemas": [
        {
            "documentreference": "https://skjema.geonorge.no/SOSI/produktspesifikasjon/MaritimInfrastruktur/20201020/MaritimInfrastruktur.xsd",
            "label": "Sjøkart - Maritim infrastruktur",
            "DatasetUuid": null
        }
    ],
    "schemaOverrides": [
        {
            "sourceLabel": "Administrative enheter",
            "targetLabel": "Administrative enheter kommuner",
            "exactMatch": false
        }
    ],
    "schemaNodeOverrides": {
        "Sjøkart - Maritim infrastruktur": [
            {
                "sourceNode": "HavbrukForankret",
                "styleName": "Havbruk - forankret / Akvakultur",
                "exactMatch": true
            }
        ]
    }
}
```

## Bruksområder

- **Standardisere visning av kartdata**: Sørger for at kartdata vises i henhold til offisielle tegneregler.
- **Tilpassede GML-koblinger**: Gjør det mulig å bruke alternative GML-skjemaer eller tilpasse navnene på tegneregler for å passe dataene i Geonorge.

## Tips for Konfigurering

- **Sjekk at alle `documentreference`-URLer** peker til oppdaterte og gyldige Geonorge-skjemaer.
- **Bruk `exactMatch` med forsiktighet** for å tillate fleksibilitet når nødvendig, men sørg for eksakte treff når det gjelder spesifikke noder eller tegneregler.
- **Lagre en kopi av lokale endringer i `resources_config.json` før du oppdaterer pluginen.** Dette sikrer at tilpassede koblinger og innstillinger ikke går tapt under oppdateringen.
