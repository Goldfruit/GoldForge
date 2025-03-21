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
  components: { CommandItem },
  data() {
    return {
      commands
    };
  }
};
</script>

<style>
main {
  margin: 0 auto;
  max-width: 800px;
  padding: 2rem;
  font-family: sans-serif;
}
h1 {
  text-align: center;
  margin-bottom: 2rem;
}
</style>
