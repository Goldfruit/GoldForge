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