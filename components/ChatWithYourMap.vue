<script>
import {mapActions, mapMutations} from "vuex";
import {Vector as VectorLayer} from "ol/layer";
import {Vector as VectorSource} from "ol/source";
import {Feature} from "ol";
import Polygon from "ol/geom/Polygon";
import {Fill, Stroke, Style} from "ol/style";
import {transform} from "ol/proj";
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
            commandHistory: [],
            activatedLayersByCommand: {} // Track which layers were activated by which command
        };
    },
    methods: {
        ...mapActions("Maps", ["setCenter", "setZoom", "placingPointMarker", "addLayer"]),
        ...mapActions("Menu", ["changeCurrentComponent"]),
        ...mapActions("Modules/LayerSelection", ["changeVisibility"]),
        ...mapMutations("Menu", ["setExpandedBySide"]),

        /**
         * Transform coordinates from WGS84 (lat/lon) to EPSG:25832
         */
        transformCoordinates (longitude, latitude) {
            return transform([longitude, latitude], "EPSG:4326", "EPSG:25832");
        },

        /**
         * Calculate bounding box that encompasses all locations
         */
        calculateBoundingBox (locations) {
            if (!locations || locations.length === 0) {
                return null;
            }

            const transformedCoords = locations.map(loc => 
                this.transformCoordinates(
                    loc.coordinates.longitude, 
                    loc.coordinates.latitude
                )
            );

            const xs = transformedCoords.map(c => c[0]);
            const ys = transformedCoords.map(c => c[1]);

            const minX = Math.min(...xs);
            const maxX = Math.max(...xs);
            const minY = Math.min(...ys);
            const maxY = Math.max(...ys);

            // Add padding (10% on each side)
            const paddingX = (maxX - minX) * 0.1;
            const paddingY = (maxY - minY) * 0.1;

            return [
                [minX - paddingX, minY - paddingY],
                [maxX + paddingX, maxY + paddingY]
            ];
        },

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
                const requestId = commandJson.metadata.requestId;

                // Initialize tracking for this command
                this.activatedLayersByCommand[requestId] = {
                    layers: [],
                    locations: [],
                    timestamp: commandJson.metadata.timestamp
                };

                // Execute action based on type
                switch (command.action.type.toLowerCase()) {
                    case "zeigen":
                        this.executeShowCommand(command, requestId);
                        break;
                    case "navigieren":
                        this.navigateToLocations(command.locations, command.options, requestId);
                        break;
                    case "filter":
                        this.executeFilterCommand(command);
                        break;
                    case "öffne":
                        this.executeToolCommand(command);
                        break;
                    default:
                        console.warn(`Unknown action type: ${command.action.type}`);
                        break;
                }

                this.lastCommand = requestId;
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
         * Execute show commands - handles multiple layers and locations
         */
        executeShowCommand (command, requestId) {
            // Handle multiple layers
            if (command.layers && Array.isArray(command.layers)) {
                this.handleMultipleLayerVisibility(command.layers, true, requestId);
            }
            // Fallback to single layer (backwards compatibility)
            else if (command.layer) {
                this.handleLayerVisibility(command.layer, true, requestId);
            }

            // Handle multiple locations
            if (command.locations && Array.isArray(command.locations)) {
                this.navigateToLocations(command.locations, command.options, requestId);
            }
            // Fallback to single location (backwards compatibility)
            else if (command.location) {
                this.navigateToLocation(command.location, command.options);
            }
        },

        /**
         * Handle visibility for multiple layers simultaneously
         */
        handleMultipleLayerVisibility (layers, visible = true, requestId) {
            console.log(`Activating ${layers.length} layers simultaneously`);
            
            const activatedLayers = [];

            layers.forEach(layer => {
                if (layer.id) {
                    try {
                        this.changeVisibility({
                            layerId: layer.id.toString(),
                            value: visible
                        });
                        
                        activatedLayers.push(layer.id.toString());
                        console.log(`✓ Layer ${layer.name} (${layer.id}) activated (confidence: ${layer.confidence})`);
                    }
                    catch (error) {
                        console.error(`✗ Failed to activate layer ${layer.name} (${layer.id}):`, error.message);
                    }
                }
                else {
                    console.warn(`✗ Layer ${layer.name} has no ID, skipping`);
                }
            });

            // Track activated layers for this command
            if (requestId && this.activatedLayersByCommand[requestId]) {
                this.activatedLayersByCommand[requestId].layers = activatedLayers;
            }

            console.log(`Successfully activated ${activatedLayers.length}/${layers.length} layers`);
        },

        /**
         * Handle layer visibility changes (single layer - backwards compatibility)
         */
        handleLayerVisibility (layer, visible = true, requestId) {
            if (layer.id) {
                try {
                    this.changeVisibility({
                        layerId: layer.id.toString(),
                        value: visible
                    });
                    
                    if (requestId && this.activatedLayersByCommand[requestId]) {
                        this.activatedLayersByCommand[requestId].layers.push(layer.id.toString());
                    }
                    
                    console.log(`Layer ${layer.name} (${layer.id}) visibility set to ${visible}`);
                }
                catch (error) {
                    console.error(`Failed to set visibility for layer ${layer.name}:`, error.message);
                }
            }
        },

        /**
         * Navigate to multiple locations simultaneously
         */
        navigateToLocations (locations, options = {}, requestId) {
            if (!locations || locations.length === 0) {
                console.warn("No locations provided for navigation");
                return;
            }

            console.log(`Navigating to ${locations.length} location(s)`);

            // Transform all coordinates
            const transformedLocations = locations.map(loc => ({
                ...loc,
                transformedCoords: this.transformCoordinates(
                    loc.coordinates.longitude,
                    loc.coordinates.latitude
                )
            }));

            // Track locations for this command
            if (requestId && this.activatedLayersByCommand[requestId]) {
                this.activatedLayersByCommand[requestId].locations = locations.map(l => l.name);
            }

            // If single location, use existing logic
            if (transformedLocations.length === 1) {
                const loc = transformedLocations[0];
                const center = loc.transformedCoords;

                this.setCenter(center);
                console.log(`Navigated to: ${loc.name} at [${center.join(", ")}]`);

                if (options.zoom) {
                    this.setZoom(options.zoom);
                }

                if (options.addMarker) {
                    this.placingPointMarker(center);
                }

                return;
            }

            // Multiple locations: calculate bounding box and fit view
            const boundingBox = this.calculateBoundingBox(locations);
            
            if (boundingBox) {
                // Calculate center of bounding box
                const [min, max] = boundingBox;
                const center = [
                    (min[0] + max[0]) / 2,
                    (min[1] + max[1]) / 2
                ];

                this.setCenter(center);
                console.log(`Centered view on ${locations.length} locations`);

                // Add markers for all locations if requested
                if (options.addMarker) {
                    transformedLocations.forEach(loc => {
                        this.placingPointMarker(loc.transformedCoords);
                        console.log(`Added marker for: ${loc.name}`);
                    });
                }

                // Highlight all locations if requested
                if (options.highlight) {
                    this.createMultiLocationHighlight(transformedLocations, options.style);
                }

                // Zoom to fit all locations (calculate appropriate zoom level)
                // You might need to adjust this based on your map's behavior
                if (options.zoom) {
                    this.setZoom(options.zoom);
                }
            }
        },

        /**
         * Navigate to a specific location (single - backwards compatibility)
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
                console.log(`Navigated to: ${location.name} at coordinates [${center.join(", ")}]`);
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
         * Create highlights for multiple locations
         */
        createMultiLocationHighlight (transformedLocations, style = {}) {
            // Get or create highlight layer
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

            // Create circular highlights for each location
            transformedLocations.forEach(loc => {
                const center = loc.transformedCoords;
                const radius = 500; // 500 meters radius

                // Create circle polygon
                const circleCoords = [];
                const sides = 32;
                
                for (let i = 0; i <= sides; i++) {
                    const angle = (i / sides) * 2 * Math.PI;
                    const x = center[0] + radius * Math.cos(angle);
                    const y = center[1] + radius * Math.sin(angle);
                    circleCoords.push([x, y]);
                }

                const polygon = new Polygon([circleCoords]);
                const feature = new Feature({
                    geometry: polygon,
                    type: "command-highlight",
                    locationName: loc.name
                });

                const polygonStyle = new Style({
                    fill: new Fill({
                        color: style?.fill || "rgba(255, 100, 50, 0.3)"
                    }),
                    stroke: new Stroke({
                        color: style?.stroke?.color || "#ff6432",
                        width: style?.stroke?.width || 2
                    })
                });

                feature.setStyle(polygonStyle);
                highlightLayer.getSource().addFeature(feature);
                
                console.log(`Created highlight for: ${loc.name}`);
            });
        },

        /**
         * Execute open tool commands
         */
        executeToolCommand (command) {
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
                            shouldShow = shouldShow && (featureValue < filter.value); // FIXED BUG
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

                // Hide/show feature based on filter result
                feature.setStyle(shouldShow ? null : new Style({}));
            });
        },

        /**
         * Create a polygon from bounding box coordinates
         */
        async createBoundingBoxPolygon (boundingBox, style = {}, targetLayer = null) {
            const [minCoords, maxCoords] = boundingBox;
            const coordinates = [[
                [minCoords[0], minCoords[1]], // bottom-left
                [maxCoords[0], minCoords[1]], // bottom-right
                [maxCoords[0], maxCoords[1]], // top-right
                [minCoords[0], maxCoords[1]], // top-left
                [minCoords[0], minCoords[1]] // close polygon
            ]];

            const polygon = new Polygon(coordinates);
            const polygonFeature = new Feature({
                geometry: polygon,
                type: "command-highlight"
            });

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

            if (targetLayer) {
                targetLayer.getSource().addFeature(polygonFeature);
            }
            else {
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
         * Clear all command-related highlights and deactivate layers from a specific command
         */
        clearCommandLayers (requestId = null) {
            const targetId = requestId || this.lastCommand;

            if (!targetId || !this.activatedLayersByCommand[targetId]) {
                console.warn(`No command found with ID: ${targetId}`);
                return;
            }

            const commandData = this.activatedLayersByCommand[targetId];

            // Deactivate all layers from this command
            commandData.layers.forEach(layerId => {
                try {
                    this.changeVisibility({
                        layerId: layerId,
                        value: false
                    });
                    console.log(`Deactivated layer: ${layerId}`);
                }
                catch (error) {
                    console.error(`Failed to deactivate layer ${layerId}:`, error.message);
                }
            });

            // Clear highlights
            const highlightLayer = layerCollection.getLayerById("command-highlight-layer");
            if (highlightLayer) {
                highlightLayer.getSource().clear();
            }

            // Remove from tracking
            delete this.activatedLayersByCommand[targetId];

            console.log(`Cleaned up command ${targetId}: deactivated ${commandData.layers.length} layers`);
        },

        /**
         * Clear ALL command-activated layers
         */
        clearAllCommandLayers () {
            Object.keys(this.activatedLayersByCommand).forEach(requestId => {
                this.clearCommandLayers(requestId);
            });

            console.log("Cleared all command-activated layers");
        },

        /**
         * Mock data for testing multi-layer and multi-location functionality
         */
        getMockResponse (query) {
            // Multi-layer, multi-location example (Parkplätze + Bahnhalt + Fahrrad in Altona + Wandsbek)
            if (/parkplätze|bahnhalt|fahrrad/i.test(query)) {
                return {
                    "command": {
                        "action": {
                            "type": "Zeigen",
                            "confidence": 0.98
                        },
                        "options": {
                            "layer": [
                                "Parkplätze",
                                "Bahnhalt",
                                "Fahrradsparkplätze"
                            ],
                            "region": [
                                "Altona",
                                "Wandsbek"
                            ],
                            "zoom": 4,
                            "addMarker": true,
                            "highlight": true
                        },
                        "layers": [
                            {
                                "name": "Parkhäuser",
                                "id": "34291",
                                "confidence": 0.8
                            },
                            {
                                "name": "P + R",
                                "id": "29124",
                                "confidence": 0.7
                            },
                            {
                                "name": "Fahrradbügel",
                                "id": "32641",
                                "confidence": 0.9
                            },
                            {
                                "name": "Fahrradabstellanlagen",
                                "id": "30580",
                                "confidence": 0.85
                            },
                            {
                                "name": "Bahnhof",
                                "id": "14523",
                                "confidence": 0.95
                            },
                            {
                                "name": "Haltestellen",
                                "id": "14526",
                                "confidence": 0.9
                            },
                            {
                                "name": "Bahnstationen",
                                "id": "16603",
                                "confidence": 0.85
                            },
                            {
                                "name": "Fahrradparkplätze",
                                "id": "32638",
                                "confidence": 0.8
                            }
                        ],
                        "locations": [
                            {
                                "name": "Altona",
                                "coordinates": {
                                    "latitude": 53.5864667,
                                    "longitude": 9.7776709
                                },
                                "confidence": 0.95
                            },
                            {
                                "name": "Wandsbek",
                                "coordinates": {
                                    "latitude": 53.5760029,
                                    "longitude": 10.0755348
                                },
                                "confidence": 0.95
                            }
                        ],
                        "rawQuery": query
                    },
                    "metadata": {
                        "requestId": `mock-${Date.now()}`,
                        "timestamp": new Date().toISOString()
                    }
                };
            }

            // Single location example (LGV Hamburg)
            if (/lgv/i.test(query)) {
                return {
                    "command": {
                        "action": {
                            "type": "Zeigen",
                            "confidence": 0.95
                        },
                        "options": {
                            "zoom": 5,
                            "addMarker": true,
                            "highlight": true
                        },
                        "locations": [
                            {
                                "name": "LGV Hamburg",
                                "coordinates": {
                                    "latitude": 53.551086,
                                    "longitude": 9.993682
                                },
                                "confidence": 0.88
                            }
                        ],
                        "rawQuery": query
                    },
                    "metadata": {
                        "requestId": `mock-lgv-${Date.now()}`,
                        "timestamp": new Date().toISOString()
                    }
                };
            }

            // Tool opening example (Kontaktformular)
            if (/kontakt/i.test(query)) {
                return {
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
                        "rawQuery": query
                    },
                    "metadata": {
                        "requestId": `mock-kontakt-${Date.now()}`,
                        "timestamp": new Date().toISOString()
                    }
                };
            }

            // Default fallback mock
            return {
                "command": {
                    "action": {
                        "type": "Zeigen",
                        "confidence": 0.8
                    },
                    "options": {
                        "zoom": 4,
                        "addMarker": true
                    },
                    "locations": [
                        {
                            "name": "Hamburg Zentrum",
                            "coordinates": {
                                "latitude": 53.5511,
                                "longitude": 9.9937
                            },
                            "confidence": 0.9
                        }
                    ],
                    "rawQuery": query
                },
                "metadata": {
                    "requestId": `mock-default-${Date.now()}`,
                    "timestamp": new Date().toISOString()
                }
            };
        },

        /**
         * API call to get JSON Command
         */
        async requestMapCommand (query) {
            try {
                this.isProcessing = true;
                console.log(`Requesting map command for query: "${query}"`);

                // MOCK MODE: Comment out this block when backend is ready
                console.log("🔧 Using MOCK data (backend not available)");
                const mockData = this.getMockResponse(query);
                
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 500));
                
                this.executeMapCommand(mockData);
                return mockData;

                // REAL API MODE: Uncomment when backend is ready
                /*
                const response = await fetch("https://localhost:8443", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({"input_text": query})
                });

                if (!response.ok) {
                    throw new Error(`API request failed: ${response.statusText}`);
                }

                const commandJson = await response.json();

                this.executeMapCommand(commandJson);
                return commandJson;
                */
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
         * Get info about activated layers for current command
         */
        getCurrentCommandInfo () {
            if (!this.lastCommand || !this.activatedLayersByCommand[this.lastCommand]) {
                return null;
            }

            return this.activatedLayersByCommand[this.lastCommand];
        },

        async onChatWidgetQuery (query, respond) {
            this.isProcessing = true;
            try {
                await this.processNaturalLanguageQuery(query);
                
                const commandInfo = this.getCurrentCommandInfo();
                if (commandInfo) {
                    const layerCount = commandInfo.layers.length;
                    const locationCount = commandInfo.locations.length;
                    
                    respond(`Befehl ausgeführt: ${layerCount} Layer aktiviert, ${locationCount} Standorte angezeigt.`);
                }
                else {
                    respond("Befehl ausgeführt.");
                }
            }
            catch (e) {
                console.error("Query processing error:", e);
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
                    <ChatWidget 
                        :isProcessing="isProcessing" 
                        @query-submitted="onChatWidgetQuery" 
                    />
                    
                    <!-- Command execution status -->
                    <div v-if="isProcessing" class="processing-indicator">
                        <p>Processing command...</p>
                    </div>

                    <!-- Current command info -->
                    <div v-if="getCurrentCommandInfo()" class="command-info">
                        <h5>Active Command:</h5>
                        <p>
                            <strong>Layers:</strong> {{ getCurrentCommandInfo().layers.length }} active<br>
                            <strong>Locations:</strong> {{ getCurrentCommandInfo().locations.join(', ') }}
                        </p>
                        <button 
                            class="btn btn-sm btn-warning" 
                            @click="clearCommandLayers()"
                        >
                            Clear Current Command
                        </button>
                        <button 
                            class="btn btn-sm btn-danger" 
                            @click="clearAllCommandLayers()"
                        >
                            Clear All Commands
                        </button>
                    </div>
                </div>

                <!-- Command history -->
                <div v-if="commandHistory.length > 0" class="command-history">
                    <h4>Recent Commands:</h4>
                    <ul>
                        <li 
                            v-for="cmd in commandHistory.slice(-5)" 
                            :key="cmd.metadata.requestId"
                        >
                            <strong>{{ cmd.command.rawQuery }}</strong>
                            <br>
                            <small>
                                Action: {{ cmd.command.action.type }} | 
                                Layers: {{ cmd.command.layers?.length || 0 }} | 
                                Locations: {{ cmd.command.locations?.length || 0 }}
                            </small>
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

.command-info {
    background-color: #e8f5e9;
    border: 1px solid #4caf50;
    padding: 15px;
    margin: 10px 0;
    border-radius: 4px;
}

.command-info button {
    margin-right: 10px;
    margin-top: 10px;
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
    padding: 10px;
    margin-bottom: 5px;
    border-bottom: 1px solid #eee;
    background-color: white;
}

.command-history li:hover {
    background-color: #f5f5f5;
}
</style>