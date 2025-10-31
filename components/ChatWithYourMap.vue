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

            const transformedCoords = locations.map(loc => this.transformCoordinates(
                    loc.coordinates.longitude,
                    loc.coordinates.latitude
                )
                ),

                xs = transformedCoords.map(c => c[0]),
                ys = transformedCoords.map(c => c[1]),

                minX = Math.min(...xs),
                maxX = Math.max(...xs),
                minY = Math.min(...ys),
                maxY = Math.max(...ys),

                // Add padding (10% on each side)
                paddingX = (maxX - minX) * 0.1,
                paddingY = (maxY - minY) * 0.1;

            return [
                [minX - paddingX, minY - paddingY],
                [maxX + paddingX, maxY + paddingY]
            ];
        },

        /**
         * Main method to execute map commands from json
         */
        executeMapCommand (responseData) {
            try {
                this.isProcessing = true;
                console.log("Executing command: ", responseData);

                // Check if response is successful
                if (!responseData.success) {
                    console.error("Command execution failed:", responseData);
                    return {
                        success: false,
                        message: responseData.text_response || "Command execution failed"
                    };
                }

                const {data} = responseData,
                    command = data.command,
                    requestId = `req-${Date.now()}`;

                // Store command in history
                this.commandHistory.push({
                    query: data.query,
                    command: command,
                    layers: data.layers,
                    locations: data.locations,
                    executedAt: new Date().toISOString(),
                    requestId: requestId
                });

                // Initialize tracking for this command
                this.activatedLayersByCommand[requestId] = {
                    layers: [],
                    locations: [],
                    timestamp: new Date().toISOString()
                };

                // Execute action based on type
                switch (command.action.type.toLowerCase()) {
                    case "zeigen":
                        this.executeShowCommand(data, requestId); // FIXED: Pass 'data' not 'command'
                        break;
                    case "navigieren":
                        this.navigateToLocations(data.locations?.locations, {}, requestId);
                        break;
                    case "filter":
                        this.executeFilterCommand(data);
                        break;
                    case "öffne":
                        this.executeToolCommand(data);
                        break;
                    default:
                        console.warn(`Unknown action type: ${command.action.type}`);
                        break;
                }

                this.lastCommand = requestId;

                return {
                    success: true,
                    message: responseData.text_response,
                    requestId: requestId
                };
            }
            catch (error) {
                console.error("Error executing map command", error);
                return {
                    success: false,
                    message: "Es gab einen Fehler bei der Ausführung des Befehls"
                };
            }
            finally {
                this.isProcessing = false;
            }
        },

        /**
         * Execute show commands - handles layers and locations from new structure
         */
        executeShowCommand (data, requestId) {
            // Handle layers from new structure
            // New structure: data.layers.layers (single layer object)
            if (data.layers && data.layers.layers) {
                // Convert single layer to array for compatibility
                const layerArray = [data.layers.layers];
                this.handleMultipleLayerVisibility(layerArray, true, requestId); // FIXED: Correct parameter order
            }

            // Handle locations from new structure
            // New structure: data.locations.locations (array)
            if (data.locations && data.locations.locations && Array.isArray(data.locations.locations)) {
                this.navigateToLocations(data.locations.locations, {}, requestId); // FIXED: Call correct method
            }
        },

        /**
         * Handle visibility for multiple layers simultaneously
         */
        handleMultipleLayerVisibility (layers, visible = true, requestId) { // FIXED: Correct parameter order
            console.log(`Activating ${layers.length} layers simultaneously`);

            const activatedLayers = [];

            layers.forEach(layer => {
                if (layer.id) {
                    try {
                        this.changeVisibility({
                            layerId: layer.id,
                            value: visible
                        });

                        activatedLayers.push(layer.id);
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
                        layerId: layer.id,
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
                this.activatedLayersByCommand[requestId].locations = locations.map(loc => loc.name);
            }

            if (locations.length === 1) {
                // Single location - navigate directly
                const loc = transformedLocations[0];
                this.navigateToSingleLocation(loc, options);
            }
            else {
                // Multiple locations - fit view to bounding box
                this.fitViewToMultipleLocations(transformedLocations, options); // FIXED: Corrected method name
            }

            // Add markers for all locations
            if (options.showMarkers !== false) {
                this.addLocationMarkers(transformedLocations, options);
            }

            // Add bounding box visualization if requested
            if (options.showBoundingBox) {
                this.visualizeBoundingBox(locations);
            }
        },

        /**
         * Navigate to a single location
         */
        navigateToSingleLocation (location, options = {}) {
            const coords = location.transformedCoords;
            const zoom = options.zoom || 5;

            console.log(`Navigating to ${location.name} at [${coords}] with zoom ${zoom}`);

            this.setCenter(coords);
            this.setZoom(zoom);
        },

        /**
         * Fit view to multiple locations
         */
        fitViewToMultipleLocations (transformedLocations, options = {}) { // FIXED: Corrected method name
            const originalLocations = transformedLocations.map(loc => ({
                name: loc.name,
                coordinates: {
                    latitude: loc.coordinates.latitude,
                    longitude: loc.coordinates.longitude
                }
            }));

            const bbox = this.calculateBoundingBox(originalLocations);

            if (bbox) {
                const center = [
                    (bbox[0][0] + bbox[1][0]) / 2,
                    (bbox[0][1] + bbox[1][1]) / 2
                ];

                console.log(`Fitting view to ${transformedLocations.length} locations with center at [${center}]`);
                this.setCenter(center);

                // Calculate appropriate zoom level based on bounding box size
                const width = bbox[1][0] - bbox[0][0],
                    height = bbox[1][1] - bbox[0][1],
                    maxDimension = Math.max(width, height);

                // Rough zoom calculation (can be refined based on your map settings)
                let zoom = 15;

                if (maxDimension > 50000) {
                    zoom = 10;
                }
                else if (maxDimension > 20000) {
                    zoom = 12;
                }
                else if (maxDimension > 10000) {
                    zoom = 13;
                }

                this.setZoom(options.zoom || zoom);
            }
        },

        /**
         * Add markers for locations
         */
        addLocationMarkers (locations, options = {}) {
            locations.forEach(location => {
                this.placingPointMarker({
                    coordinates: location.transformedCoords,
                    label: location.name
                });
                console.log(`✓ Marker added for ${location.name}`);
            });
        },

        /**
         * Visualize bounding box around locations
         */
        visualizeBoundingBox (locations) {
            const bbox = this.calculateBoundingBox(locations);
            if (!bbox) {
                return;
            }

            // Create polygon feature for bounding box
            const polygon = new Polygon([[
                [bbox[0][0], bbox[0][1]], // bottom-left
                [bbox[1][0], bbox[0][1]], // bottom-right
                [bbox[1][0], bbox[1][1]], // top-right
                [bbox[0][0], bbox[1][1]], // top-left
                [bbox[0][0], bbox[0][1]]  // close polygon
            ]]);

            const feature = new Feature({
                geometry: polygon
            });

            feature.setStyle(new Style({
                stroke: new Stroke({
                    color: "rgba(255, 0, 0, 0.8)",
                    width: 2
                }),
                fill: new Fill({
                    color: "rgba(255, 0, 0, 0.1)"
                })
            }));

            // Create vector layer for bounding box
            const vectorSource = new VectorSource({
                features: [feature]
            });

            const vectorLayer = new VectorLayer({
                source: vectorSource,
                name: "BoundingBox_Overlay",
                id: `bbox_${Date.now()}`
            });

            this.addLayer({layer: vectorLayer});
            console.log("✓ Bounding box visualization added");
        },

        /**
         * Navigate to single location (backwards compatibility)
         */
        navigateToLocation (location, options = {}) {
            const transformedCoords = this.transformCoordinates(
                location.coordinates.longitude,
                location.coordinates.latitude
            );

            const zoom = options.zoom || 15;

            console.log(`Navigating to ${location.name} at [${transformedCoords}] with zoom ${zoom}`);

            this.setCenter(transformedCoords);
            this.setZoom(zoom);

            // Add marker if requested
            if (options.showMarker !== false) {
                this.placingPointMarker({
                    coordinates: transformedCoords,
                    label: location.name
                });
            }
        },

        /**
         * Execute filter commands
         */
        executeFilterCommand (data) {
            console.log("Filter command execution not yet implemented");
            // TODO: Implement filter logic
        },

        /**
         * Execute tool commands (e.g., opening specific tools)
         */
        executeToolCommand (data) {
            console.log("Tool command execution not yet implemented");
            // TODO: Implement tool opening logic
        },

        /**
         * Clear layers activated by current command
         */
        clearCommandLayers () {
            if (!this.lastCommand || !this.activatedLayersByCommand[this.lastCommand]) {
                console.warn("No active command to clear");
                return;
            }

            const commandInfo = this.activatedLayersByCommand[this.lastCommand];

            console.log(`Clearing ${commandInfo.layers.length} layers from command ${this.lastCommand}`);

            commandInfo.layers.forEach(layerId => {
                try {
                    this.changeVisibility({
                        layerId: layerId,
                        value: false
                    });
                    console.log(`✓ Layer ${layerId} deactivated`);
                }
                catch (error) {
                    console.error(`✗ Failed to deactivate layer ${layerId}:`, error);
                }
            });

            // Remove from tracking
            delete this.activatedLayersByCommand[this.lastCommand];
            this.lastCommand = null;
        },

        /**
         * Clear all layers from all commands
         */
        clearAllCommandLayers () {
            console.log("Clearing all command layers");

            Object.keys(this.activatedLayersByCommand).forEach(requestId => {
                const commandInfo = this.activatedLayersByCommand[requestId];

                commandInfo.layers.forEach(layerId => {
                    try {
                        this.changeVisibility({
                            layerId: layerId,
                            value: false
                        });
                    }
                    catch (error) {
                        console.error(`Failed to deactivate layer ${layerId}:`, error);
                    }
                });
            });

            // Clear all tracking
            this.activatedLayersByCommand = {};
            this.lastCommand = null;
            this.commandHistory = [];
        },

        /**
         * Generate mock response with new backend structure
         */
        getMockResponse (query) {
            const lowerQuery = query.toLowerCase();

            // Mock response matching new backend structure
            if (lowerQuery.includes("fahrrad") || lowerQuery.includes("bike") || lowerQuery.includes("fahrräder")) {
                return {
                    "success": true,
                    "text_response": "Hallo! Du hast nach allen frei verfügbaren Fahrrädern in Wandsbek gefragt. Ich habe deine Anfrage bearbeitet und die \"Anzahl frei verfügbarer Fahrräder je StadtRad-Station\"-Schicht identifiziert, die am besten zu deiner Suche passt. Ich kann dir jetzt alle relevanten Fahrradstationen in Wandsbek anzeigen, lass uns loslegen!",
                    "data": {
                        "query": query,
                        "reasoning": "The query asks to display bike stations in a specific location.",
                        "command": {
                            "action": {
                                "type": "Zeigen",
                                "confidence": 0.95
                            }
                        },
                        "layers": {
                            "layers": {
                                "name": "StadtRAD-Stationen Hamburg",
                                "id": "18105",
                                "confidence": 0.92
                            }
                        },
                        "locations": {
                            "locations": [
                                {
                                    "name": "Wandsbek",
                                    "coordinates": {
                                        "latitude": 53.5760029,
                                        "longitude": 10.0755348
                                    },
                                    "confidence": 0.95
                                }
                            ]
                        }
                    },
                    "metadata": {
                        "num_agent_calls": 3,
                        "reasoning": null
                    }
                };
            }

            // Default mock response
            return {
                "success": true,
                "text_response": `Ich habe deine Anfrage "${query}" verarbeitet und werde dir helfen, die relevanten Informationen auf der Karte anzuzeigen.`,
                "data": {
                    "query": query,
                    "reasoning": "Processing general map query.",
                    "command": {
                        "action": {
                            "type": "Zeigen",
                            "confidence": 0.85
                        }
                    },
                    "layers": {
                        "layers": {
                            "name": "Default Layer",
                            "id": "1234",
                            "confidence": 0.8
                        }
                    },
                    "locations": {
                        "locations": [
                            {
                                "name": "Hamburg",
                                "coordinates": {
                                    "latitude": 53.5511,
                                    "longitude": 9.9937
                                },
                                "confidence": 0.9
                            }
                        ]
                    }
                },
                "metadata": {
                    "num_agent_calls": 2,
                    "reasoning": null
                }
            };
        },

        /**
         * API call to get JSON Command
         * Updated to handle new backend response structure
         */
        async requestMapCommand (query) {
            try {
                this.isProcessing = true;
                console.log(`Requesting map command for query: "${query}"`);

                // MOCK MODE: Comment out this block when backend is ready
                /*
                console.log("🔧 Using MOCK data (backend not available)");
                const mockData = this.getMockResponse(query);

                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 500));

                return this.executeMapCommand(mockData);
                */
                // REAL API MODE: Uncomment when backend is ready

                const response = await fetch("http://localhost:8082/api/query", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        "query": query,
                        "include_reasoning": false,
                        "language": "German"
                    })
                });

                if (!response.ok) {
                    throw new Error(`API request failed: ${response.statusText}`);
                }

                const responseData = await response.json();

                // Validate response structure
                if (!responseData.success) {
                    throw new Error(responseData.text_response || "Backend returned unsuccessful response");
                }

                return this.executeMapCommand(responseData);
                
            }
            catch (error) {
                console.error("Error requesting map command:", error);
                return {
                    success: false,
                    message: "Es gab einen Fehler bei der Kommunikation mit dem Server."
                };
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

        /**
         * Handle chat widget query - updated to use text_response from backend
         */
        async onChatWidgetQuery (query, respond) {
            this.isProcessing = true;
            try {
                const result = await this.processNaturalLanguageQuery(query);

                if (result && result.success) {
                    // Use the text_response from backend as the bot's response
                    respond(result.message);
                }
                else {
                    // Fallback response if execution failed
                    respond(result.message || "Es gab einen Fehler bei der Verarbeitung.");
                }
            }
            catch (e) {
                console.error("Query processing error:", e);
                respond("Es gab einen Fehler bei der Verarbeitung deiner Anfrage.");
            }
            finally {
                this.isProcessing = false;
            }
        },

        /**
         * Set zoom
         */
        zoom () {
            console.log("Setting zoom...")
            this.setZoom(5);
        }
    }
};
</script>

<template lang="html">
    <div id="tool-chatWithYourMap"
         class="chatWithYourMap"
    >
        <div class="row h-100">
            <div class="col-12 col-md-12 col-lg-12 h100">
                <div class="h-100">
                    <ChatWidget
                        :is-processing="isProcessing"
                        @query-submitted="onChatWidgetQuery"
                    />

                    <!-- Command execution status -->
                    <div v-if="isProcessing"
                         class="processing-indicator"
                    >
                        <p>Processing command...</p>
                    </div>
                    <button class="btn" @click="zoom()">Zoom</button>
                    <!-- Current command info (optional, can be uncommented for debugging) -->
                    <!-- <div v-if="getCurrentCommandInfo()" class="command-info">
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
                    </div> -->
                </div>

                <!-- Command history (optional, can be uncommented for debugging) -->
                <div v-if="commandHistory.length > 0"
                     class="command-history"
                >
                    <h4>Recent Commands:</h4>
                    <ul>
                        <li
                            v-for="cmd in commandHistory.slice(-5)"
                            :key="cmd.requestId"
                        >
                            <strong>{{ cmd.query }}</strong>
                            <br>
                            <small>
                                Action: {{ cmd.command.action.type }} |
                                Layers: {{ cmd.layers?.layers ? 1 : 0 }} |
                                Locations: {{ cmd.locations?.locations?.length || 0 }}
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