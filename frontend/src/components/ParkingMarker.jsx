import { Marker } from 'react-leaflet'
import L from 'leaflet'
import PopupInfo from './PopupInfo'

const colorMap = {
  Mobil: '#3b82f6',
  Motor: '#10b981',
  Disabilitas: '#f59e0b',
}

function createIcon(color) {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:14px;height:14px;border-radius:50%;
      background:${color};border:2px solid white;
      box-shadow:0 1px 3px rgba(0,0,0,0.4)">
    </div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  })
}

function ParkingMarker({ feature, onEdit }) {
  const { geometry, properties } = feature
  const [lng, lat] = geometry.coordinates
  const color = colorMap[properties.jenis_kendaraan] || '#6b7280'

  return (
    <Marker position={[lat, lng]} icon={createIcon(color)}>
      <PopupInfo properties={properties} onEdit={onEdit} />
    </Marker>
  )
}

export default ParkingMarker