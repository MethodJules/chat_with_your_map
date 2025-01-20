import {generateSimpleGetters} from "../../../src/shared/js/utils/generators";
import stateChatWithYourMap from "./stateChatWithYourMap";

const getters = {
    ...generateSimpleGetters(stateChatWithYourMap)
};

export default getters;