<script>
import {mapActions, mapMutations} from "vuex";
import {Vector as VectorLayer} from "ol/layer";
import {Vector as VectorSource} from "ol/source";
import {Feature} from "ol";
import Polygon from "ol/geom/Polygon";
import {Fill, Stroke, Style} from "ol/style";
import ChatWidget from "./ChatWidget.vue";
import layerCollection from "../../../src/core/layers/js/layerCollection";
export default {
    name: "ChatWithYourMap",
    components: {
        ChatWidget
    },
    data () {
        return {
            isProcessing: false,
            lastCommand: null,
            commandHistory: []
        };
    },
    methods: {
        ...mapActions("Maps", ["setCenter", "setZoom", "placingPointMarker", "addLayer"]),
        ...mapActions("Menu", ["changeCurrentComponent"]),
        ...mapActions("Modules/LayerSelection", ["changeVisibility"]),
        ...mapMutations("Menu", ["setExpandedBySide"]),

        /**
         * Main method to execute map commands from json
         */
        executeMapCommand (commandJson) {
            try {
                this.isProcessing = true;
                console.log("Executing command: ", commandJson);

                // Store command in history
                this.commandHistory.push({
                    ...commandJson,
                    executedAt: new Date().toISOString()
                });

                const {command} = commandJson;

                // Execute action based on type
                switch (command.action.type.toLowerCase()) {
                    case "zeigen":
                        this.executeShowCommand(command);
                        break;
                    case "navigieren":
                        this.navigateToLocation(command);
                        break;
                    case "filter":
                        this.executeFilterCommand(command);
                        break;
                    case "öffne":
                        this.executeToolCoommand(command);
                        break;
                    default:
                        console.warn(`Unknown action type: ${command.action.type}`);
                        break;
                }

                this.lastCommandId = commandJson.metadata.requestId;
            }
            catch (error) {
                console.error("Error executing map command", error);
                throw error;
            }
            finally {
                this.isProcessing = false;
            }
        },

        /**
         * Execute show commands
         */
        executeShowCommand (command) {
            // Handle location navigation
            if (command.location) {
                this.navigateToLocation(command.location, command.options);
            }

            // Handle layer visibility
            if (command.layer) {
                this.handleLayerVisibilty(command.layer, true);
            }
        },

        /**
         * Execute open tool commands
         */
        executeToolCoommand (command) {
            if (!command.tool) {
                return;
            }

            this.changeCurrentComponent({
                type: command.tool.tool,
                side: command.tool.side,
                props: command.tool.props
            });

            // Set expanded state if provided
            if (command.options?.expanded) {
                this.setExpandedBySide({
                    side: command.tool.side || "left",
                    expanded: command.options.expanded
                });
            }

            console.log(`Opened tool: ${command.tool.name}`);
        },
        /**
         * Navigate to a specific location
         */
        navigateToLocation (location, options = {}) {
            console.log(`Navigating to location: ${location.name}`);
            if (!location.coordinates) {
                return;
            }

            const {center, boundingBox} = location.coordinates;

            // Set map center
            if (center) {
                this.setCenter(center);
                console.log(`Navigated to:  ${location.name} at coordinates [${center.join(", ")}]`);
            }

            // Set zoom level
            if (options.zoom) {
                this.setZoom(options.zoom);
            }

            // Add marker if requested
            if (options.addMarker && center) {
                this.placingPointMarker(center);
            }

            // Create bounding box polygon if available
            if (boundingBox && options.highlight) {
                this.createBoundingBoxPolygon(boundingBox, options.style);
            }
        },

        /**
         * Handle layer visibility changes
         */
        handleLayerVisibilty (layer, visible = true) {
            if (layer.id) {
                this.changeVisibility({
                    layerId: layer.id,
                    value: visible
                });
                console.log(`Layer ${layer.name} (${layer.id}) visibility set to ${visible}`);
            }
        },

        /**
         * Apply filters to a layer
         */
        async applyFilters (layer, filters) {
            if (!layer?.id) {
                return;
            }

            const targetLayer = layerCollection.getLayerById(layer.id);

            if (!targetLayer) {
                console.warn(`Layer with ID ${layer.id} not found`);
                return;
            }

            console.log(`Applying ${filters.length} filter(s) to layer ${layer.name}`);

            // Get all feature from the layer
            // eslint-disable-next-line
            const features = targetLayer.layerSource.getFeatures();

            // Apply each filter
            features.forEach(feature => {
                let shouldShow = true;

                filters.forEach(filter => {
                    const featureValue = feature.get(filter.property);

                    switch (filter.operator) {
                        case "greaterThan":
                            shouldShow = shouldShow && (featureValue > filter.value);
                            break;
                        case "lessThan":
                            shouldShow = shouldShow && (featureValue > filter.value);
                            break;
                        case "equals":
                            shouldShow = shouldShow && (featureValue === filter.value);
                            break;
                        case "contains":
                            shouldShow = shouldShow && String(featureValue).includes(filter.value);
                            break;
                        case "between":
                            shouldShow = shouldShow && featureValue >= filter.value[0] && featureValue <= filter.value[1];
                            break;
                        default:
                            console.warn(`Unknown filter operator: ${filter.operator}`);
                    }
                });

                // Hide/show feature based in filter result
                feature.setStyle(shouldShow ? null : new Style({})); // Empty style hides the feature
            });
        },

        /**
         * Add highlighting to the map
         */
        async addHighlighting (command) {
            const {location, options} = command;

            if (!location?.coordinates?.boundingBox) {
                return;
            }

            // Create or get highlight layer
            let highlightLayer = layerCollection.getLayerById("command-highlight-layer");

            if (!highlightLayer) {
                highlightLayer = new VectorLayer({
                    id: "command-highlight-layer",
                    name: "Command Highlights",
                    source: new VectorSource(),
                    alwaysOnTop: true
                });
                this.addLayer(highlightLayer);
            }
            // Clear existing highlights
            highlightLayer.getSource().clear();

            // Create highlight polygon
            await this.createBoundingBoxPolygon(
                location.coordinates.boundingBox,
                options?.style,
                highlightLayer
            );
        },

        /**
         * Create a polygon from bounding box coordinates
         */
        async createBoundingBoxPolygon (boundingBox, style = {}, targetLayer = null) {
            // Convert bounding box to polygon coordinates
            const [minCoords, maxCoords] = boundingBox;
            // eslint-disable-next-line
            const coordinates = [[
                [minCoords[0], minCoords[1]], // bottom-left
                [maxCoords[0], minCoords[1]], // bottom-right
                [maxCoords[0], maxCoords[1]], // top-right
                [minCoords[0], maxCoords[1]], // top-left
                [minCoords[0], minCoords[1]] // close polygon
            ]];
            // Create polygon geometry
            // eslint-disable-next-line
            const polygon = new Polygon(coordinates);

            // Create feature
            // eslint-disable-next-line
            const polygonFeature = new Feature({
                geometry: polygon,
                type: "command-highlight"
            });

            // Apply styling
            // eslint-disable-next-line
            const polygonStyle = new Style({
                fill: new Fill({
                    color: style?.fill || "rgba(255, 100, 50, 0.3)"
                }),
                stroke: new Stroke({
                    color: style?.stroke?.color || "#ff6432",
                    width: style?.stroke?.width || 2
                })
            });

            polygonFeature.setStyle(polygonStyle);

            // Add to layer
            if (targetLayer) {
                targetLayer.getSource().addFeature(polygonFeature);
            }
            else {
                // Create temporary layer if none specified
                const tempLayer = new VectorLayer({
                    id: `temp-highlight-${Date.now()}`,
                    name: "Temporary Highlight",
                    source: new VectorSource(),
                    alwaysOnTop: true
                });

                tempLayer.getSource().addFeature(polygonFeature);
                this.addLayer(tempLayer);
            }

            console.log("Created bounding box polygon with styling");
        },
        /**
         * API call to get JSON Command
         */
        async requestMapCommand (query) {
            try {
                this.isProcessing = true;
                console.log(`Requesting map command for query: "${query}"`);

                // Simulate responses for specific queries
                if ((/lgv/i).test(query)) {
                    const exampleCommand = {
                        "command": {
                            "action": {"type": "zeigen", "confidence": 0.95},
                            "location": {
                                "name": "LGV Hamburg",
                                "coordinates": {"center": [566478.61, 5928155.26], "boundingBox": [[566378.61, 5928055.26], [566578.61, 5928255.26]]},
                                "confidence": 0.88
                            },
                            "options": {
                                "zoom": 5,
                                "addMarker": true,
                                "highlight": true,
                                "style": {"fill": "rgba(255, 100, 50, 0.5)", "stroke": {"color": "#ff6432", "width": 2}}
                            },
                            "rawQuery": query
                        },
                        "metadata": {
                            "requestId": "sim-lgv",
                            "timestamp": new Date().toISOString(),
                            "processingTimeMs": 100
                        }
                    };

                    this.executeMapCommand(exampleCommand);
                    return exampleCommand;
                }

                if ((/fahrradstation(en)? in altona/i).test(query)) {
                    const exampleCommand = {
                        "command": {
                            "action": {"type": "Zeigen", "confidence": 0.95},
                            "layer": {"name": "Fahrradstationen", "id": "18105", "confidence": 0.92},
                            "location": {
                                "type": "district",
                                "name": "Altona",
                                "coordinates": {
                                    "center": [561951.11, 5934289.02],
                                    "boundingBox": [[560800.00, 5929500.00], [563200.00, 5938000.00]]
                                },
                                "confidence": 0.88
                            },
                            "filters": [],
                            "options": {
                                "zoom": 5,
                                "addMarker": true,
                                "highlight": false,
                                "style": {"fill": "rgba(255, 100, 50, 0.5)", "stroke": {"color": "#ff6432", "width": 2}}
                            },
                            "rawQuery": query
                        },
                        "metadata": {
                            "requestId": "sim-fahrrad-altona",
                            "timestamp": new Date().toISOString(),
                            "processingTimeMs": 100
                        }
                    };

                    this.executeMapCommand(exampleCommand);
                    return exampleCommand;
                }

                if ((/kontaktformular/i).test(query)) {
                    const exampleCommand = {
                        "command": {
                            "action": {"type": "Öffne", "confidence": 0.95},
                            "tool": {
                                "name": "Kontakt",
                                "tool": "contact",
                                "side": "secondaryMenu",
                                "props": {
                                    "name": "contact",
                                    "infoMessage": "Schreiben Sie uns Ihre Anfrage",
                                    "subject": "Irgendwas",
                                    "noConfigProps": true
                                }
                            },
                            "options": {"expanded": true},
                            "rawQuery": query
                        },
                        "metadata": {
                            "requestId": "sim-kontakt",
                            "timestamp": new Date().toISOString(),
                            "processingTimeMs": 100
                        }
                    };

                    this.executeMapCommand(exampleCommand);
                    return exampleCommand;
                }

                // Fallback: real API call
                const response = await fetch("https://localhost:8443", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({"input_text": query})
                });

                if (!response.ok) {
                    throw new Error(`API request failed: ${response.statusText}`);
                }

                const commandJson = await response.json(); // eslint-disable-line

                this.executeMapCommand(commandJson);
                return commandJson;
            }
            catch (error) {
                console.error("Error requesting map command:", error);
                throw error;
            }
            finally {
                this.isProcessing = false;
            }
        },

        /**
         * Process natural language query
        */
        async processNaturalLanguageQuery (query) {
            try {
                console.log(`Processing query "${query}"`);
                const result = await this.requestMapCommand(query);

                return result;
            }
            catch (error) {
                console.error("Error processing natural language query", error);
                throw error;
            }
        },

        /**
         * Clear all command-related highlights and temporary layers
         */
        clearCommandHighlights () {
            const highlightLayer = layerCollection.getLayerById("command-highlight-layer");

            if (highlightLayer) {
                highlightLayer.getSource().clear();
            }

            // Remove temporary layers
            const tempLayers = layerCollection.getLayers().filter(layer => // eslint-disable-line
                layer.get('id')?.startsWith('temp-highlight-')             // eslint-disable-line
            );

            tempLayers.forEach(layer => {
                // Remove layer logic here - depends on your layer collection implementation
                console.log(`Removing temporary layer ${layer.get("id")}`);
            });
        },

        // Example method for testing
        async testShowCommand () {
            const exampleCommand = {
                "command": {
                    "action": {
                        "type": "Zeigen",
                        "confidence": 0.95
                    },
                    "layer": {
                        "name": "Fahrradstationen",
                        "id": "18105",
                        "confidence": 0.92
                    },
                    "location": {
                        "type": "district",
                        "name": "Altona",
                        "coordinates": {
                            "center": [561951.11, 5934289.02],
                            "boundingBox": [[560800.00, 5929500.00], [563200.00, 5938000.00]]
                        },
                        "confidence": 0.88
                    },
                    "filters": [],
                    "options": {
                        "zoom": 5,
                        "addMarker": true,
                        "highlight": false,
                        "style": {
                            "fill": "rgba(255, 100, 50, 0.5)",
                            "stroke": {
                                "color": "#ff6432",
                                "width": 2
                            }
                        }
                    },
                    "rawQuery": "Zeige mir alle Fahrradstationen in Altona"
                },
                "metadata": {
                    "requestId": "123-456-789",
                    "timestamp": "2025-05-16T10:23:45Z",
                    "processingTimeMs": 320
                }
            };

            await this.executeMapCommand(exampleCommand);
        },

        async enableTool () {
            this.$store.commit("Modules/Contact/setMail", "julien.hofer@gv.hamburg.de");
            this.$store.commit("Modules/Contact/setPhone", "017444444444");
            this.changeCurrentComponent({
                type: "contact",
                side: "secondaryMenu",
                props: {
                    name: "contact",
                    infoMessage: "Test Message",
                    subject: "Igrendwas",
                    noConfigProps: true
                }
            });
            this.setExpandedBySide({ expanded: true, side: "secondaryMenu" });

        },

        async testToolCommand () {
            const exampleCommand = {
                "command": {
                    "action": {
                        "type": "Öffne",
                        "confidence": 0.95
                    },
                    "tool": {
                        "name": "Kontakt",
                        "tool": "contact",
                        "side": "secondaryMenu",
                        "props": {
                            "name": "contact",
                            "infoMessage": "Schreiben Sie uns Ihre Anfrage",
                            "subject": "Irgendwas",
                            "noConfigProps": true
                        }
                    },
                    "options": {
                        "expanded": true
                    },
                    "rawQuery": "Öffne das Kontaktformular"
                },
                "metadata": {
                    "requestId": "123-456-789",
                    "timestamp": "2025-05-16T10:23:45Z",
                    "processingTimeMs": 320
                }
            };

            await this.executeMapCommand(exampleCommand);
        },

        async testNavigateCommand () {
            const exampleCommand = {
                "command": {
                    "action": {
                        "type": "Zeigen",
                        "confidence": 0.95
                    },
                    "location": {
                        "name": "LGV Hamburg",
                        "coordinates": {
                            "center": [566478.61, 5928155.26],
                            "boundingBox": [[566378.61, 5928055.26], [566578.61, 5928255.26]]
                        },
                        "confidence": 0.88
                    },
                    "options": {
                        "zoom": 5,
                        "addMarker": true,
                        "highlight": true,
                        "style": {
                            "fill": "rgba(255, 100, 50, 0.5)",
                            "stroke": {
                                "color": "#ff6432",
                                "width": 2
                            }
                        }
                    },
                    "rawQuery": "Navigiere zum LGV Hamburg"
                },
                "metadata": {
                    "requestId": "123-456-789",
                    "timestamp": "2025-05-16T10:23:45Z",
                    "processingTimeMs": 320
                }
            };

            await this.executeMapCommand(exampleCommand);
        },

        async onChatWidgetQuery (query, respond) {
            this.isProcessing = true;
            try {
                await this.processNaturalLanguageQuery(query); // This executes the command!
                // You can customize the bot's response here:
                if ((/lgv/i).test(query)) {
                    respond("Ich navigiere zum LGV (Landesbetrieb Geoinformation und Vermessung).");
                }
                else if ((/fahrradstation(en)? in altona/i).test(query)) {
                    respond("Hier sind alle Fahrradstationen in Altona auf der Karte hervorgehoben.");
                }
                else if ((/kontaktformular/i).test(query)) {
                    respond("Das Kontaktformular wird geöffnet.");
                }
                else {
                    respond("Befehl ausgeführt.");
                }
            }
            catch (e) {
                respond("Es gab einen Fehler bei der Verarbeitung.");
            }
            finally {
                this.isProcessing = false;
            }
        }
    }
};
</script>

<template lang="html">
    <div id="tool-chatWithYourMap" class="chatWithYourMap">
        <div class="row h-100">
            <div class="col-12 col-md-12 col-lg-12 h100">
                <div class="h-100">
                    <p>Natural Language Map Control</p>
                    <ChatWidget :isProcessing="isProcessing" @query-submitted="onChatWidgetQuery" />
                    <!-- Command execution status -->
                    <div v-if="isProcessing" class="processing-indicator">
                        <p>Processing command...</p>
                    </div>
                </div>
                <div>
                    <button class="btn btn-primary control-buttons" @click="enableTool">Test Show Command</button>
                </div>
                <!-- Command history -->
                <div v-if="commandHistory.length > 0" class="command-history">
                    <h4>Recent Commands:</h4>
                    <ul>
                        <li v-for="cmd in commandHistory.slice(-5)" :key="cmd.metadata.requestId">
                            {{ cmd.command.rawQuery }} - {{ cmd.command.action.type }}
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.processing-indicator {
    background-color: #f0f8ff;
    border: 1px solid #4a90e2;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}

.control-buttons {
    margin: 15px 0;
}

.control-buttons button {
    margin: 5px;
    padding: 8px 12px;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.control-buttons button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.control-buttons button:hover:not(:disabled) {
    background-color: #357abd;
}

.command-history {
    margin-top: 20px;
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 4px;
}

.command-history ul {
    list-style-type: none;
    padding: 0;
}

.command-history li {
    padding: 5px 0;
    border-bottom: 1px solid #eee;
}
</style>
