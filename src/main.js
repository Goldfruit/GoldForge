import { createApp } from 'vue';
import App from './App.vue';

// (PWA) Service Worker registrieren:
import { registerSW } from 'virtual:pwa-register';
registerSW({ immediate: true });

// Vue Tippy-Plugin:
import VueTippy from 'vue-tippy';
import 'tippy.js/dist/tippy.css';
import 'tippy.js/animations/scale.css';

// App erstellen und konfigurieren:
const app = createApp(App);

app.use(VueTippy, {
  directive: 'tippy',            // => v-tippy (Direktivenname)
  component: 'tippy',            // => <tippy /> (Komponentenname)
  componentSingleton: 'tippy-singleton',
  defaultProps: {
    placement: 'top',
    allowHTML: true,
    animation: 'scale',
    theme: 'light-border'
  }
});

app.mount('#app');
