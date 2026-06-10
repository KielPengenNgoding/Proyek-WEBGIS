import { useState } from 'react'
import { useMap, Marker, Polyline } from 'react-leaflet'
import L from 'leaflet'
import { getParkingNearest } from '../services/api'
import PopupInfo from './PopupInfo'

const nearestIcon = L.divIcon({
  className: '',
  html: `<div style="width:20px;height:20px;border-radius:50%;background:#8B5CF6;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.4)"></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -12],
})

const originIcon = L.divIcon({
  className: '',
  html: `<div style="width:16px;height:16px;border-radius:50%;background:#F59E0B;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.4)"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
})

function NearestSearch() {
  const map = useMap()
  const [open, setOpen] = useState(false)
  const [lng, setLng] = useState('110.3644')
  const [lat, setLat] = useState('-7.7956')
  const [n, setN] = useState('5')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    setLoading(true)
    try {
      const data = await getParkingNearest(parseFloat(lng), parseFloat(lat), parseInt(n))
      setResults(data.features || [])
      map.flyTo([parseFloat(lat), parseFloat(lng)], 15)
    } catch (e) {
      alert('Gagal mengambil data KNN')
    }
    setLoading(false)
  }

  const handleClear = () => setResults(null)
  const origin = results ? [parseFloat(lat), parseFloat(lng)] : null

  return (
    <>
      <div className="leaflet-top leaflet-right" style={{ marginTop: '160px', marginRight: '10px' }}>
        <div className="leaflet-control bg-white rounded-lg shadow-lg p-3 w-64">
          <button onClick={() => setOpen(!open)}
            className="w-full text-left font-semibold text-sm text-purple-700 flex justify-between items-center">
            🟣 Parkir Terdekat (KNN) {open ? '▲' : '▼'}
          </button>
          {open && (
            <div className="mt-2 space-y-2">
              <input type="number" placeholder="Longitude" value={lng}
                onChange={e => setLng(e.target.value)}
                className="w-full border rounded px-2 py-1 text-xs" />
              <input type="number" placeholder="Latitude" value={lat}
                onChange={e => setLat(e.target.value)}
                className="w-full border rounded px-2 py-1 text-xs" />
              <input type="number" placeholder="Jumlah (N)" value={n} min={1} max={20}
                onChange={e => setN(e.target.value)}
                className="w-full border rounded px-2 py-1 text-xs" />
              <div className="flex gap-2">
                <button onClick={handleSearch} disabled={loading}
                  className="flex-1 bg-purple-600 text-white rounded px-2 py-1 text-xs hover:bg-purple-700">
                  {loading ? 'Mencari...' : 'Cari'}
                </button>
                {results && <button onClick={handleClear}
                  className="flex-1 bg-gray-400 text-white rounded px-2 py-1 text-xs hover:bg-gray-500">
                  Reset
                </button>}
              </div>
              {results && <p className="text-xs text-gray-500">{results.length} parkir terdekat</p>}
            </div>
          )}
        </div>
      </div>
      {origin && <Marker position={origin} icon={originIcon} />}
      {results && results.map(f => {
        const pos = [f.geometry.coordinates[1], f.geometry.coordinates[0]]
        return (
          <div key={f.properties.id_lokasi}>
            <Polyline positions={[origin, pos]} pathOptions={{ color: '#8B5CF6', weight: 1.5, dashArray: '4' }} />
            <Marker position={pos} icon={nearestIcon}>
              <PopupInfo properties={f.properties} />
            </Marker>
          </div>
        )
      })}
    </>
  )
}

export default NearestSearch