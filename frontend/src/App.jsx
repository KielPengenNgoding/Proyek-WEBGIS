import { useState } from 'react'
import Map from './components/Map'
import Sidebar from './components/Sidebar'
import ParkingForm from './components/ParkingForm'

function App() {
  const [filters, setFilters] = useState({})
  const [formOpen, setFormOpen] = useState(false)
  const [editData, setEditData] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleEdit = (properties) => {
    setEditData(properties)
    setFormOpen(true)
  }

  const handleAddNew = () => {
    setEditData(null)
    setFormOpen(true)
  }

  const handleClose = () => {
    setFormOpen(false)
    setEditData(null)
  }

  const handleRefresh = () => setRefreshKey(k => k + 1)

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar filters={filters} setFilters={setFilters} onAddNew={handleAddNew} />
      <div className="flex-1 relative">
        <Map filters={filters} refreshKey={refreshKey} onEdit={handleEdit} />
      </div>
      {formOpen && (
        <ParkingForm
          editData={editData}
          onClose={handleClose}
          onRefresh={handleRefresh}
        />
      )}
    </div>
  )
}

export default App