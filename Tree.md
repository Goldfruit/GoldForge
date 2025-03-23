befehlsbibliothek/
├── .github/
│   └── workflows/
│       └── deploy.yml        # GitHub Actions Workflow für Deployment
├── public/
│   └── vite.svg
├── src/
│   ├── assets/
│   │   └── styles.css        # Globale CSS-Datei
│   ├── components/
│   │   └── CommandItem.vue
│   ├── data/
│   │   └── befehle.json      # Beispiel-Befehlsdaten
│   ├── App.vue
│   └── main.js
├── goldanker_commands/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py           <-- FastAPI-Code
│   ├── befehle.json      <-- Serverseitig gespeichert
│   └── ...
├── .gitignore
├── index.html
├── package.json
├── README.md
└── vite.config.js