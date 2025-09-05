# AdsPower Browser Manager

Ein Python-Skript zum Verwalten und Starten von AdsPower Browser-Profilen mit verschiedenen Proxy- und Cookie-Einstellungen.

## Funktionen

- ✅ Browser-Profile mit verschiedenen Proxy-Typen erstellen (HTTP, HTTPS, SOCKS5)
- ✅ Cookies zu Profilen hinzufügen
- ✅ Browser automatisch starten und stoppen
- ✅ Integration mit Selenium für Web-Automation
- ✅ Konfiguration über JSON-Dateien
- ✅ Einfache API für eigene Skripte

## Voraussetzungen

1. **AdsPower Browser** installiert und gestartet
2. **Python 3.7+** installiert
3. **ChromeDriver** für Selenium (falls Selenium verwendet wird)

## Installation

1. Repository klonen oder Dateien herunterladen
2. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

## Verwendung

### 1. Einfacher Browser-Launcher

Verwenden Sie `simple_browser_launcher.py` mit der `config.json`:

```bash
python simple_browser_launcher.py
```

### 2. Erweiterte Beispiele

Führen Sie das Hauptskript aus:

```bash
python adspower_browser_manager.py
```

### 3. Selenium-Integration

Verwenden Sie das Selenium-Beispiel:

```bash
python selenium_example.py
```

## Konfiguration

### config.json Format

```json
{
  "profiles": [
    {
      "name": "Profil-Name",
      "proxy": {
        "type": "http",
        "host": "proxy.example.com",
        "port": 8080,
        "username": "user",
        "password": "pass"
      },
      "cookies": [
        {
          "domain": ".example.com",
          "name": "cookie_name",
          "value": "cookie_value",
          "secure": true
        }
      ]
    }
  ]
}
```

### Proxy-Typen

- `http` - HTTP-Proxy
- `https` - HTTPS-Proxy  
- `socks5` - SOCKS5-Proxy

### Cookie-Parameter

- `domain` - Cookie-Domain (z.B. ".google.com")
- `name` - Cookie-Name
- `value` - Cookie-Wert
- `path` - Cookie-Pfad (optional, Standard: "/")
- `secure` - Sichere Cookies (optional, Standard: false)
- `http_only` - HTTP-Only Cookies (optional, Standard: false)
- `expires` - Ablaufzeit (optional)

## API-Verwendung

### Grundlegende Verwendung

```python
from adspower_browser_manager import AdsPowerManager, ProxyConfig, CookieConfig

# Manager erstellen
manager = AdsPowerManager()

# Proxy-Konfiguration
proxy = ProxyConfig(
    proxy_type="http",
    host="proxy.example.com",
    port=8080,
    username="user",
    password="pass"
)

# Profil erstellen
user_id = manager.create_profile("Mein-Profil", proxy)

# Cookies hinzufügen
cookies = [
    CookieConfig(
        domain=".google.com",
        name="NID",
        value="abc123",
        secure=True
    )
]
manager.add_cookies(user_id, cookies)

# Browser starten
debugger_address = manager.start_browser(user_id)

# Browser stoppen
manager.stop_browser(user_id)
```

### Selenium-Integration

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Chrome-Optionen für AdsPower
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", debugger_address)

# Driver erstellen
driver = webdriver.Chrome(options=chrome_options)

# Automation durchführen
driver.get("https://www.google.com")
# ... weitere Automation ...

# Aufräumen
driver.quit()
manager.stop_browser(user_id)
```

## Fehlerbehebung

### Häufige Probleme

1. **AdsPower nicht erreichbar**
   - Stellen Sie sicher, dass AdsPower gestartet ist
   - Überprüfen Sie die API-URL (Standard: `http://local.adspower.net:50325`)

2. **Proxy-Verbindung fehlschlägt**
   - Überprüfen Sie Proxy-Einstellungen
   - Testen Sie Proxy-Verbindung manuell

3. **Selenium-Fehler**
   - Installieren Sie ChromeDriver
   - Stellen Sie sicher, dass Chrome installiert ist

### Debug-Modus

Fügen Sie Debug-Ausgaben hinzu:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dateien

- `adspower_browser_manager.py` - Hauptklasse und API
- `simple_browser_launcher.py` - Einfacher Launcher mit JSON-Konfiguration
- `selenium_example.py` - Selenium-Integrationsbeispiel
- `config.json` - Beispiel-Konfigurationsdatei
- `requirements.txt` - Python-Abhängigkeiten

## Lizenz

Dieses Projekt ist für Bildungszwecke gedacht. Verwenden Sie es verantwortungsvoll und in Übereinstimmung mit den Nutzungsbedingungen von AdsPower.

## Support

Bei Problemen oder Fragen:
1. Überprüfen Sie die AdsPower-Dokumentation
2. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind
3. Überprüfen Sie die Konfigurationsdatei auf Syntaxfehler
