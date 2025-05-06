Eberle Artikel-Matching System 
================================ 
 
Installation: 
1. Laden Sie Python 3.10 oder höher von https://www.python.org/downloads/ herunter und installieren Sie es 
   (Wichtig: Aktivieren Sie die Option "Add Python to PATH" während der Installation) 
2. Doppelklicken Sie auf setup.bat, um alle notwendigen Abhängigkeiten zu installieren 
3. Nach der Installation starten Sie die Anwendung mit start.bat 
 
Benutzerhandbuch: 
1. Nach dem Start über start.bat wird ein Browser-Fenster mit der App geöffnet 
2. Laden Sie die drei benötigten Excel-Dateien hoch: 
   - Top-50 Liste (Eberle Italia) 
   - Übersetzungsdatei (JNEB-EBITA-ARTIKEL) 
   - Open Order List (Eberle Deutschland) 
3. Klicken Sie auf "Dateien verarbeiten" und warten Sie auf den Abschluss 
4. Laden Sie die erstellten Dateien herunter: 
   - Markierte Open Order List: Mit rot hervorgehobenen Zeilen und zusätzlichen Spalten 
   - Zusammenfassungsdatei: Mit allen Artikelnummern und Übereinstimmungen 
 
Bei Fragen wenden Sie sich an Dirk Wonhoefer. 

---

# Hinweise für Streamlit Cloud Deployment

1. **requirements.txt**
   - Stelle sicher, dass eine Datei `requirements.txt` im Hauptverzeichnis liegt. Diese sollte mindestens enthalten:
     ```
     streamlit
     pandas
     numpy
     ```
   - Weitere Pakete ggf. ergänzen.

2. **Import-Fehler (ModuleNotFoundError: utils.file_utils)**
   - Die Ordnerstruktur muss so bleiben, dass `app.py` und der Ordner `utils` im selben Verzeichnis liegen.
   - Die Imports in `app.py` müssen lauten:
     ```python
     from utils.file_utils import ...
     from utils.data_processing import ...
     ```
   - Falls weiterhin Fehler auftreten, prüfe, ob der Ordner `utils` und die Datei `__init__.py` (auch leer) im Repository sind.

3. **Startdatei**
   - Gib beim Deployment als Hauptdatei `app.py` an.

4. **Weitere Hinweise**
   - Alle benötigten Dateien müssen im Repository liegen.
   - Keine relativen Imports mit Punktnotation (z.B. `from .file_utils import ...`) verwenden.
