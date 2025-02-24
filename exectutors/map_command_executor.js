import { mapActions, mapMutations} from 'vuex';

/**
 *
 */
export class MapCommandExecutor {
    /**
     *
     */
    constructor (store) {
        this.store = store;

        // Bind Vuex actions to the instance
        const mapActions = {
            setCenter: (payload) => store.dispatch('Maps/setCenter', payload),
            setZoom: (level) => store.dispatch('Maps/setZoom', level),
            placingPointMarker: (point) => store.dispatch('Maps/placingPointMarker', point),
            addLayer: (layer) => store.dispatch('Maps/addLayer', layer),
            changeCurrentComponent: (component) => store.dispatch('Menu/changeCurrentComponent', component),
        };
        
        // Bind mutations
        const mapMutations = {
            setExpandedBySide: (payload) => store.commit('Menu/setExpandedBySide', payload)
        };

        // Attach actions and mutations to instance
        Object.assign(this, mapActions, mapMutations);

        this.commandPatterns = { // TODO: Muss eigentlich an ein LLM geschickt werdne und der key dann zurückgegeben
            zoom: /(?:zeige|zoom|zeig)\s+(?:mir\s+)?(?:das\s+)?(?:gebiet|bereich|area)\s+(?:von\s+)?(\w+)/i,
            layer: /(?:zeige|aktiviere)\s+(?:mir\s+)?(?:die\s+)?(\w+)/i,
            measure: /(?:messe|miss|berechne)\s+(?:die\s+)?(?:distanz|entfernung|strecke)/i,
            coordinate: /(?:öffne|zeige|aktiviere)\s+(?:mir\s+)?(?:das\s+)?koordinaten\s*werkzeug/i
        };
    }

    /**
     *
     */
    async executeCommand (command) {
        console.log(command)
        try {
            // Parse the command
            const action = this.parseCommand(command);
            console.log(action)

            if (!action) {
                return {
                    success: false,
                    message: "Entschuldigung, ich konnte den Befehl nicht verstehen."
                };
            }

            // execute the corresponding action
            await this.executeAction(action);

            return {
                success: true,
                message: `Aktion '${action.type} wurde ausgeführt.`,
                action: action
            };
        }
        catch (error) {
            console.error("Error execution command:", error);
            return {
                success: false,
                message: "Es gab einen Fehler bei der Ausführung des Befehls"
            };
        }
    }

    /**
     *
     */
    parseCommand (command) {
        // check for zoom command
        const zoomMatch = command.match(this.commandPatterns.zoom);

        if (zoomMatch) {
            return {
                type: "zoom",
                area: zoomMatch[1]
            };
        }

        // check for layer command
        // eslint-disable-next-line one-var
        const layerMatch = command.match(this.commandPatterns.layer);

        if (layerMatch) {
            return {
                type: "layer",
                layerName: layerMatch[1]
            };
        }

        // check for measure command
        // eslint-disable-next-line one-var
        const measureMatch = command.match(this.commandPatterns.measure);

        if (measureMatch) {
            return {
                type: "measure"
            };
        }

        // check for coordinate toolkit
        // eslint-disable-next-line one-var
        const coordMatch = command.match(this.commandPatterns.coordinate);

        if (coordMatch) {
            return {
                type: "coordinate"
            };
        }

        return null;
    }

    /**
     *
     */
    async executeAction (action) {
        switch (action.type) {
            case "zoom":
                await this.handleZoom(action.area);
                break;
            case "layer":
                await this.handleLayer(action.layerName);
                break;
            case "measure":
                await this.handleMeasure();
                break;
            case "coordinate":
                await this.handleCoordinateToolkit();
                break;
            default:
                throw new Error("Unbekannte Aktion");
        }
    }

    /**
     *
     */
    async handleZoom () {
        // Here we would integrate with your GeoJSON endpoint
        const coordinates = [562778.98, 5935272.29];
        // Coordinates 562778.98|5935272.29

        this.setCenter(coordinates); // Set the center of the Map
        this.setZoom(5);
        await this.setZoom(5);
        // Implement zoom logic using the GeoJSON data
    }

    async handleLayer(layerName) {
        // Implement layer activation logic
        // This would need to integrate with your layer management system
    }

    async handleMeasure() {
        // Implement measure tool activation
    }

    async handleCoordinateToolkit() {
        this.store.dispatch("Menu/changeCurrentComponent", {
            type: "coordToolkit",
            side: "secondaryMenu",
            props: {
                name: "coordToolkit"
            }
        });

        this.store.commit("Menu/setExpandedBySide", {
            expanded: true,
            side: "secondaryMenu"
        });
    }

    async fetchAreaData(area) {
        // Implement GeoJSON fetching from your urban data platform
        // Return the GeoJSON data for the specified area
    }
}
