import subprocess 
import os 
import sys 
import webbrowser 
import time 
 
def run_app(): 
    # Pfad zur app.py ermitteln 
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    app_path = os.path.join(base_dir, "app.py") 
    print(f"Starte App: {app_path}") 
 
    # Starte Streamlit-Server 
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.headless", "true"] 
    process = subprocess.Popen(cmd) 
 
    # Warte kurz und öffne Browser 
    print("Warte, bis der Server startet...") 
    time.sleep(3) 
    print("Öffne Browser...") 
    webbrowser.open("http://localhost:8501") 
 
    print("App läuft. Schließen Sie die Konsole oder drücken Sie Strg+C, um die App zu beenden.") 
    # Warte auf Beendigung 
    try: 
        process.wait() 
    except KeyboardInterrupt: 
        print("Beende App...") 
        process.terminate() 
 
if __name__ == "__main__": 
    run_app() 
