import pandas as pd
import io
import base64
import xlsxwriter
from typing import Tuple, Dict, List, Any, Optional

def load_excel_file(uploaded_file) -> pd.DataFrame:
    """
    Lädt eine hochgeladene Excel-Datei und gibt sie als DataFrame zurück.
    
    Args:
        uploaded_file: Die hochgeladene Datei vom Streamlit-Uploader
        
    Returns:
        DataFrame mit den Daten aus der Excel-Datei
    """
    return pd.read_excel(uploaded_file)

def validate_top50_file(df: pd.DataFrame) -> bool:
    """
    Überprüft, ob die hochgeladene Datei die erwartete Struktur einer Top-50-Datei hat.
    
    Args:
        df: DataFrame der Top-50-Datei
        
    Returns:
        True, wenn die Datei gültig ist, sonst False
    """
    # Prüfen, ob die Datei mindestens eine 'Codice'-Spalte hat
    if 'Codice' not in df.columns:
        return False
    
    # Prüfen, ob wichtige Spalten vorhanden sind
    required_columns = ['Lagerbestand', 'Kundenauftraegen', 'Montatlicher Verbrauch']
    for col in required_columns:
        if col not in df.columns:
            return False
    
    return True

def validate_translator_file(df: pd.DataFrame) -> bool:
    """
    Überprüft, ob die hochgeladene Datei die erwartete Struktur einer Übersetzungsdatei hat.
    
    Args:
        df: DataFrame der Übersetzungsdatei
        
    Returns:
        True, wenn die Datei gültig ist, sonst False
    """
    # Da die Übersetzungsdatei keine klaren Spaltenbezeichnungen hat, 
    # prüfen wir, ob genügend Spalten vorhanden sind
    return df.shape[1] >= 17  # Wir benötigen mindestens 17 Spalten (bis Q)

def validate_ool_file(df: pd.DataFrame) -> bool:
    """
    Überprüft, ob die hochgeladene Datei die erwartete Struktur einer Open Order List hat.
    
    Args:
        df: DataFrame der Open Order List
        
    Returns:
        True, wenn die Datei gültig ist, sonst False
    """
    # Prüfen, ob die 'artikel no'-Spalte vorhanden ist
    return 'artikel no' in df.columns

def create_downloadable_excel(df: pd.DataFrame, highlight_indices: List[int] = None) -> str:
    """
    Erstellt eine herunterladbare Excel-Datei aus einem DataFrame mit optionaler Hervorhebung bestimmter Zeilen.
    
    Args:
        df: DataFrame, der exportiert werden soll
        highlight_indices: Liste von Zeilenindizes, die hervorgehoben werden sollen
        
    Returns:
        Base64-kodierter Excel-Inhalt
    """
    output = io.BytesIO()
    
    # Excel-Datei mit XlsxWriter erstellen (für Formatierung)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        # Format für die hervorzuhebenden Zeilen erstellen
        if highlight_indices:
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            
            # Zeilen hervorheben
            for idx in highlight_indices:
                # +1 für die Excel-Zeilennummerierung (beginnt bei 1) und +1 für Header
                row_idx = idx + 2
                # Alle Spalten hervorheben
                worksheet.set_row(row_idx, None, red_format)

    # In Base64 konvertieren für Download
    b64 = base64.b64encode(output.getvalue()).decode()
    return b64

def create_downloadable_summary(summary_data: List[Dict[str, Any]]) -> str:
    """
    Erstellt eine herunterladbare Excel-Datei mit der Zusammenfassung der gefundenen Übereinstimmungen.
    
    Args:
        summary_data: Liste von Dictionaries mit den Zusammenfassungsdaten
        
    Returns:
        Base64-kodierter Excel-Inhalt
    """
    # DataFrame aus den Zusammenfassungsdaten erstellen
    df = pd.DataFrame(summary_data)
    
    # Spaltenreihenfolge und Spaltenüberschriften anpassen
    if len(df) > 0:
        # Spalten umbenennen
        column_mapping = {
            'codice_full': 'Codice (vollständig)',
            'codice_base': 'Codice (Basis)',
            'artikelnummer': 'Artikelnummer',
            'lagerbestand': 'Lagerbestand',
            'kundenauftraege': 'Kundenaufträge',
            'monatlicher_verbrauch': 'Monatlicher Verbrauch',
            'gefunden_in_ool': 'In OOL gefunden'
        }
        df = df.rename(columns=column_mapping)
        
        # Spaltenreihenfolge definieren
        columns_order = [
            'Codice (vollständig)', 'Codice (Basis)', 'Artikelnummer', 
            'Lagerbestand', 'Kundenaufträge', 'Monatlicher Verbrauch', 
            'In OOL gefunden'
        ]
        
        # Spalten in der gewünschten Reihenfolge auswählen
        df = df[columns_order]
    
    # Excel-Datei erstellen
    output = io.BytesIO()
    df.to_excel(output, index=False)
    
    # In Base64 konvertieren für Download
    b64 = base64.b64encode(output.getvalue()).decode()
    return b64 