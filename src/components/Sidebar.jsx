function Sidebar({ filters, setFilters }) {
  const jenisOptions = ['Mobil', 'Motor', 'Disabilitas']

  const toggleJenis = (jenis) => {
    setFilters(f => ({
      ...f,
      jenis_kendaraan: f.jenis_kendaraan === jenis ? undefined : jenis
    }))
  }

  const toggleFee = (val) => {
    setFilters(f => ({
      ...f,
      fee_berbayar: f.fee_berbayar === val ? undefined : val
    }))
  }

  return (
    <div className="w-64 bg-white shadow-lg flex flex-col z-10">
      {/* Header */}
      <div className="bg-blue-700 text-white px-4 py-4">
        <h1 className="font-bold text-lg leading-tight">🅿️ WebGIS Parkir</h1>
        <p className="text-xs text-blue-200 mt-1">Kota Yogyakarta</p>
      </div>

      <div className="p-4 flex flex-col gap-4 overflow-y-auto flex-1">
        {/* Filter Jenis Kendaraan */}
        <div>
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">
            Jenis Kendaraan
          </h2>
          <div className="flex flex-col gap-1">
            {jenisOptions.map(j => (
              <button key={j}
                onClick={() => toggleJenis(j)}
                className={`text-left px-3 py-2 rounded text-sm font-medium transition-colors
                  ${filters.jenis_kendaraan === j
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                {j === 'Mobil' ? '🚗' : j === 'Motor' ? '🏍️' : '♿'} {j}
              </button>
            ))}
            {filters.jenis_kendaraan && (
              <button onClick={() => setFilters(f => ({ ...f, jenis_kendaraan: undefined }))}
                className="text-xs text-gray-400 hover:text-gray-600 text-left px-3 py-1">
                ✕ Hapus filter
              </button>
            )}
          </div>
        </div>

        {/* Filter Fee */}
        <div>
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">
            Tarif Parkir
          </h2>
          <div className="flex flex-col gap-1">
            <button onClick={() => toggleFee(false)}
              className={`text-left px-3 py-2 rounded text-sm font-medium transition-colors
                ${filters.fee_berbayar === false
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
              🆓 Gratis
            </button>
            <button onClick={() => toggleFee(true)}
              className={`text-left px-3 py-2 rounded text-sm font-medium transition-colors
                ${filters.fee_berbayar === true
                  ? 'bg-orange-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
              💰 Berbayar
            </button>
            {filters.fee_berbayar !== undefined && (
              <button onClick={() => setFilters(f => ({ ...f, fee_berbayar: undefined }))}
                className="text-xs text-gray-400 hover:text-gray-600 text-left px-3 py-1">
                ✕ Hapus filter
              </button>
            )}
          </div>
        </div>

        {/* Legend */}
        <div>
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">
            Legenda Marker
          </h2>
          <div className="flex flex-col gap-1 text-xs text-gray-600">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div> Mobil
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-emerald-500"></div> Motor
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-amber-400"></div> Disabilitas
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div> Hasil Radius
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-purple-500"></div> Hasil KNN
            </div>
          </div>
        </div>
      </div>

      <div className="px-4 py-3 border-t text-xs text-gray-400">
        Kelompok 17 · SIG ITERA 2025/2026
      </div>
    </div>
  )
}

export default Sidebar