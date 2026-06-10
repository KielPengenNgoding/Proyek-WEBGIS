function LandingPage({ onEnter }) {
  const features = [
    {
      icon: '🗺️',
      title: 'Peta Interaktif',
      desc: 'Visualisasi 95 lokasi parkir di Kota Yogyakarta secara real-time dengan basemap OpenStreetMap.'
    },
    {
      icon: '🔴',
      title: 'Pencarian Radius',
      desc: 'Temukan semua parkir dalam radius tertentu dari titik koordinat yang kamu tentukan.'
    },
    {
      icon: '🟣',
      title: 'Parkir Terdekat (KNN)',
      desc: 'Cari N parkir terdekat dari lokasimu menggunakan algoritma K-Nearest Neighbor.'
    },
    {
      icon: '🏙️',
      title: 'Zona Voronoi',
      desc: '21 zona wilayah parkir Yogyakarta ditampilkan dengan overlay polygon berwarna.'
    },
    {
      icon: '🚗',
      title: 'Filter Kendaraan',
      desc: 'Filter parkir berdasarkan jenis kendaraan: Mobil, Motor, atau Disabilitas.'
    },
    {
      icon: '💰',
      title: 'Info Tarif',
      desc: 'Informasi lengkap tarif parkir, status berbayar/gratis, dan detail lokasi.'
    },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc', fontFamily: 'sans-serif' }}>
      {/* Navbar */}
      <nav style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '16px 48px', background: 'white', borderBottom: '1px solid #e2e8f0',
        position: 'sticky', top: 0, zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 24 }}>🅿️</span>
          <span style={{ fontWeight: 700, fontSize: 18, color: '#1e40af' }}>WebGIS Parkir</span>
        </div>
        <button onClick={onEnter} style={{
          background: '#1e40af', color: 'white', border: 'none',
          padding: '8px 20px', borderRadius: 8, cursor: 'pointer', fontWeight: 600
        }}>
          Buka Peta →
        </button>
      </nav>

      {/* Hero */}
      <div style={{
        textAlign: 'center', padding: '80px 24px 60px',
        background: 'linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%)'
      }}>
        <div style={{
          display: 'inline-block', background: '#dbeafe', color: '#1e40af',
          padding: '4px 16px', borderRadius: 999, fontSize: 13, fontWeight: 600, marginBottom: 20
        }}>
          Sistem Informasi Geografis · ITERA 2025/2026
        </div>
        <h1 style={{ fontSize: 48, fontWeight: 800, color: '#0f172a', margin: '0 0 16px' }}>
          Sistem Informasi<br />
          <span style={{ color: '#1e40af' }}>Parkir Publik</span> Yogyakarta
        </h1>
        <p style={{ fontSize: 18, color: '#64748b', maxWidth: 520, margin: '0 auto 40px' }}>
          Temukan lokasi parkir mobil dan motor di Kota Yogyakarta dengan mudah menggunakan WebGIS interaktif.
        </p>
        <button onClick={onEnter} style={{
          background: '#1e40af', color: 'white', border: 'none',
          padding: '14px 36px', borderRadius: 10, cursor: 'pointer',
          fontWeight: 700, fontSize: 16, boxShadow: '0 4px 14px rgba(30,64,175,0.3)'
        }}>
          Mulai Jelajahi Peta →
        </button>
        <div style={{ marginTop: 48, display: 'flex', justifyContent: 'center', gap: 48, flexWrap: 'wrap' }}>
          {[['95', 'Lokasi Parkir'], ['21', 'Zona Wilayah'], ['3', 'Jenis Kendaraan']].map(([num, label]) => (
            <div key={label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 36, fontWeight: 800, color: '#1e40af' }}>{num}</div>
              <div style={{ fontSize: 14, color: '#64748b' }}>{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Fitur */}
      <div style={{ padding: '64px 48px', maxWidth: 1100, margin: '0 auto' }}>
        <h2 style={{ textAlign: 'center', fontSize: 32, fontWeight: 700, color: '#0f172a', marginBottom: 8 }}>
          Fitur Aplikasi
        </h2>
        <p style={{ textAlign: 'center', color: '#64748b', marginBottom: 48 }}>
          Semua yang kamu butuhkan untuk menemukan parkir terbaik
        </p>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 24
        }}>
          {features.map(f => (
            <div key={f.title} style={{
              background: 'white', borderRadius: 12, padding: '28px 24px',
              border: '1px solid #e2e8f0', transition: 'box-shadow 0.2s'
            }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>{f.icon}</div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 8 }}>{f.title}</h3>
              <p style={{ fontSize: 14, color: '#64748b', lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer style={{
        textAlign: 'center', padding: '24px', borderTop: '1px solid #e2e8f0',
        color: '#94a3b8', fontSize: 13
      }}>
        Kelompok 17 · SIG ITERA 2025/2026
      </footer>
    </div>
  )
}

export default LandingPage