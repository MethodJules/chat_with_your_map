<script>
import {mapActions, mapMutations} from "vuex";
import {Vector as VetorLayer} from "ol/layer";
import {Vector as VectorSource} from "ol/source";
import {GeoJSON} from "ol/format";
import { Feature } from 'ol';
import Polygon from 'ol/geom/Polygon';
import { Fill, Stroke, Style } from 'ol/style';
import ChatBot from "./ChatBot.vue";
export default {
    components: {
        ChatBot
    },
    name: "ChatWithYourMap",
    methods: {
        ...mapActions("Maps", ["setCenter", "setZoom", "placingPointMarker", "addLayer"]),
        ...mapActions("Menu", ["changeCurrentComponent"]),
        ...mapMutations("Menu", ["setExpandedBySide"]),
        goToLocation() {
            const code = mapCollection.getMapView("2D").getProjection().getCode()
            console.log(code)
            console.log("Go to location");
            const coordinates = [562778.98, 5935272.29]
            // Coordinates 562778.98|5935272.29
            this.setCenter(coordinates); // Set the center of the Map
            this.setZoom(5)
            this.placingPointMarker(coordinates)
            const meinNeuerLayer = new VetorLayer({
                id: "chat-bunty",
                name: "chattxy-bunty",
                source: new VectorSource(),
                alwaysOnTop: true,
            }
            )
            this.addLayer(meinNeuerLayer)

            // Koordinaten für das Polygon (im EPSG:4326 WGS84-Format)
            const coordinates2 = [
                [
                    [562960.94, 5935312.10], // Punkt 1 562960.94|5935312.10
                    [562820.71, 5935011.80], // Punkt 2
                    [562597.14, 5935363.70], // Punkt 3
                    [562960.94, 5935312.10] // Schließen des Polygons
                ],
            ];

            // Geometrie erstellen
            const polygon = new Polygon(coordinates2);
            console.log(polygon);

            // Optional: In Projektion EPSG:3857 umwandeln, falls erforderlich
            // polygon.transform('EPSG:4326', 'EPSG:3857');

            // Feature mit der Geometrie erstellen
            const polygonFeature = new Feature({
                geometry: polygon,
            });

            // Stil für das Polygon festlegen
            polygonFeature.setStyle(
            new Style({
                fill: new Fill({
                color: 'rgba(255, 100, 50, 0.5)', // halbtransparente Füllung
                }),
                stroke: new Stroke({
                color: '#ff6432', // Randfarbe
                width: 2,         // Randbreite
                }),
            })
            );

            meinNeuerLayer.getSource().addFeature(polygonFeature);

        },

        enableTool() {
            this.changeCurrentComponent({
                type: "coordToolkit",
                side: "secondaryMenu",
                props: {
                    name: "coordToolkit"
                }
            });

            this.setExpandedBySide({expanded: true, side: "secondaryMenu"})
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
                        <button @click="goToLocation">Go To Location</button>
                        <button @click="enableTool">Enable Coordinates Tool</button>
                    </div>
                </div>
            </div>
    </div>
</template>