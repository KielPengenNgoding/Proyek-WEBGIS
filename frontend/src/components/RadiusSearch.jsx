import { useState } from 'react'
import { useMap, Circle, Marker } from 'react-leaflet'
import L from 'leaflet'
import { getParkingRadius } from '../services/api'
import PopupInfo from './PopupInfo'

const resultIcon = L.divIcon({
  className: '',
  html: `<div style="width:20px;height:20px;border-radius:50%;background:#EF4444;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.4)"></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -12],
})

function RadiusSearch() {
  const map = useMap()
  const [open, setOpen] = useState(false)
  const [lng, setLng] = useState('110.3644')
  const [lat, setLat] = useState('-7.7956')
  const [radius, setRadius] = useState('500')
  const [results, setResults] = useState(null)
  const [center, setCenter] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    setLoading(true)
    try {
      const data = await getParkingRadius(parseFloat(lng), parseFloat(lat), parseFloat(radius))
      setResults(data.features || [])
      setCenter([parseFloat(lat), parseFloat(lng)])
      map.flyTo([parseFloat(lat), parseFloat(lng)], 15)
    } catch (e) {
      alert('Gagal mengambil data radius')
    }
    setLoading(false)
  }

  const handleClear = () => { setResults(null); setCenter(null) }

  return (
    <>
      <div className="leaflet-top leaflet-right" style={{ marginTop: '10px', marginRight: '10px' }}>
        <div className="leaflet-control bg-white rounded-lg shadow-lg p-3 w-64">
          <button onClick={() => setOpen(!open)}
            className="w-full text-left font-semibold text-sm text-blue-700 flex justify-between items-center">
            🔴 Pencarian Radius {open ? '▲' : '▼'}
          </button>
          {open && (
            <div className="mt-2 space-y-2">
              <input type="number" placeholder="Longitude" value={lng}
                onChange={e => setLng(e.target.value)}
                className="w-full border rounded px-2 py-1 text-xs" />
              <input type="number" placeholder="Latitude" value={lat}
                onChange={e => setLat(e.target.value)}
                className="w-full border rounded px-2 py-1 text-xs" />
              <input type="number" placeholder="Radius (meter)" value={radius}
                onChange={e => setRadius(e.target.value)}
                className="w-full border rounded px-2 py-1 text-xs" />
              <div className="flex gap-2">
                <button onClick={handleSearch} disabled={loading}
                  className="flex-1 bg-blue-600 text-white rounded px-2 py-1 text-xs hover:bg-blue-700">
                  {loading ? 'Mencari...' : 'Cari'}
                </button>
                {results && <button onClick={handleClear}
                  className="flex-1 bg-gray-400 text-white rounded px-2 py-1 text-xs hover:bg-gray-500">
                  Reset
                </button>}
              </div>
              {results && <p className="text-xs text-gray-500">{results.length} parkir ditemukan</p>}
            </div>
          )}
        </div>
      </div>
      {center && <Circle center={center} radius={parseFloat(radius)}
        pathOptions={{ color: '#EF4444', fillOpacity: 0.1 }} />}
      {results && results.map(f => (
        <Marker key={f.properties.id_lokasi} position={[f.geometry.coordinates[1], f.geometry.coordinates[0]]} icon={resultIcon}>
          <PopupInfo properties={f.properties} />
        </Marker>
      ))}
    </>
  )
}

export default RadiusSearch