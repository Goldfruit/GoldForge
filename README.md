# Befehlsbibliothek mit Goldanker-Backend – Komplette README


Dieser Leitfaden vereint zwei Roadmaps (v1 und v2) zu einer umfassenden Dokumentation für deine Interaktive Befehlsbibliothek mit Anbindung an einen **Goldanker**-Microservice.

---

## 1. Architektur & Idee

### 1.1 Ziel
Eine **Progressive Web App (PWA)** zur **Verwaltung von Befehlen** (z. B. Docker-, Kubernetes-, Git-Befehle) mit
- **Zweiteiliger Oberfläche** (Bibliothek & Arbeitsfläche)
- **Drag & Drop**-Funktionalität
- **Kachel-Design**
- **Backend** (Goldanker CommandService, FastAPI oder Node.js)

### 1.2 Datenfluss
1. Frontend (Vue + Vite + PWA)
2. Backend (Goldanker_CommandService)
3. befehle.json (Serverseitige Ablage)
4. CI/CD (GitHub Actions / GitLab)

---

## 2. Funktionale Übersicht

### 2.1 Zweiteilige Oberfläche
- **Bibliothek (links):**
  - Alle Befehle kategorisiert (Git, Docker, usw.)
  - Suchfeld, um rasch Befehle zu finden
- **Arbeitsfläche (rechts):**
  - Kachel-Design
  - Drag & Drop: Befehle aus Bibliothek in Arbeitsfläche schieben
  - X-Button zum Entfernen

### 2.2 Kachel-Design
- Enthält:
  - **Name**, **Beschreibung**, **Command**
  - Optionale Infos, Tooltips
- Resizable (per CSS-Resize) & frei platzierbar

### 2.3 Drag & Drop
- Nutzung von [vue-draggable-next](https://github.com/SortableJS/vue.draggable.next)
  - `v-model`-Synchronisierung
  - Optional: Reordering in Bibliothek oder Arbeitsfläche
- Alternativ: manuelles Drag & Drop (Events `dragstart`, `dragend`)

### 2.4 Persistenz
- **Frontend**: localStorage
  - Speichert Position und Größe der Kacheln
- **Backend**: befehle.json
  - Speichert Befehle, Kategorien, Beschreibungen

### 2.5 JSON-Struktur
- `name`, `command`, `category`, `description`, `info`

```json
[
  {
    "name": "Docker Build",
    "command": "docker-compose up --build",
    "category": "Docker",
    "description": "Container neu bauen und starten",
    "info": "Nach Änderungen oder Cache-Problemen."
  },
  {
    "name": "Kubernetes Pods anzeigen",
    "command": "kubectl get pods",
    "category": "Kubernetes",
    "description": "Zeigt aktuell laufende Pods an",
    "info": "Hilfreich für schnellen Überblick der Container."
  }
]
```

---

## 3. Goldanker CommandService (Beispiel in FastAPI)

### 3.1 Aufbau
```
goldanker_commands/
 ├── Dockerfile
 ├── requirements.txt
 ├── main.py           <-- FastAPI-Code
 ├── befehle.json      <-- Serverseitig gespeichert
 └── ...
```

### 3.2 Dockerfile
```Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.3 main.py (CRUD-Endpunkte)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI()

JSON_FILE = os.getenv("COMMANDS_JSON_PATH", "./befehle.json")

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
    return load_commands()

@app.post("/commands", response_model=Command)
def create_command(new_cmd: Command):
    commands = load_commands()
    # Optional: check duplicates
    commands.append(new_cmd)
    save_commands(commands)
    return new_cmd

@app.put("/commands/{cmd_name}", response_model=Command)
def update_command(cmd_name: str, updated_cmd: Command):
    commands = load_commands()
    for i, c in enumerate(commands):
        if c.name == cmd_name:
            commands[i] = updated_cmd
            save_commands(commands)
            return updated_cmd
    raise HTTPException(status_code=404, detail="Command not found")

@app.delete("/commands/{cmd_name}")
def delete_command(cmd_name: str):
    commands = load_commands()
    filtered = [c for c in commands if c.name != cmd_name]
    if len(filtered) == len(commands):
        raise HTTPException(status_code=404, detail="Command not found")
    save_commands(filtered)
    return {"message": f"Befehl '{cmd_name}' gelöscht"}
```

### 3.4 Docker-Compose Integration
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
    # depends_on, networks, etc.
```

---

## 4. Vue-Frontend (Befehlsbibliothek)

### 4.1 Struktur
```
befehlsbibliothek/
 ├── src/
 │   ├── App.vue
 │   ├── main.js
 │   └── assets/
 │       └── styles.css
 ├── public/
 ├── vite.config.js
 ├── package.json
 └── ...
```

### 4.2 App.vue (Beispiel mit vue-draggable-next)
```html
<template>
  <div class="app-layout">
    <!-- Linke Seite (Bibliothek) -->
    <div class="left-panel">
      <h2>Bibliothek</h2>
      <input type="text" v-model="searchQuery" placeholder="Befehle durchsuchen..." />

      <div v-for="cmd in filteredCommands" :key="cmd.name" class="library-item">
        <div>{{ cmd.name }} ({{ cmd.category }})</div>
        <button @click="addToWorkspace(cmd)">→</button>
      </div>
    </div>

    <!-- Rechte Seite (Arbeitsfläche) -->
    <div class="right-panel">
      <h2>Arbeitsfläche</h2>

      <draggable v-model="workspace" class="workspace" @end="onDragEnd">
        <transition-group>
          <div
            v-for="(cmd, idx) in workspace"
            :key="cmd.name"
            class="command-box"
            :style="{
              position: 'relative',
              marginBottom: '1rem',
              // Optional: you could store x/y for absolute positioning,
              // but Draggable handles basic re-order by default
            }"
          >
            <h3>{{ cmd.name }}</h3>
            <p>{{ cmd.description }}</p>
            <code>{{ cmd.command }}</code>
            <button @click="removeFromWorkspace(idx)">X</button>
          </div>
        </transition-group>
      </draggable>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import Draggable from 'vuedraggable'

export default {
  components: {
    Draggable,
  },
  setup() {
    const commands = ref([])
    const workspace = ref([])
    const searchQuery = ref('')

    // 1) Commands laden
    const loadCommands = async () => {
      const res = await fetch('http://localhost:8000/commands')
      const data = await res.json()
      commands.value = data
    }

    // 2) Filter
    const filteredCommands = computed(() => {
      if (!searchQuery.value) return commands.value
      return commands.value.filter((cmd) =>
        cmd.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        cmd.category.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    })

    // 3) Hinzufügen zur Arbeitsfläche
    const addToWorkspace = (cmd) => {
      // Minimale Kopie, evtl. mit default Position
      workspace.value.push({ ...cmd })
      saveWorkspace()
    }

    // 4) Entfernen von Arbeitsfläche
    const removeFromWorkspace = (idx) => {
      workspace.value.splice(idx, 1)
      saveWorkspace()
    }

    // 5) onDragEnd
    const onDragEnd = () => {
      // Speichere Reihenfolge
      saveWorkspace()
    }

    // 6) localStorage persist
    const saveWorkspace = () => {
      localStorage.setItem('workspace', JSON.stringify(workspace.value))
    }
    const loadWorkspaceLocal = () => {
      const saved = localStorage.getItem('workspace')
      if (saved) {
        workspace.value = JSON.parse(saved)
      }
    }

    onMounted(() => {
      loadCommands()
      loadWorkspaceLocal()
    })

    return {
      commands,
      workspace,
      searchQuery,
      filteredCommands,
      addToWorkspace,
      removeFromWorkspace,
      onDragEnd,
    }
  },
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
  padding: 1rem;
}
.workspace {
  min-height: 400px;
  background: #e0e0e0;
  padding: 1rem;
  border: 2px dashed #ccc;
}
.command-box {
  background: white;
  border: 2px solid #ccc;
  padding: 1rem;
  margin-bottom: 1rem;
  transition: transform 0.2s ease;
}
.command-box:hover {
  transform: translateY(-4px);
}
</style>
```

---

## 5. Kategorien & Struktur

Hier einige sinnvolle Kategorien (erweiterbar):

```yaml
- Git
- Docker
- npm & Node.js
- Ubuntu & Linux
- Kubernetes & Helm
- Kafka
- Istio
- Helm
- Prometheus
- Grafana
- CI/CD (GitLab)
- Python
- Sicherheit & VPN
- IPFS
```

---

## 6. CI/CD und Deployment

1. **Backend**: Docker build/push
2. **Frontend**: `npm run build`, deploy nach GitHub Pages oder Docker-Container + Nginx
3. **Docker-Compose**: orchestriert Services (goldanker_commands + befehlsbibliothek)
4. **GitHub Actions / GitLab-CI**: automatisiertes Bauen und Ausrollen

---

## 7. Erweiterungsideen

- **Command-Eingabemaske** (POST /commands)
- **Edit-Funktion** (PUT /commands/{cmd_name})
- **Git-Commit-Hook** nach Speichern
- **Nutzer-/Rollenverwaltung**
- **Tooltip**-Infos mit Tippy.js
- **Responsive** für Mobile/Tablet

---

## 8. Fazit

Mit dieser kombinierten README hast du:
1. Eine **Architektur-Beschreibung** (Backend/Frontend)
2. **Konkrete Codebeispiele** (FastAPI + Vue)
3. **Einen klaren Projektplan** (Phasen, Tools, Docker-Setup)
4. **Optionale Features** (Git-Commit-Hooks, CI/CD, etc.)befehlsbibliothek/