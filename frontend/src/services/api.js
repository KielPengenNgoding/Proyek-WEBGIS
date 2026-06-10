import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

// Ambil semua parkir (dengan filter opsional)
export const getParkingAll = (filters = {}) =>
  api.get('/parking/', { params: filters }).then(r => r.data)

// Parkir dalam radius
export const getParkingRadius = (longitude, latitude, radius_m, jenis_kendaraan = null) =>
  api.get('/parking/radius', {
    params: { longitude, latitude, radius_m, ...(jenis_kendaraan && { jenis_kendaraan }) }
  }).then(r => r.data)

// N parkir terdekat (KNN)
export const getParkingNearest = (longitude, latitude, n = 5, jenis_kendaraan = null) =>
  api.get('/parking/nearest', {
    params: { longitude, latitude, n, ...(jenis_kendaraan && { jenis_kendaraan }) }
  }).then(r => r.data)

// Detail satu parkir
export const getParkingDetail = (id) =>
  api.get(`/parking/${id}`).then(r => r.data)

// Semua zona Voronoi
export const getZones = () =>
  api.get('/zones/geojson').then(r => r.data)

// Semua kategori kendaraan
export const getCategories = () =>
  api.get('/categories/').then(r => r.data)

// Tambah lokasi parkir baru
export const createParking = (data) =>
  api.post('/parking/', data).then(r => r.data)

// Update lokasi parkir
export const updateParking = (id, data) =>
  api.put(`/parking/${id}`, data).then(r => r.data)

// Hapus lokasi parkir
export const deleteParking = (id) =>
  api.delete(`/parking/${id}`).then(r => r.data)