import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime

from utils.file_utils import (
    load_excel_file, 
    validate_top50_file, 
    validate_translator_file, 
    validate_ool_file,
    create_downloadable_excel,
    create_downloadable_summary
)
from utils.data_processing import process_all_data

# --- CSS Styling ---
def local_css():
    st.markdown("""
    <style>
        /* Corporate Colors */
        :root {
            --primary: #003366;
            --secondary: #405d7d;
            --accent: #f8f9fa;
            --text: #212529;
            --light-gray: #e9ecef;
        }
        
        /* Main layout */
        .main {
            padding: 1.5rem;
        }
        .stApp {
            background-color: white;
        }
        
        /* Header styling */
        h1, h2, h3, h4 {
            color: var(--primary);
            font-weight: 400;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
        h1 {
            font-size: 2rem;
            border-bottom: 2px solid var(--primary);
            padding-bottom: 0.5rem;
        }
        h2 {
            font-size: 1.5rem;
            margin-top: 1.5rem;
        }
        h3 {
            font-size: 1.2rem;
        }
        
        /* Card styling */
        .file-card {
            background-color: var(--accent);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: 100%;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            background-color: var(--secondary);
        }
        
        /* Divider */
        hr {
            border-top: 1px solid var(--light-gray);
            margin-top: 2rem;
            margin-bottom: 2rem;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 1rem;
            color: var(--text);
            font-size: 0.9rem;
            border-top: 1px solid var(--light-gray);
            margin-top: 2rem;
        }
        
        /* Corporate Header */
        .corporate-header {
            padding: 1rem;
            background-color: var(--primary);
            color: white;
            border-radius: 5px;
            margin-bottom: 1.5rem;
        }
        .corporate-title {
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        .corporate-subtitle {
            font-weight: 300;
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
        }
        .corporate-dev {
            font-size: 0.8rem;
            font-style: italic;
            text-align: right;
        }
        
        /* Compact metrics */
        .compact-metric {
            padding: 0.5rem;
            background-color: var(--accent);
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 500;
            color: var(--primary);
        }
        .metric-label {
            font-size: 0.9rem;
            color: var(--secondary);
        }
        
        /* Progress indicators */
        .stProgress > div > div > div > div {
            background-color: var(--primary);
        }
        
        /* File upload area */
        .uploadedFile {
            border: 1px dashed var(--secondary);
            border-radius: 5px;
            padding: 0.5rem;
        }
        
        /* Caption styling */
        .caption {
            color: var(--secondary);
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }
        
        /* Download buttons */
        .download-button {
            display: inline-block;
            background-color: var(--primary);
            color: white !important;
            padding: 0.6rem 1.2rem;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 0.5rem;
            transition: all 0.3s;
        }
        .download-button:hover {
            background-color: var(--secondary);
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

def get_corporate_header():
    return """
    <div class="corporate-header">
        <div class="corporate-title">J.N. Eberle & Cie. GmbH KI Apps</div>
        <div class="corporate-subtitle">Intelligentes Artikel-Matching-System</div>
        <div class="corporate-dev">KI Entwickler: Dirk Wonhoefer mit Claude3.7</div>
    </div>
    """

# Seitenkonfiguration
st.set_page_config(
    page_title="Eberle Artikelnummern-Matching",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS und Corporate Design anwenden
local_css()
st.markdown(get_corporate_header(), unsafe_allow_html=True)

# App-Titel und Beschreibung
st.markdown("<h1>Artikelnummern-Matching</h1>", unsafe_allow_html=True)
st.markdown("""
<p>Diese App automatisiert den Prozess zum Abgleich von Artikelnummern zwischen Eberle Deutschland und Eberle Italien.</p>
""", unsafe_allow_html=True)

# Hauptcontainer
main_container = st.container()

with main_container:
    # Datei-Upload-Sektion
    st.markdown("<h2>1. Dateien hochladen</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown('<div class="file-card">', unsafe_allow_html=True)
        st.markdown("<h3>Top-50 Liste</h3>", unsafe_allow_html=True)
        st.markdown('<div class="caption">Eberle Italia</div>', unsafe_allow_html=True)
        top50_file = st.file_uploader("Top-50 Excel-Datei", type=["xlsx"], key="top50", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="file-card">', unsafe_allow_html=True)
        st.markdown("<h3>Übersetzungsdatei</h3>", unsafe_allow_html=True)
        st.markdown('<div class="caption">JNEB-EBITA-ARTIKEL</div>', unsafe_allow_html=True)
        translator_file = st.file_uploader("Übersetzungsdatei", type=["xlsx"], key="translator", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="file-card">', unsafe_allow_html=True)
        st.markdown("<h3>Open Order List</h3>", unsafe_allow_html=True)
        st.markdown('<div class="caption">Eberle Deutschland</div>', unsafe_allow_html=True)
        ool_file = st.file_uploader("Open Order List", type=["xlsx"], key="ool", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Verarbeitungs-Button
    st.markdown("<h2>2. Datenverarbeitung</h2>", unsafe_allow_html=True)
    
    process_button = st.button("Dateien verarbeiten", type="primary")
    
    if process_button:
        # Prüfen, ob alle Dateien hochgeladen wurden
        if not top50_file or not translator_file or not ool_file:
            st.error("Bitte laden Sie alle drei Dateien hoch, bevor Sie fortfahren.")
        else:
            # Zeige Fortschrittsanzeige
            progress_container = st.container()
            progress_bar = progress_container.progress(0)
            status_text = progress_container.empty()
            
            # Dateien laden
            status_text.info("Dateien werden geladen...")
            progress_bar.progress(10)
            
            try:
                top50_df = load_excel_file(top50_file)
                progress_bar.progress(20)
                
                translator_df = load_excel_file(translator_file)
                progress_bar.progress(30)
                
                ool_df = load_excel_file(ool_file)
                progress_bar.progress(40)
                
                # Validierung der Dateien
                status_text.info("Dateien werden validiert...")
                
                if not validate_top50_file(top50_df):
                    st.error("Die Top-50-Datei hat nicht das erwartete Format.")
                    progress_bar.empty()
                    status_text.empty()
                elif not validate_translator_file(translator_df):
                    st.error("Die Übersetzungsdatei hat nicht das erwartete Format.")
                    progress_bar.empty()
                    status_text.empty()
                elif not validate_ool_file(ool_df):
                    st.error("Die Open Order List hat nicht das erwartete Format.")
                    progress_bar.empty()
                    status_text.empty()
                else:
                    # Datenverarbeitung
                    status_text.info("Daten werden verarbeitet...")
                    progress_bar.progress(60)
                    
                    match_indices, summary_data, ool_df_extended = process_all_data(top50_df, translator_df, ool_df)
                    
                    progress_bar.progress(80)
                    status_text.info("Ergebnisdateien werden erstellt...")
                    
                    # Erstelle herunterladbare Dateien
                    ool_b64 = create_downloadable_excel(ool_df_extended, match_indices)
                    summary_b64 = create_downloadable_summary(summary_data)
                    
                    progress_bar.progress(100)
                    status_text.success("Verarbeitung abgeschlossen!")
                    
                    # Ergebnisse anzeigen
                    st.markdown("<h2>3. Ergebnisse</h2>", unsafe_allow_html=True)
                    
                    # Statistik anzeigen
                    st.markdown("<h3>Zusammenfassung</h3>", unsafe_allow_html=True)
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        codices_count = len({item['codice_full'] for item in summary_data})
                        st.markdown(f"""
                        <div class="compact-metric">
                            <div class="metric-value">{codices_count}</div>
                            <div class="metric-label">Verarbeitete Codices</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with metric_col2:
                        artikel_count = len({item['artikelnummer'] for item in summary_data})
                        st.markdown(f"""
                        <div class="compact-metric">
                            <div class="metric-value">{artikel_count}</div>
                            <div class="metric-label">Gefundene Artikelnummern</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with metric_col3:
                        mark_count = len(match_indices)
                        st.markdown(f"""
                        <div class="compact-metric">
                            <div class="metric-value">{mark_count}</div>
                            <div class="metric-label">Markierte Zeilen in OOL</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Download-Buttons
                    st.markdown("<h3>Ergebnisdateien herunterladen</h3>", unsafe_allow_html=True)
                    
                    download_col1, download_col2 = st.columns(2)
                    
                    # Aktuelles Datum für Dateinamen
                    current_date = datetime.now().strftime("%d.%m.%Y")
                    
                    with download_col1:
                        ool_href = f'<a class="download-button" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{ool_b64}" download="OOL_markiert_{current_date}.xlsx">Markierte Open Order List</a>'
                        st.markdown(ool_href, unsafe_allow_html=True)
                        
                    with download_col2:
                        summary_href = f'<a class="download-button" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{summary_b64}" download="Zusammenfassung_{current_date}.xlsx">Zusammenfassungsdatei</a>'
                        st.markdown(summary_href, unsafe_allow_html=True)
                    
                    # Vorschau der zusätzlichen Informationen
                    if len(match_indices) > 0:
                        st.markdown("<h3>Vorschau der zusätzlichen Informationen</h3>", unsafe_allow_html=True)
                        
                        preview_df = ool_df_extended.iloc[match_indices[:5] if len(match_indices) > 5 else match_indices]
                        preview_cols = ['artikel no', 'Abmessung', 'Lagerbestand', 'Kundenauftraege', 'Monatlicher Verbrauch', 'Codice']
                        preview_cols = [col for col in preview_cols if col in preview_df.columns]
                        
                        # Tabelle mit besserem Styling
                        st.dataframe(
                            preview_df[preview_cols],
                            use_container_width=True,
                            column_config={
                                "artikel no": "Artikelnummer",
                                "Abmessung": "Abmessung",
                                "Lagerbestand": st.column_config.NumberColumn(
                                    "Lagerbestand",
                                    format="%.2f"
                                ),
                                "Kundenauftraege": st.column_config.NumberColumn(
                                    "Kundenaufträge",
                                    format="%.2f"
                                ),
                                "Monatlicher Verbrauch": st.column_config.NumberColumn(
                                    "Monatlicher Verbrauch",
                                    format="%.2f"
                                ),
                                "Codice": "Codice"
                            }
                        )
                    else:
                        st.info("Keine Übereinstimmungen gefunden.")
                    
                    # Toggle für erweiterte Informationen
                    with st.expander("Weitere Informationen anzeigen"):
                        st.write("Diese App hilft beim Abgleich von Artikelnummern zwischen verschiedenen ERP-Systemen.")
                        st.write("""
                        Das Ergebnis besteht aus zwei Excel-Dateien:
                        1. **Markierte Open Order List**: Die OOL mit rot hervorgehobenen übereinstimmenden Zeilen und zusätzlichen Spalten für Lagerbestand, Kundenaufträge und monatlichen Verbrauch.
                        2. **Zusammenfassungsdatei**: Eine Zusammenfassung aller verarbeiteten Codices, ihrer zugehörigen Artikelnummern und ob sie in der OOL gefunden wurden.
                        """)
                    
            except Exception as e:
                st.error(f"Bei der Verarbeitung ist ein Fehler aufgetreten: {str(e)}")
                progress_bar.empty()
                status_text.empty()
    
# Footer
st.markdown('<div class="footer">J.N. Eberle & Cie. GmbH © 2025</div>', unsafe_allow_html=True) 