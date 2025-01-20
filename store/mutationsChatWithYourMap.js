import {generateSimpleMutations} from "../../../src/shared/js/utils/generators";
import stateChatWithYourMap from "./stateChatWithYourMap";

const mutations = {
    ...generateSimpleMutations(stateChatWithYourMap)

};

export default mutations;