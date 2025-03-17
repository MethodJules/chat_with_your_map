<script>
import { mapActions, mapMutations } from "vuex";
import { Vector as VetorLayer } from "ol/layer";
import { Vector as VectorSource } from "ol/source";
import { GeoJSON } from "ol/format";
import { Feature } from 'ol';
import Polygon from 'ol/geom/Polygon';
import { Fill, Stroke, Style } from 'ol/style';
import ChatBot from "./ChatBot.vue";

export default {
    components: {
        ChatBot
    },
    name: "ChatWithYourMap",
    data() {
        return {
            // Assuming you have a layerConfig object in your data or can access it from Vuex
            layerConfig: {
                subjectlayer: {
                    elements: [
                        // Your layer definitions here
                        {
                            id: "2003",
                            name: "WFS Schutzgebiete",
                            styleId: "2003",
                            mouseHoverField: "gebietsname",
                            visibility: false // Initially set to false
                        },
                        // Other layers...
                    ]
                }
            }
        };
    },
    methods: {
        ...mapActions("Maps", ["setCenter", "setZoom", "placingPointMarker", "addLayer"]),
        ...mapActions("Menu", ["changeCurrentComponent"]),
        ...mapMutations("Menu", ["setExpandedBySide"]),
        
        goToLocation() {
            const code = mapCollection.getMapView("2D").getProjection().getCode();
            console.log(code);
            console.log("Go to location");
            const coordinates = [562778.98, 5935272.29];
            this.setCenter(coordinates); // Set the center of the Map
            this.setZoom(5);
            this.placingPointMarker(coordinates);
            const meinNeuerLayer = new VetorLayer({
                id: "chat-bunty",
                name: "chattxy-bunty",
                source: new VectorSource(),
                alwaysOnTop: true,
            });
            this.addLayer(meinNeuerLayer);

            const coordinates2 = [
                [
                    [562960.94, 5935312.10],
                    [562820.71, 5935011.80],
                    [562597.14, 5935363.70],
                    [562960.94, 5935312.10]
                ],
            ];

            const polygon = new Polygon(coordinates2);
            console.log(polygon);

            const polygonFeature = new Feature({
                geometry: polygon,
            });

            polygonFeature.setStyle(
                new Style({
                    fill: new Fill({
                        color: 'rgba(255, 100, 50, 0.5)',
                    }),
                    stroke: new Stroke({
                        color: '#ff6432',
                        width: 2,
                    }),
                })
            );

            meinNeuerLayer.getSource().addFeature(polygonFeature);
        },

        enableTool() {
            
            this.changeCurrentComponent({
                type: "layerSlider",
                side: "secondaryMenu",
                props: {
                    name: "layerSlider"
                }
            });

            this.setExpandedBySide({ expanded: true, side: "secondaryMenu" });
        },
        enableTool2(typeID) {
            
            this.changeCurrentComponent({
                type: typeID,
                side: "secondaryMenu",
                props: {
                    name: typeID
                }
            });

            this.setExpandedBySide({ expanded: true, side: "secondaryMenu" });
        },

        enableLayer(layerId) {

            // Find the layer in the layerConfig
            const layer = this.layerConfig.subjectlayer.elements.find(layer => layer.id === layerId);

            if (layer) {
                layer.visibility = true;
                console.log(layer)

                this.updateLayerVisibility(layerId);
                console.log(`Layer ${layerId} enabled.`);
            } else {
                console.error(`Layer with ID ${layerId} not found.`);
            }
        },

        updateLayerVisibility(layerId) {
            console.log(`Layer ${layerId} visibility updated.`);
        }
    }
}
</script>

<template lang="html">
    <div id="tool-chatWithYourMap" class="chatWithYourMap">
        <div class="row h-100">
            <div class="col-12 col-md-12 col-lg-12 h100">
                <div class="h-100">
                    <p>Hier soll das Chatfenster hin</p>
                    <ChatBot />
                    <div class="button-container">
                        <button @click="goToLocation" class="styled-button">Go To Location</button>
                        <button @click="enableTool" class="styled-button">Enable Coordinates Tool</button>
                        <label>Chatbot-Vorschläge</label>

                        <button @click="enableTool2('bufferAnalysis')" class="styled-button">Öffne Buffer Analysis</button>
                        <button @click="enableTool2('measure')" class="styled-button">Öffne Messungen</button>
                        <button @click="enableTool2('shareView')" class="styled-button">Öffne Ansicht als Link kopieren</button>
                        <button @click="enableTool2('legend')" class="styled-button">Öffne Legende Liste</button>
                        <button @click="enableTool2('layerSlider')" class="styled-button">Öffne Simulation von Beispiel-Diensten</button>
                        <button @click="enableTool2('layerConfigS')" class="styled-button">Öffnen layerClusterToggler</button>

                        
                        <button @click="enableLayer('2003')" class="styled-button">Enable WFS Schutzgebiete</button>
                        
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.button-container {
    display: flex;
    flex-wrap: wrap; /* Allow buttons to wrap */
    gap: 10px; /* Space between buttons */
    margin-top: 10px; 
}

.styled-button {
    padding: 10px 20px; 
    border: none;
    border-radius: 25px; /* More rounded edges */
    background-color: #007bff; 
    color: white; 
    font-size: 14px; 
    cursor: pointer;
    transition: background-color 0.3s, transform 0.2s;
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2); 
    display: inline-flex; /* Center text vertically */
    align-items: center; /* Center text vertically */
}

.styled-button:hover {
    background-color: #0056b3; 
    transform: translateY(-1px); 
}

.styled-button:active {
    background-color: #004494; 
    transform: translateY(0); 
}
</style>