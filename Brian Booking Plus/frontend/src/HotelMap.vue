<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({ hotels: { type: Array, required: true }, center: { type: Object, required: true }, selected: { type: String, default: '' } })
const emit = defineEmits(['select'])
const container = ref(null)
const tileError = ref(false)
let map, observer
const markers = new Map()

function selectMarker() {
  for (const [id, marker] of markers) {
    marker.getElement()?.classList.toggle('selected-hotel-marker', id === props.selected)
    marker.setZIndexOffset(id === props.selected ? 1000 : 0)
  }
  const marker = markers.get(props.selected)
  if (marker) { marker.openPopup(); map.panTo(marker.getLatLng()) }
}
onMounted(() => {
  map = L.map(container.value, { scrollWheelZoom: false }).setView([props.center.latitude, props.center.longitude], 13)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).on('tileerror', () => { tileError.value = true }).addTo(map)
  L.circle([props.center.latitude, props.center.longitude], { radius: 5000, color: '#526b7b', weight: 1, fillOpacity: 0.03, interactive: false }).addTo(map)
  props.hotels.forEach((hotel, index) => {
    const title = `${index + 1} · ${hotel.name || 'Name not provided'}`
    const marker = L.marker([hotel.latitude, hotel.longitude], {
      title, alt: title, keyboard: true,
      icon: L.divIcon({ className: 'hotel-map-marker', html: String(index + 1), iconSize: [32, 32], iconAnchor: [16, 32] }),
    }).addTo(map)
    const popup = document.createElement('div')
    const name = document.createElement('strong')
    name.textContent = title
    const address = document.createElement('p')
    address.textContent = hotel.address || 'Address not provided'
    popup.append(name, address)
    marker.bindPopup(popup).on('click', () => emit('select', hotel.place_id))
    markers.set(hotel.place_id, marker)
  })
  if (props.hotels.length) map.fitBounds(props.hotels.map(h => [h.latitude, h.longitude]), { padding: [35, 35], maxZoom: 14 })
  selectMarker()
  observer = new ResizeObserver(() => map.invalidateSize())
  observer.observe(container.value)
})
watch(() => props.selected, () => { if (map) selectMarker() })
onBeforeUnmount(() => { observer?.disconnect(); map?.remove(); markers.clear() })
</script>

<template>
  <div>
    <div ref="container" class="hotel-map" role="region" aria-label="Nearby hotel map; numbered markers match the hotel list"></div>
    <p class="muted">Select a numbered marker or hotel name to highlight the same place. Use Tab and Enter for markers; arrow keys and +/− navigate the focused map.</p>
    <p v-if="tileError" role="alert" class="error">Some map imagery could not load. Hotel locations and the list remain available.</p>
  </div>
</template>

<style>
.hotel-map { height: 420px; width: 100%; border-radius: 8px; z-index: 0; }
.hotel-map-marker { background: #193c55; border: 2px solid white; border-radius: 50%; color: white; display: grid; place-items: center; font: 600 14px system-ui; box-shadow: 0 1px 5px #0005; }
.selected-hotel-marker { background: #a63b12; outline: 3px solid #a63b1255; }
.hotel-map .leaflet-popup-content p { margin: 8px 0; }
</style>
