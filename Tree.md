befehlsbibliothek/
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions Workflow: automatisches Deployment auf GitHub Pages
├── public/
│   └── vite.svg               # Platzhalter-/Standard-Icon für die App
├── src/
│   ├── assets/
│   │   └── styles.css         # Globale CSS-Stile inkl. Farbverläufe, Schriftarten, Kachel-Design
│   ├── components/
│   │   └── CommandItem.vue    # Einzelne Befehlskachel-Komponente (Darstellung + Interaktion)
│   ├── data/
│   │   └── befehle.json       # Alle Befehle als JSON (Frontend-Ansicht)
│   ├── App.vue                # Haupt-Vue-Komponente mit Layout (Bibliothek & Arbeitsfläche)
│   └── main.js                # Einstiegspunkt für Vue-App, Registrierung von Plugins (Tippy, PWA)
├── goldanker_commands/
│   ├── Dockerfile             # Build-Anleitung für den FastAPI-Microservice (Backend)
│   ├── requirements.txt       # Python-Abhängigkeiten für FastAPI (Backend)
│   ├── main.py                # FastAPI-Backend (CRUD-API für befehle.json)
│   ├── befehle.json           # Serverseitig gespeicherte Befehle (wird von der API genutzt)
│   └── ...                    # Weitere Backend-Dateien (optional erweiterbar)
├── .gitignore                 # Git-Ignore-Regeln (z. B. node_modules, dist, etc.)
├── index.html                 # HTML-Startpunkt der App, lädt Vue & registriert PWA
├── package.json               # Node.js-Projektkonfiguration: Abhängigkeiten, Scripts etc.
├── README.md                  # Projektbeschreibung, Setup-Anleitung und Funktionsübersicht
└── vite.config.js             # Vite-Konfiguration (inkl. PWA-Plugin, Pfadoptionen)
