import { useState, useEffect } from 'react'
import { createParking, updateParking, deleteParking } from '../services/api'

const EMPTY_FORM = {
  nama_lokasi: '', alamat: '', longitude: '', latitude: '',
  kapasitas_total: '', tarif_per_jam: '0', operator: '',
  jam_buka: '', jam_tutup: '', fee_berbayar: false,
  beratap: false, status: 'aktif', tipe_parkir: '',
}

function ParkingForm({ editData, onClose, onRefresh }) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(false)
  const isEdit = !!editData

  useEffect(() => {
    if (editData) {
      setForm({
        nama_lokasi: editData.nama_lokasi || '',
        alamat: editData.alamat || '',
        longitude: editData.longitude || '',
        latitude: editData.latitude || '',
        kapasitas_total: editData.kapasitas_total || '',
        tarif_per_jam: editData.tarif_per_jam || '0',
        operator: editData.operator || '',
        jam_buka: editData.jam_buka || '',
        jam_tutup: editData.jam_tutup || '',
        fee_berbayar: editData.fee_berbayar || false,
        beratap: editData.beratap || false,
        status: editData.status || 'aktif',
        tipe_parkir: editData.tipe_parkir || '',
      })
    } else {
      setForm(EMPTY_FORM)
    }
  }, [editData])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSubmit = async () => {
    if (!form.nama_lokasi || !form.longitude || !form.latitude) {
      alert('Nama lokasi, longitude, dan latitude wajib diisi!')
      return
    }
    setLoading(true)
    try {
      const payload = {
        ...form,
        longitude: parseFloat(form.longitude),
        latitude: parseFloat(form.latitude),
        kapasitas_total: form.kapasitas_total ? parseInt(form.kapasitas_total) : null,
        tarif_per_jam: parseFloat(form.tarif_per_jam) || 0,
      }
      if (isEdit) {
        await updateParking(editData.id_lokasi, payload)
        alert('Data berhasil diupdate!')
      } else {
        await createParking(payload)
        alert('Lokasi parkir berhasil ditambahkan!')
      }
      onRefresh()
      onClose()
    } catch (e) {
      alert('Gagal menyimpan data: ' + (e.response?.data?.detail || e.message))
    }
    setLoading(false)
  }

  const handleDelete = async () => {
    if (!window.confirm(`Hapus "${editData.nama_lokasi}"? Tindakan ini tidak bisa dibatalkan.`)) return
    setLoading(true)
    try {
      await deleteParking(editData.id_lokasi)
      alert('Data berhasil dihapus!')
      onRefresh()
      onClose()
    } catch (e) {
      alert('Gagal menghapus data')
    }
    setLoading(false)
  }

  const Field = ({ label, name, type = 'text', placeholder = '' }) => (
    <div>
      <label className="text-xs text-gray-500 block mb-1">{label}</label>
      <input type={type} name={name} value={form[name]} onChange={handleChange}
        placeholder={placeholder}
        className="w-full border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
    </div>
  )

  return (
    <div className="w-72 bg-white shadow-lg flex flex-col border-l z-10">
      {/* Header */}
      <div className={`px-4 py-3 text-white flex justify-between items-center ${isEdit ? 'bg-orange-500' : 'bg-green-600'}`}>
        <h2 className="font-bold text-sm">{isEdit ? '✏️ Edit Parkir' : '➕ Tambah Parkir'}</h2>
        <button onClick={onClose} className="text-white hover:text-gray-200 text-lg leading-none">×</button>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <Field label="Nama Lokasi *" name="nama_lokasi" placeholder="cth: Parkir Malioboro" />
        <Field label="Alamat" name="alamat" placeholder="Jl. ..." />
        <div className="grid grid-cols-2 gap-2">
          <Field label="Longitude *" name="longitude" type="number" placeholder="110.36" />
          <Field label="Latitude *" name="latitude" type="number" placeholder="-7.79" />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <Field label="Kapasitas" name="kapasitas_total" type="number" />
          <Field label="Tarif/jam (Rp)" name="tarif_per_jam" type="number" />
        </div>
        <Field label="Operator" name="operator" />
        <div className="grid grid-cols-2 gap-2">
          <Field label="Jam Buka" name="jam_buka" placeholder="07:00" />
          <Field label="Jam Tutup" name="jam_tutup" placeholder="22:00" />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Status</label>
          <select name="status" value={form.status} onChange={handleChange}
            className="w-full border rounded px-2 py-1.5 text-sm">
            <option value="aktif">Aktif</option>
            <option value="nonaktif">Nonaktif</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Tipe Parkir</label>
          <select name="tipe_parkir" value={form.tipe_parkir} onChange={handleChange}
            className="w-full border rounded px-2 py-1.5 text-sm">
            <option value="">-- Pilih --</option>
            <option value="tepi jalan">Tepi Jalan</option>
            <option value="gedung">Gedung</option>
            <option value="lahan">Lahan</option>
          </select>
        </div>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" name="fee_berbayar" checked={form.fee_berbayar} onChange={handleChange} />
            Berbayar
          </label>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" name="beratap" checked={form.beratap} onChange={handleChange} />
            Beratap
          </label>
        </div>
      </div>

      {/* Actions */}
      <div className="p-4 border-t space-y-2">
        <button onClick={handleSubmit} disabled={loading}
          className={`w-full py-2 rounded text-white text-sm font-semibold
            ${isEdit ? 'bg-orange-500 hover:bg-orange-600' : 'bg-green-600 hover:bg-green-700'}
            disabled:opacity-50`}>
          {loading ? 'Menyimpan...' : isEdit ? 'Simpan Perubahan' : 'Tambah Lokasi'}
        </button>
        {isEdit && (
          <button onClick={handleDelete} disabled={loading}
            className="w-full py-2 rounded text-white text-sm font-semibold bg-red-500 hover:bg-red-600 disabled:opacity-50">
             Hapus Lokasi Ini
          </button>
        )}
      </div>
    </div>
  )
}

export default ParkingForm