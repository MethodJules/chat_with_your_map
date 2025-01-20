import getters from "./gettersChatWithYourMap";
import mutations from "./mutationsChatWithYourMap";
import state from "./stateChatWithYourMap";

export default {
    namespace: true,
    state: {...state},
    mutations,
    getters
}