# Quelle der Kochbuch-App

Die App im Hauptverzeichnis wird aus diesem Ordner gebaut. Nicht von Hand ändern.

- `src/rezepte.md`: alle Rezepte (Textform, ein Abschnitt pro Rezept `## rNN · Titel`)
- `src/index.template.html`: die App (Oberfläche und Logik)
- `build/images.json`: Rezeptbilder als Daten, Schlüssel = Rezept-Nummer (`r00` …)
- `build/parse.py`, `build/build.py`: wandeln Rezepte und Bilder in `index.html`, `manifest.webmanifest`, `sw.js` und Icons um
- `update.sh`: baut neu und kopiert die Dateien ins Hauptverzeichnis (benötigt Python 3 mit Pillow)

Neues Rezept: Abschnitt an `src/rezepte.md` anhängen, Bild in `build/images.json` ergänzen, `./update.sh` ausführen, committen.
