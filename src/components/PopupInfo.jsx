import { Popup } from 'react-leaflet'

function PopupInfo({ properties: p }) {
  return (
    <Popup>
      <div className="text-sm min-w-[200px]">
        <h3 className="font-bold text-base mb-2 text-blue-700">{p.nama_lokasi}</h3>
        <table className="w-full text-xs">
          <tbody>
            <tr><td className="text-gray-500 pr-2">Zona</td><td>{p.nama_zona || '-'}</td></tr>
            <tr><td className="text-gray-500 pr-2">Jenis</td><td>{p.jenis_kendaraan || '-'}</td></tr>
            <tr><td className="text-gray-500 pr-2">Tarif/jam</td>
              <td>{p.tarif_per_jam > 0 ? `Rp ${p.tarif_per_jam}` : 'Gratis'}</td></tr>
            <tr><td className="text-gray-500 pr-2">Berbayar</td>
              <td>{p.fee_berbayar === true ? '✅ Ya' : p.fee_berbayar === false ? '❌ Tidak' : '-'}</td></tr>
            <tr><td className="text-gray-500 pr-2">Status</td>
              <td><span className={`font-semibold ${p.status === 'aktif' ? 'text-green-600' : 'text-red-500'}`}>
                {p.status || '-'}
              </span></td></tr>
            {p.jarak_m > 0 && (
              <tr><td className="text-gray-500 pr-2">Jarak</td>
                <td>{(p.jarak_m / 1000).toFixed(2)} km</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Popup>
  )
}

export default PopupInfo