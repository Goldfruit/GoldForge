<template>
  <main>
    <h1>Befehlsbibliothek</h1>
    <CommandItem
      v-for="(cmd, idx) in commands"
      :key="idx"
      :command="cmd"
    />
  </main>
</template>

<script>
import CommandItem from "./components/CommandItem.vue";
import commands from "./data/befehle.json";

export default {
  name: "App",
  components: {
    CommandItem
  },
  data() {
    return {
      commands
    };
  }
};
</script>

<style src="./assets/styles.css"></style>
