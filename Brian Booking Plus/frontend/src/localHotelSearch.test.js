import test from 'node:test'
import assert from 'node:assert/strict'
import { loadHotels } from './localHotelSearch.js'

test('saved ZIP reads dated values without the Part 1 API endpoint', async () => {
  const paths = []
  const local = { center: { postcode: '16802' }, hotels: [{ place_id: 'fixture', nights: [{ nightly_rate_cents: 12345, rooms_available: 7 }] }] }
  const found = await loadHotels('16802', async path => { paths.push(path); return local })
  assert.deepEqual(paths, ['/api/local-hotels?postcode=16802'])
  assert.equal(found.source, 'Saved locally')
  assert.equal(found.result.hotels[0].nights[0].nightly_rate_cents, 12345)
})

test('successful empty local lookup falls back once, preserving leading zeros', async () => {
  const paths = []
  const responses = [{ hotels: [], center: null }, { hotel_ids: ['already-saved'] }, { hotels: [], center: { postcode: '02108' } }]
  const found = await loadHotels('02108', async path => { paths.push(path); return responses.shift() })
  assert.deepEqual(paths, ['/api/local-hotels?postcode=02108', '/api/local-hotels/status', '/api/hotels?postcode=02108'])
  assert.equal(found.source, 'API results')
  assert.deepEqual(found.savedIds, ['already-saved'])
})

test('failed local lookup never falls back', async () => {
  const paths = []
  await assert.rejects(loadHotels('16802', async path => { paths.push(path); throw new Error('Local storage unavailable') }), /Local storage/)
  assert.deepEqual(paths, ['/api/local-hotels?postcode=16802'])
})

test('malformed local response is an error rather than empty success', async () => {
  let calls = 0
  await assert.rejects(loadHotels('16802', async () => { calls++; return {} }), /invalid/)
  assert.equal(calls, 1)
})

test('saved status failure blocks provider lookup and ambiguous Add buttons', async () => {
  const paths = []
  await assert.rejects(loadHotels('16802', async path => {
    paths.push(path)
    if (paths.length === 1) return { hotels: [] }
    throw new Error('Status unavailable')
  }), /Status unavailable/)
  assert.equal(paths.length, 2)
})
