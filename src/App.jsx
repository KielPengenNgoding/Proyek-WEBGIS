import { useState } from 'react'
import Map from './components/Map'
import Sidebar from './components/Sidebar'

function App() {
  const [filters, setFilters] = useState({})

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
      <Sidebar filters={filters} setFilters={setFilters} />
      <div style={{ flex: 1, position: 'relative' }}>
        <Map filters={filters} />
      </div>
    </div>
  )
}

export default App