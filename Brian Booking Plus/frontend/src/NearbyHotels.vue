<script setup>
import { onMounted, ref } from 'vue'
import HotelMap from './HotelMap.vue'

const zip = ref('16802')
const result = ref(null)
const loading = ref(false)
const error = ref('')
const saved = ref([])
const savedLoading = ref(false)
const savedError = ref('')
const busy = ref(false)
const selected = ref('')
const notice = ref('')

async function request(path, options = {}) {
  const response = await fetch(path, { ...options, signal: AbortSignal.timeout(30000) })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Request could not be completed.')
  }
  return response.status === 204 ? null : response.json()
}
function message(err) {
  return ['TypeError', 'TimeoutError', 'AbortError'].includes(err.name)
    ? 'Could not reach the service. Please try again.' : err.message
}
async function search() {
  if (loading.value) return
  result.value = null
  selected.value = ''
  error.value = ''
  notice.value = ''
  const postcode = zip.value.trim()
  if (!/^[0-9]{5}$/.test(postcode)) {
    error.value = 'Enter a five-digit U.S. ZIP code.'
    return
  }
  loading.value = true
  try {
    result.value = await request(`/api/hotels?postcode=${encodeURIComponent(postcode)}`)
    selected.value = result.value.hotels[0]?.place_id || ''
  } catch (err) { error.value = message(err) }
  finally { loading.value = false }
}
async function refreshSaved() {
  savedLoading.value = true
  savedError.value = ''
  try { saved.value = await request('/api/shortlist') }
  catch (err) { savedError.value = message(err) }
  finally { savedLoading.value = false }
}
function isSaved(id) { return saved.value.some(h => h.place_id === id) }
async function mutate(hotel, remove = false) {
  if (busy.value || (!remove && isSaved(hotel.place_id))) return
  busy.value = true
  savedError.value = ''
  notice.value = ''
  try {
    const data = await request(`/api/shortlist?place_id=${encodeURIComponent(hotel.place_id)}`, { method: remove ? 'DELETE' : 'POST' })
    if (remove) saved.value = saved.value.filter(h => h.place_id !== hotel.place_id)
    else saved.value = data.shortlist
    notice.value = remove ? 'Hotel removed from shortlist.' : 'Hotel saved to shortlist.'
  } catch (err) {
    savedError.value = `${message(err)} The outcome may be uncertain; refresh the shortlist before retrying.`
  } finally { busy.value = false }
}
onMounted(refreshSaved)
</script>

<template>
  <section class="nearby search-panel" aria-labelledby="nearby-title">
    <h2 id="nearby-title">Explore nearby hotels</h2>
    <p class="muted">Search within 5 km of a verified U.S. ZIP location. Place information only—not room availability or booking prices.</p>
    <form @submit.prevent="search">
      <label for="nearby-zip">Hotel search ZIP code</label>
      <div class="search-row">
        <input id="nearby-zip" v-model="zip" inputmode="numeric" type="text" pattern="[0-9]{5}" maxlength="5" required :disabled="loading" />
        <button :disabled="loading" type="submit">{{ loading ? 'Searching…' : 'Find hotels' }}</button>
      </div>
    </form>
    <p v-if="loading" role="status">Resolving ZIP and finding nearby hotels…</p>
    <p v-if="error" role="alert" class="error">{{ error }}</p>
    <template v-if="result">
      <p role="status">{{ result.hotels.length }} hotels returned near ZIP {{ result.center.postcode }}<span v-if="result.center.locality"> · {{ result.center.locality }}</span></p>
      <p class="muted">Up to {{ result.limit }} provider results per search; this is not an exhaustive hotel inventory.<span v-if="result.omitted"> {{ result.omitted }} unusable or out-of-radius results omitted.</span></p>
      <p v-if="!result.hotels.length">No usable hotels returned within 5 km. Try another ZIP code.</p>
      <div v-else class="nearby-layout">
        <ul class="nearby-list nearby-results" aria-label="Nearby hotels">
          <li v-for="(hotel, index) in result.hotels" :key="hotel.place_id" :class="{ 'nearby-selected': selected === hotel.place_id }">
            <button class="secondary" :aria-pressed="selected === hotel.place_id" @click="selected = hotel.place_id">{{ index + 1 }} · {{ hotel.name || 'Name not provided' }}</button>
            <p>{{ hotel.address || 'Address not provided' }}</p>
            <p class="muted">{{ (hotel.distance_m / 1000).toFixed(2) }} km from the ZIP location</p>
            <button :disabled="busy || savedLoading || Boolean(savedError) || isSaved(hotel.place_id)" @click="mutate(hotel)">{{ isSaved(hotel.place_id) ? 'Saved' : 'Save hotel' }}</button>
          </li>
        </ul>
        <HotelMap :hotels="result.hotels" :center="result.center" :selected="selected" @select="selected = $event" />
      </div>
    </template>
    <p class="muted">Powered by <a href="https://www.geoapify.com/">Geoapify</a> · Data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a></p>
    <section aria-labelledby="shortlist-title">
      <div class="section-title"><h2 id="shortlist-title">Saved shortlist</h2><button class="secondary" :disabled="busy || savedLoading" @click="refreshSaved">Refresh shortlist</button></div>
      <p class="muted">Saved place details are snapshots. They remain available when you search another ZIP or restart the app. This local shortlist is shared across demo travelers.</p>
      <p v-if="notice" role="status" class="success">{{ notice }}</p>
      <p v-if="savedLoading" role="status">Loading shortlist…</p>
      <p v-if="savedError" role="alert" class="error">{{ savedError }}</p>
      <p v-if="!saved.length && !savedLoading && !savedError">No saved hotels yet. Save a place from your results.</p>
      <ul class="nearby-list" aria-label="Saved hotels">
        <li v-for="hotel in saved" :key="hotel.place_id">
          <strong>{{ hotel.name || 'Name not provided' }}</strong>
          <p>{{ hotel.address || 'Address not provided' }}</p>
          <p class="muted">Search ZIP {{ hotel.postcode }} · {{ hotel.latitude }}, {{ hotel.longitude }} · Saved {{ hotel.saved_at }}</p>
          <button class="danger" :disabled="busy || savedLoading" :aria-label="`Remove ${hotel.name || 'unnamed hotel'} from shortlist`" @click="mutate(hotel, true)">Remove</button>
        </li>
      </ul>
    </section>
  </section>
</template>

<style scoped>
.nearby { margin: 26px 0; }
.nearby h2 { margin-top: 0; }
.nearby-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.nearby-list { list-style: none; padding: 0; }
.nearby-results { max-height: 500px; overflow-y: auto; margin-top: 0; padding: 3px; }
.nearby-list li { padding: 16px; border: 1px solid #d4dee6; border-radius: 8px; margin-bottom: 12px; overflow-wrap: anywhere; }
.nearby-list .nearby-selected { border: 2px solid #2682bd; background: #eaf4fc; }
.nearby-list button { white-space: normal; text-align: left; }
@media(max-width: 760px) { .nearby-layout { grid-template-columns: 1fr; } }
</style>
