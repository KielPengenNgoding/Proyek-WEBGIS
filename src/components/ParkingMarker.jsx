import { Marker } from 'react-leaflet'
import L from 'leaflet'
import PopupInfo from './PopupInfo'

// Ikon warna berbeda per jenis kendaraan
const createIcon = (color) => L.divIcon({
  className: '',
  html: `<div style="
    width:28px;height:28px;border-radius:50% 50% 50% 0;
    background:${color};border:2px solid white;
    transform:rotate(-45deg);box-shadow:0 2px 6px rgba(0,0,0,0.4)
  "></div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -30],
})

const ICONS = {
  mobil:      createIcon('#3B82F6'),   // biru
  motor:      createIcon('#10B981'),   // hijau
  disabilitas: createIcon('#F59E0B'),  // kuning
  default:    createIcon('#6B7280'),   // abu
}

function getIcon(jenis) {
  if (!jenis) return ICONS.default
  const j = jenis.toLowerCase()
  if (j.includes('mobil')) return ICONS.mobil
  if (j.includes('motor')) return ICONS.motor
  if (j.includes('disabilitas')) return ICONS.disabilitas
  return ICONS.default
}

function ParkingMarker({ feature }) {
  const { geometry, properties } = feature
  const [lng, lat] = geometry.coordinates
  const icon = getIcon(properties.jenis_kendaraan)

  return (
    <Marker position={[lat, lng]} icon={icon}>
      <PopupInfo properties={properties} />
    </Marker>
  )
}

export default ParkingMarker