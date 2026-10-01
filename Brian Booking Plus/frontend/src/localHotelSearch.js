// A failed local lookup deliberately never becomes a provider fallback.
export async function loadHotels(postcode, request) {
  const query = encodeURIComponent(postcode)
  const local = await request(`/api/local-hotels?postcode=${query}`)
  if (!Array.isArray(local.hotels)) throw new Error('Local hotel response was invalid.')
  if (local.hotels.length) {
    if (!local.center) throw new Error('Saved search location is unavailable.')
    return { result: local, source: 'Saved locally', savedIds: local.hotels.map(h => h.place_id) }
  }
  const status = await request('/api/local-hotels/status')
  if (!Array.isArray(status.hotel_ids)) throw new Error('Saved hotel status is unavailable.')
  const result = await request(`/api/hotels?postcode=${query}`)
  return { result, source: 'API results', savedIds: status.hotel_ids }
}
