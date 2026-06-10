import { useEffect, useState } from 'react'
import { GeoJSON, Tooltip } from 'react-leaflet'
import { getZones } from '../services/api'

const ZONE_COLORS = [
  '#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEAA7',
  '#DDA0DD','#98D8C8','#F7DC6F','#BB8FCE','#85C1E9',
  '#82E0AA','#F1948A','#AED6F1','#A9DFBF','#FAD7A0',
  '#D2B4DE','#A3E4D7','#FDEBD0','#D5DBDB','#ABB2B9','#F9E79F'
]

function ZoneOverlay() {
  const [zones, setZones] = useState(null)
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    getZones().then(setZones).catch(console.error)
  }, [])

  if (!zones || !visible) return null

  return (
    <GeoJSON
      key={JSON.stringify(zones)}
      data={zones}
      style={(feature) => ({
        fillColor: ZONE_COLORS[feature.properties.id_zona % ZONE_COLORS.length],
        fillOpacity: 0.15,
        color: ZONE_COLORS[feature.properties.id_zona % ZONE_COLORS.length],
        weight: 1.5,
        opacity: 0.7,
      })}
      onEachFeature={(feature, layer) => {
        layer.bindTooltip(feature.properties.nama_zona, {
          permanent: true,
          direction: 'center',
          className: 'zone-label',
        })
      }}
    />
  )
}

export default ZoneOverlay