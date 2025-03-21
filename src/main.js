import { createApp } from "vue";
import App from "./App.vue";

// (PWA) Service Worker Registrieren:
import { registerSW } from "virtual:pwa-register";
registerSW({ immediate: true });

createApp(App).mount("#app");
