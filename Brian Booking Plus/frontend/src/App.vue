<script setup>
import { computed, onMounted, ref, watch } from 'vue'

const query = ref('')
const searchedQuery = ref('')
const stays = ref([])
const searched = ref(false)
const loading = ref(false)
const error = ref('')
const users = ref([])
const selectedUser = ref('')
const userError = ref('')
const usersLoading = ref(false)
const history = ref([])
const historyLoading = ref(false)
const historyError = ref('')
const busy = ref(false)
const notice = ref('')
const actionError = ref('')
const pendingDelete = ref('')
const traveler = computed(() => users.value.find(user => user.user_id === selectedUser.value))
let historyRequest = 0
const dollars = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

async function request(path, options = {}) {
  const response = await fetch(path, { ...options, signal: AbortSignal.timeout(20000) })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status}).`)
  }
  return response.status === 204 ? null : response.json()
}

async function loadUsers() {
  usersLoading.value = true
  userError.value = ''
  try {
    users.value = await request('/api/users')
    selectedUser.value = users.value[0]?.user_id || ''
  } catch {
    userError.value = 'Could not load travelers. Check that the backend is running, then retry.'
  } finally {
    usersLoading.value = false
  }
}

async function loadHistory() {
  const requestId = ++historyRequest
  historyLoading.value = true
  historyError.value = ''
  history.value = []
  try {
    const rows = await request(`/api/bookings?user_id=${encodeURIComponent(selectedUser.value)}`)
    if (requestId === historyRequest) history.value = rows
  } catch {
    if (requestId === historyRequest) historyError.value = 'Could not load booking history. Please retry.'
  } finally {
    if (requestId === historyRequest) historyLoading.value = false
  }
}

watch(selectedUser, () => {
  notice.value = ''
  actionError.value = ''
  pendingDelete.value = ''
  if (selectedUser.value) loadHistory()
})
onMounted(loadUsers)

async function changeBooking(method, booking = null, tripId = null) {
  if (busy.value || !selectedUser.value) return
  busy.value = true
  notice.value = ''
  actionError.value = ''
  try {
    const path = booking ? `/api/bookings/${encodeURIComponent(booking.booking_id)}` : '/api/bookings'
    const body = method === 'POST' ? { user_id: selectedUser.value, trip_id: tripId } : { status: 'cancelled' }
    const result = await request(path, {
      method,
      ...(method === 'DELETE' ? {} : { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
    })
    notice.value = method === 'POST' ? `Booking created for ${result.trip_name}. View it in history below.`
      : method === 'PATCH' ? 'Booking cancelled. The record is retained in history.'
        : 'Booking deleted. It has been removed from history.'
  } catch (err) {
    actionError.value = `Could not confirm the change. ${err.message} Refresh history before trying again.`
  } finally {
    pendingDelete.value = ''
    await loadHistory()
    busy.value = false
  }
}

async function search() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  stays.value = []
  searched.value = false
  searchedQuery.value = query.value.trim()
  try {
    stays.value = await request(`/api/stays?hotel_name=${encodeURIComponent(searchedQuery.value)}`)
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
      <h1>Brian Booking Plus</h1>
      <p>Find a hotel stay, make a simulated booking, and manage your history.</p>
    </header>
    <section class="traveler-panel" aria-label="Demo traveler">
      <label for="traveler">Demo traveler</label>
      <select id="traveler" v-model="selectedUser" :disabled="busy || usersLoading" aria-describedby="traveler-help">
        <option v-if="!users.length" value="">{{ usersLoading ? 'Loading travelers…' : 'Travelers unavailable' }}</option>
        <option v-for="user in users" :key="user.user_id" :value="user.user_id">{{ user.display_name }} ({{ user.user_id }})</option>
      </select>
      <p id="traveler-help" class="muted">Bookings and history belong to the selected demo traveler. No sign-in or payment is needed.</p>
      <p v-if="userError" role="alert" class="error">{{ userError }} <button @click="loadUsers" :disabled="usersLoading">Retry travelers</button></p>
    </section>
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
          <thead><tr><th scope="col">Hotel / location</th><th scope="col">Stay / trip ID</th><th scope="col">Check-in</th><th scope="col">Check-out</th><th scope="col">Nights</th><th scope="col">Nightly rate (USD)</th><th scope="col">Stay price (USD)</th><th scope="col">Book</th></tr></thead>
          <tbody><tr v-for="stay in stays" :key="stay.trip_id">
            <td><strong>{{ stay.hotel_name }}</strong><span>{{ stay.city }}, {{ stay.state }} · {{ stay.hotel_id }}</span></td>
            <td>{{ stay.trip_name }}<span>{{ stay.trip_id }}</span></td>
            <td class="date">{{ stay.check_in }}</td><td class="date">{{ stay.check_out }}</td>
            <td>{{ stay.nights }}</td><td>{{ dollars.format(stay.nightly_rate_usd) }}</td><td><strong>{{ dollars.format(stay.stay_price_usd) }}</strong></td>
            <td><button :disabled="busy || !selectedUser" :aria-label="`Book ${stay.trip_name}`" @click="changeBooking('POST', null, stay.trip_id)">Book stay</button></td>
          </tr></tbody>
        </table>
      </div>
    </section>
    <p v-if="notice" role="status" class="success">{{ notice }}</p>
    <p v-if="actionError" role="alert" class="error">{{ actionError }}</p>
    <section class="history" aria-label="Booking history" :aria-busy="historyLoading || busy">
      <div class="section-title"><h2>Booking history</h2><button class="secondary" :disabled="busy || historyLoading || !selectedUser" @click="loadHistory">Refresh history</button></div>
      <p v-if="traveler" class="muted">{{ traveler.display_name }} ({{ selectedUser }}) · Cancel to keep a record; delete to remove a test booking.</p>
      <p v-if="historyLoading" role="status">Loading booking history…</p>
      <p v-else-if="historyError" role="alert" class="error">{{ historyError }}</p>
      <p v-else-if="selectedUser && !history.length">No bookings yet for this traveler. Search for a stay to make a simulated booking.</p>
      <div v-else-if="history.length" class="table-scroll">
        <table>
          <caption class="sr-only">Saved bookings for the selected traveler</caption>
          <thead><tr><th scope="col">Booking / booked on</th><th scope="col">Hotel / stay</th><th scope="col">Dates / nights</th><th scope="col">Stay price (USD)</th><th scope="col">Status</th><th scope="col">Actions</th></tr></thead>
          <tbody><tr v-for="booking in history" :key="booking.booking_id">
            <td><code class="booking-id">{{ booking.booking_id }}</code><span>{{ booking.booked_on }}</span></td>
            <td><strong>{{ booking.hotel_name }}</strong><span>{{ booking.trip_name }} · {{ booking.trip_id }}</span></td>
            <td><span class="date">{{ booking.check_in }} → {{ booking.check_out }}</span>{{ booking.nights }} nights</td>
            <td>{{ dollars.format(booking.stay_price_usd) }}</td>
            <td><span class="status" :class="booking.status">{{ booking.status }}</span></td>
            <td><div class="actions">
              <button v-if="booking.status === 'confirmed'" class="secondary" :disabled="busy" :aria-label="`Cancel booking ${booking.booking_id}`" @click="changeBooking('PATCH', booking)">Cancel booking</button>
              <button class="danger" :disabled="busy" :aria-label="`Delete booking ${booking.booking_id}`" @click="pendingDelete = booking.booking_id">Delete booking</button>
            </div>
              <div v-if="pendingDelete === booking.booking_id" class="delete-confirm">
                <p>Remove this booking from history?</p>
                <div class="actions"><button class="danger" :disabled="busy" @click="changeBooking('DELETE', booking)">Confirm delete</button><button class="secondary" :disabled="busy" @click="pendingDelete = ''">Keep booking</button></div>
              </div>
            </td>
          </tr></tbody>
        </table>
      </div>
    </section>
    <footer>Fictional hotels and sample prices for a classroom project. Prices exclude taxes and fees.</footer>
  </main>
</template>
