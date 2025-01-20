import deLocale from "./locales/de/additional.json";
import enLocale from "./locales/en/additional.json";
import ChatWithYourMap from "./components/ChatWithYourMap.vue";
import chatWithYourStore from "./store/indexChatWithYourMap";

export default {
    component: ChatWithYourMap,
    store: chatWithYourStore,
    locales: {
        de: deLocale,
        en: enLocale
    }
};