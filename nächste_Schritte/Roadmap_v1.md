Hier kommt ein **komplettes Grob-Konzept** für deine **Interaktive Befehlsbibliothek** mit **Goldanker** als Backend. Wir kombinieren:

1. **Vue-Frontend** (Zweiteiliger Aufbau: Bibliothek links, Arbeitsfläche rechts, Drag & Drop, Persistenz)
2. **Goldanker-Backend (FastAPI)** als eigenen Microservice für Befehlsverwaltung (CRUD auf befehle.json)
3. **Deployment** via Docker Compose oder Kubernetes
4. **CI/CD** (z. B. GitLab oder GitHub Actions) zur automatischen Ausrollung

Ich zeige dir im Folgenden die **Architektur**, den **Datenfluss** und anschließend **Code-Beispiele** für Frontend (Vue) und Backend (FastAPI).

---

## 1. **Architekturüberblick**

```plaintext
          +------------------------+
          |   Befehlsbibliothek   | (Vue Frontend)
          |  (Linke Spalte/Liste) |
          |  (Rechte Spalte/Kacheln)       
          +-----------+------------+
                      |
                      |  HTTPS/REST (fetch JSON, create/update commands)
                      v
     +---------------------------------+
     |  Goldanker_CommandService (API) | (FastAPI)
     |---------------------------------|
     |  /commands GET/POST/DELETE/...  |
     |  JSON-Datei: befehle.json       |
     |  GitHub push/commit (optional)  |
     +---------------------------------+
                      |
                 Docker Compose / k8s
                      |
                +------------+
                |  CI/CD     |
                +------------+
```

- **Frontend** (Befehlsbibliothek) zeigt alle Befehle aus `/commands` an (kategorisiert, suchbar).
- **Arbeitsfläche**: Befehlskarten werden per Drag & Drop rübergezogen.  
  - Layout und Positionen in **localStorage** (damit der State auf dem selben Gerät bestehen bleibt).
- **Backend** (Goldanker_CommandService) speichert die Befehle in `befehle.json`.  
  - Bietet Endpunkte für **Neueinträge** (POST), **Änderungen** (PUT) und **Löschen** (DELETE).
  - **Optional**: Bei jedem API-Update kann das Backend selbst einen Commit ins Git-Repo machen, sodass `befehle.json` versioniert bleibt.
- **CI/CD**: Pullt den Code (inkl. aktualisierter `befehle.json`) und deployed das Ganze.

---

## 2. **Backend: Goldanker_CommandService (FastAPI) Beispiel**

### Verzeichnisstruktur (vereinfacht)

```
goldanker_commands/
 ├── Dockerfile
 ├── requirements.txt
 ├── main.py           <-- Hier steckt unser FastAPI-Code
 ├── befehle.json      <-- Liegt hier oder in einem Volume
 └── ...
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### requirements.txt

```txt
fastapi
uvicorn
```

### main.py (zentraler FastAPI-Code)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI()

# Pfad zur JSON-Datei (evtl. anpassbar per ENV)
JSON_FILE = os.getenv("COMMANDS_JSON_PATH", "./befehle.json")

# Pydantic-Modell für Befehle
class Command(BaseModel):
    name: str
    command: str
    category: str
    description: Optional[str] = None
    info: Optional[str] = None

def load_commands() -> List[Command]:
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Command(**cmd) for cmd in data]

def save_commands(commands: List[Command]):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump([cmd.dict() for cmd in commands], f, indent=2, ensure_ascii=False)

@app.get("/commands", response_model=List[Command])
def get_commands():
    """Liste aller Befehle zurückgeben"""
    return load_commands()

@app.post("/commands", response_model=Command)
def create_command(new_cmd: Command):
    """Neuen Befehl erstellen"""
    commands = load_commands()
    # Optional: prüfen, ob Name schon existiert
    commands.append(new_cmd)
    save_commands(commands)
    return new_cmd

@app.put("/commands/{cmd_name}", response_model=Command)
def update_command(cmd_name: str, updated_cmd: Command):
    """Befehl aktualisieren"""
    commands = load_commands()
    for i, c in enumerate(commands):
        if c.name == cmd_name:
            commands[i] = updated_cmd
            save_commands(commands)
            return updated_cmd
    raise HTTPException(status_code=404, detail="Command not found")

@app.delete("/commands/{cmd_name}")
def delete_command(cmd_name: str):
    """Befehl löschen"""
    commands = load_commands()
    filtered = [c for c in commands if c.name != cmd_name]
    if len(filtered) == len(commands):
        raise HTTPException(status_code=404, detail="Command not found")
    save_commands(filtered)
    return {"message": f"Befehl '{cmd_name}' gelöscht"}

```

> **Optional**: Du könntest hier Hooks einbauen, die nach jedem Schreibzugriff (`save_commands`) einen **Git-Commit** anstoßen (z. B. per `subprocess` oder GitHub-API), um die aktualisierte `befehle.json` ins Repo zu pushen.

---

## 3. **Docker-Compose Integration**

In deiner übergeordneten `docker-compose.yaml` kannst du den neuen Service einbinden:

```yaml
version: '3.8'
services:
  goldanker_commands:
    build: ./goldanker_commands
    container_name: goldanker_commands
    environment:
      - COMMANDS_JSON_PATH=/app/befehle.json
    volumes:
      - ./goldanker_commands/befehle.json:/app/befehle.json
    ports:
      - "8000:8000"
    # depends_on, networks, etc. je nach Bedarf
```

Andere Goldanker-Services (north, east, west …) kannst du in der Compose-Datei genauso auflisten. So läuft dein CommandService auf Port 8000 und ist erreichbar über `http://localhost:8000/commands`.

---

## 4. **Frontend: Befehlsbibliothek (Vue)**

### 4.1 Grober Aufbau

- **Linke Seite**: Liste / Suchfeld / Kategorien-Filter
- **Rechte Seite**: Arbeitsfläche (Drag & Drop, Kachel-Layout)

#### Beispiel-Hauptkomponente (App.vue)

```html
<template>
  <div class="app-layout">
    <!-- Linke Seite (Bibliothek) -->
    <div class="left-panel">
      <h2>Bibliothek</h2>
      <input type="text" v-model="searchQuery" placeholder="Befehle durchsuchen..."/>

      <div v-for="cmd in filteredCommands" :key="cmd.name" class="library-item">
        <div>{{ cmd.name }} ({{ cmd.category }})</div>
        <button @click="addToWorkspace(cmd)">→</button>
      </div>
    </div>

    <!-- Rechte Seite (Arbeitsfläche) -->
    <div class="right-panel">
      <h2>Arbeitsfläche</h2>
      <div
        v-for="(cmd, idx) in workspace"
        :key="cmd.name"
        class="command-box"
        :style="{ position: 'absolute', left: cmd.x + 'px', top: cmd.y + 'px' }"
        draggable="true"
        @dragstart="dragStart($event, idx)"
        @dragend="dragEnd($event, idx)"
      >
        <h3>{{ cmd.name }}</h3>
        <p>{{ cmd.description }}</p>
        <code>{{ cmd.command }}</code>
        <button @click="removeFromWorkspace(idx)">X</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  setup() {
    const commands = ref([])
    const workspace = ref([])     // Hier liegen die Kacheln (mit Koordinaten)
    const searchQuery = ref('')

    // 1) Commands per API laden
    const loadCommands = async () => {
      const res = await fetch('http://localhost:8000/commands')
      const data = await res.json()
      commands.value = data
    }

    // 2) Filter-Funktion
    const filteredCommands = computed(() => {
      if (!searchQuery.value) return commands.value
      return commands.value.filter(cmd => 
        cmd.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        cmd.category.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    })

    // 3) Befehl auf Arbeitsfläche legen
    const addToWorkspace = (cmd) => {
      // Standardposition / Minimale Kopie
      workspace.value.push({ ...cmd, x: 50, y: 50 })
      saveWorkspace()
    }

    // 4) Kachel von Arbeitsfläche entfernen
    const removeFromWorkspace = (idx) => {
      workspace.value.splice(idx, 1)
      saveWorkspace()
    }

    // 5) Drag & Drop (einfache Variante)
    let currentIndex = null
    const dragStart = (evt, idx) => {
      currentIndex = idx
    }
    const dragEnd = (evt, idx) => {
      const x = evt.pageX
      const y = evt.pageY
      workspace.value[idx].x = x
      workspace.value[idx].y = y
      saveWorkspace()
      currentIndex = null
    }

    // 6) Persistenz in localStorage
    const saveWorkspace = () => {
      localStorage.setItem('workspace', JSON.stringify(workspace.value))
    }
    const loadWorkspace = () => {
      const saved = localStorage.getItem('workspace')
      if (saved) {
        workspace.value = JSON.parse(saved)
      }
    }

    // Lifecycle
    onMounted(() => {
      loadCommands()
      loadWorkspace()
    })

    return {
      commands,
      workspace,
      searchQuery,
      filteredCommands,
      addToWorkspace,
      removeFromWorkspace,
      dragStart,
      dragEnd
    }
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
}
.left-panel {
  width: 300px;
  background: #fff;
  padding: 1rem;
  overflow-y: auto;
}
.right-panel {
  flex: 1;
  position: relative;
  background: #f5f5f5;
  overflow: hidden;
}
.command-box {
  width: 200px;
  height: auto;
  background: white;
  border: 2px solid #ccc;
  cursor: move;
  padding: 1rem;
}
</style>
```

**Erläuterungen:**
- **`loadCommands()`** ruft unsere FastAPI auf `http://localhost:8000/commands` ab.
- Wir speichern alle Befehle in `commands.value`.
- Suchfeld filtert `commands.value` → `filteredCommands`.
- Button → `addToWorkspace(cmd)`, was in `workspace.value` landet.
- Kachel hat `draggable="true"` → wir fangen `@dragstart` und `@dragend` ab und passen x/y-Position an.
- `saveWorkspace()` & `loadWorkspace()` legen den Kachel-Status in `localStorage` ab.

*(Dies ist ein Minimalbeispiel – du kannst natürlich **vue-draggable-next** oder **Vue Draggable** nehmen, um echtes Drag & Drop bequemer zu machen.)*

---

## 5. **Kategorien-Struktur**

Im Backend hast du das Feld `category`. Im Frontend kannst du:

- Ein Dropdown oder Filter für Kategorien erstellen.
- Einen eigenen Endpunkt `/categories` machen, falls du willst, oder die Kategorien aus `commands` ableiten (`unique`).

Beispiel: 
```js
const categories = computed(() => {
  const allCats = commands.value.map(c => c.category)
  return [...new Set(allCats)]
})
```

---

## 6. **CI/CD & Deployment**

1. **Backend** (goldanker_commands):  
   - Kompiliere es über Docker: `docker build -t goldanker_commands .`  
   - Evtl. in dein GitLab/GitHub-Repo pushen.  
   - GitLab-CI kann es automatisiert bauen und auf deinen Server pushen.

2. **Frontend** (Befehlsbibliothek):  
   - `npm run build` → `dist`  
   - Deploy via GitHub Pages oder auf denselben Server.  
   - Oder über Docker + Nginx-Container bereitstellen.

3. **Docker-Compose**  
   - Eine zentrale Compose-Datei enthält alle Services:  
     ```yaml
     services:
       goldanker_commands:
         # ...
       befehlsbibliothek:
         build: ./befehlsbibliothek
         ports:
           - "8080:80"
         # ...
     ```
   - Dann: `docker-compose up -d`  
   - Frontend ist erreichbar unter `http://localhost:8080`, Backend unter `http://localhost:8000`

---

## 7. **Optionale Features**

- **Command-Eingabemaske** im Frontend:  
  - Ein Formular, das POST `/commands` aufruft, um neue Befehle zu erstellen.
- **Edit-Funktion** pro Kachel → PUT `/commands/{cmd_name}`.
- **Git-Commit-Hook** nach jedem `save_commands()` – so bleiben deine Befehle versioniert.
- **Benutzer-/Rollenverwaltung**: Absichern, dass nur berechtigte User neue Befehle anlegen können.
- **Tooltips (Tippy.js)** für Zusatzinfos (z. B. `info`-Feld in der JSON).
- **Responsive Layout** für Mobile & Tablet.

---

## 8. **Zusammenfassung**

Mit diesem Ansatz hast du:

1. **Modularität**: Ein **Goldanker_CommandService**-Microservice, der Befehle verwaltet (CRUD).
2. **Ein Vue-Frontend** (Befehlsbibliothek) mit **Drag & Drop**-Arbeitsfläche, in der du Kacheln frei anordnen kannst.
3. **Persistenz**:  
   - Kachel-Position und Layout in `localStorage`.  
   - Befehlsdaten in `befehle.json` (serverseitig).
4. **Deployment**: Alles in Docker-Containern, orchestriert via **docker-compose** (oder Kubernetes).  
5. **CI/CD**: Du kannst bei jeder Änderung an `befehle.json` (oder an den Code-Dateien) automatisiert builden & deployen.

Diese Lösung lässt sich beliebig erweitern, z. B. um Slack-Benachrichtigungen, automatisches **Git-Commit** oder Integration in dein Triangel-Setup (north/east/west) – je nachdem, wie du es in dein Goldanker-Ökosystem einbetten willst.

---

### Fertig! 

Damit hast du eine **vollständige Blaupause** für deine interaktive Befehlsbibliothek:  
- **Zweiteilige Oberfläche** (Liste links, Arbeitsfläche rechts),  
- **Kachel-Design** mit Draggable,  
- **Persistenz** (localStorage + FastAPI-JSON),  
- **Kategorien** als Teil des JSON,  
- **Goldanker** als schlanker Backend-Service,  
- **Optionale** CI/CD-Anbindung mit automatischem Deployment.

Viel Erfolg bei der Umsetzung! Wenn du weitere Fragen hast oder spezielle Code-Snippets brauchst, sag einfach Bescheid.