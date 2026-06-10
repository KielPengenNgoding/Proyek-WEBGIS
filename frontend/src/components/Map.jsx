import { useEffect, useState } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import { getParkingAll } from '../services/api'
import ParkingMarker from './ParkingMarker'
import ZoneOverlay from './ZoneOverlay'
import RadiusSearch from './RadiusSearch'
import NearestSearch from './NearestSearch'

const YOGYA_CENTER = [-7.7956, 110.3644]

function Map({ filters, refreshKey, onEdit }) {
  const [parkingData, setParkingData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getParkingAll(filters)
      .then(data => {
        setParkingData(data.features || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching parking:', err)
        setLoading(false)
      })
  }, [filters, refreshKey])

  return (
    <div className="relative w-full h-full">
      {loading && (
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-[1000] bg-white px-4 py-2 rounded shadow text-sm">
          Memuat data parkir...
        </div>
      )}
      <MapContainer
        center={YOGYA_CENTER}
        zoom={13}
        className="w-full h-full"
        style={{ zIndex: 0 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ZoneOverlay />
        {parkingData.map(feature => (
          <ParkingMarker
            key={feature.properties.id_lokasi}
            feature={feature}
            onEdit={onEdit}
          />
        ))}
        <RadiusSearch />
        <NearestSearch />
      </MapContainer>
    </div>
  )
}

export default Map