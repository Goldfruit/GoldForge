<template>
    <section class="command-box">
      <h3>{{ command.name }}</h3>
      <p class="category">{{ command.category }}</p>
      <div class="cmd-line">
        <code class="the-command">{{ command.command }}</code>
        <button @click="copyCommand(command.command)">Kopieren</button>
      </div>
      <p class="desc">{{ command.description }}</p>
      <div class="info-icon" @mouseover="showInfo = true" @mouseleave="showInfo = false">
        ℹ
      </div>
      <div v-if="showInfo" class="tooltip">
        {{ command.info }}
      </div>
    </section>
  </template>
  
  <script>
  export default {
    name: "CommandItem",
    props: {
      command: Object
    },
    data() {
      return {
        showInfo: false
      };
    },
    methods: {
      copyCommand(str) {
        navigator.clipboard.writeText(str).then(() => {
          alert("Kopiert: " + str);
        });
      }
    }
  };
  </script>
  
  <style scoped>
  .command-box {
    position: relative;
    background: #fff;
    margin-bottom: 1rem;
    padding: 1rem;
    border-left: 5px solid #4caf50;
    border-radius: 3px;
  }
  .cmd-line {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  .category {
    font-size: 0.9rem;
    color: gray;
  }
  .the-command {
    background: #eee;
    padding: 0.25rem 0.5rem;
  }
  .info-icon {
    position: absolute;
    right: 1rem;
    top: 1rem;
    cursor: pointer;
    border: 1px solid #ccc;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    text-align: center;
    line-height: 20px;
    background: #fff;
    font-size: 14px;
  }
  .tooltip {
    position: absolute;
    right: 2.5rem;
    top: 1rem;
    background: #333;
    color: #fff;
    font-size: 0.9rem;
    padding: 0.5rem;
    border-radius: 5px;
    width: 200px;
  }
  </style>
  