<script setup>
import { ref } from 'vue'

const query = ref('')
const searchedQuery = ref('')
const stays = ref([])
const searched = ref(false)
const loading = ref(false)
const error = ref('')
const dollars = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

async function search() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  stays.value = []
  searched.value = false
  searchedQuery.value = query.value.trim()
  try {
    const response = await fetch(`/api/stays?hotel_name=${encodeURIComponent(searchedQuery.value)}`, { signal: AbortSignal.timeout(10000) })
    if (!response.ok) throw new Error(`Search failed (${response.status}).`)
    stays.value = await response.json()
    searched.value = true
  } catch {
    error.value = 'Could not load stays. Check that the backend is running, then search again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main>
    <header>
      <p class="eyebrow">HOTEL STAYS · CLASSROOM DEMO</p>
      <h1>Expedia Lite</h1>
      <p>Find your next hotel stay.</p>
    </header>
    <section class="search-panel" aria-label="Hotel search">
      <form @submit.prevent="search">
        <label for="hotel-name">Hotel name</label>
        <div class="search-row">
          <input id="hotel-name" v-model="query" maxlength="200" placeholder="e.g. Harbor Lantern Hotel" aria-describedby="search-help" type="search" />
          <button type="submit" :disabled="loading">{{ loading ? 'Searching…' : 'Search' }}</button>
        </div>
        <p id="search-help" class="muted">Enter all or part of a hotel name. Leave blank to see all stays.</p>
      </form>
    </section>
    <section class="results" aria-label="Search results" :aria-busy="loading">
      <p v-if="error" role="alert" class="error">{{ error }}</p>
      <div role="status" aria-live="polite">
        <p v-if="loading">Searching hotel stays…</p>
        <p v-else-if="!searched && !error" class="muted">Search to explore the available stays in our sample collection.</p>
        <template v-else-if="searched">
          <h2>{{ stays.length }} {{ stays.length === 1 ? 'stay' : 'stays' }} found</h2>
          <p v-if="!stays.length">No hotels match “{{ searchedQuery }}”. Try another hotel name.</p>
          <p v-else class="muted">{{ searchedQuery ? `Hotels matching “${searchedQuery}”` : 'All sample hotels' }} · Fixed check-in and check-out dates</p>
        </template>
      </div>
      <div v-if="stays.length" class="table-scroll">
        <table>
          <caption class="sr-only">Matching hotels and their offered stays. Prices are in US dollars.</caption>
          <thead><tr><th scope="col">Hotel / location</th><th scope="col">Stay / trip ID</th><th scope="col">Check-in</th><th scope="col">Check-out</th><th scope="col">Nights</th><th scope="col">Nightly rate (USD)</th><th scope="col">Stay price (USD)</th></tr></thead>
          <tbody><tr v-for="stay in stays" :key="stay.trip_id">
            <td><strong>{{ stay.hotel_name }}</strong><span>{{ stay.city }}, {{ stay.state }} · {{ stay.hotel_id }}</span></td>
            <td>{{ stay.trip_name }}<span>{{ stay.trip_id }}</span></td>
            <td class="date">{{ stay.check_in }}</td><td class="date">{{ stay.check_out }}</td>
            <td>{{ stay.nights }}</td><td>{{ dollars.format(stay.nightly_rate_usd) }}</td><td><strong>{{ dollars.format(stay.stay_price_usd) }}</strong></td>
          </tr></tbody>
        </table>
      </div>
    </section>
    <footer>Fictional hotels and sample prices for a classroom project. Prices exclude taxes and fees.</footer>
  </main>
</template>
