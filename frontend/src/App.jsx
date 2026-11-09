import { useEffect, useState } from 'react'
import { listWatches, createWatch, refreshWatch, deleteWatch, getConfig } from './api'
import Sparkline from './components/Sparkline'
import './App.css'

const money = (v, cur = 'THB') =>
  v == null ? '-' : `${Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })} ${cur}`

const emptyForm = { origin: '', destination: '', departure_date: '', target_price: '' }

function WatchCard({ w, busy, onRefresh, onDelete }) {
  const prices = w.history.map((h) => Number(h.price))
  const dir = w.change_pct > 0 ? 'up' : w.change_pct < 0 ? 'down' : 'flat'
  return (
    <article className={`card ${w.below_target ? 'hit' : ''}`}>
      <header>
        <h3>{w.origin} <span>→</span> {w.destination}</h3>
        <time>{w.departure_date}</time>
      </header>
      <div className="price-row">
        <strong className="price">{money(w.latest_price, w.currency)}</strong>
        {w.change_pct != null && w.checks > 1 && (
          <span className={`chg ${dir}`}>{w.change_pct > 0 ? '+' : ''}{w.change_pct}%</span>
        )}
      </div>
      <p className="muted">{w.airline} · lowest {money(w.lowest_price, w.currency)} · {w.checks} checks</p>
      <Sparkline values={prices} />
      {w.target_price != null && (
        <p className={`target ${w.below_target ? 'ok' : ''}`}>
          {w.below_target ? 'Target reached' : 'Target'} · {money(w.target_price, w.currency)}
        </p>
      )}
      <footer>
        <button onClick={() => onRefresh(w.id)} disabled={busy}>{busy ? 'Checking…' : 'Check price'}</button>
        <button className="danger" onClick={() => onDelete(w.id)} disabled={busy}>Remove</button>
      </footer>
    </article>
  )
}

export default function App() {
  const [watches, setWatches] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState(null)
  const [error, setError] = useState('')
  const [provider, setProvider] = useState('')

  const load = async () => {
    try {
      setWatches(await listWatches())
      setError('')
    } catch (e) {
      setError(`Cannot reach the API: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => {
    load()
    getConfig().then((c) => setProvider(c.price_provider)).catch(() => {})
  }, [])

  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    try {
      const created = await createWatch({
        origin: form.origin,
        destination: form.destination,
        departure_date: form.departure_date,
        target_price: form.target_price ? Number(form.target_price) : null,
      })
      setWatches((prev) => [...prev, created].sort((a, b) => a.departure_date.localeCompare(b.departure_date)))
      setForm(emptyForm)
      setError('')
    } catch (e) {
      setError(e.message)
    }
  }

  const refresh = async (id) => {
    setBusyId(id)
    try {
      const updated = await refreshWatch(id)
      setWatches((prev) => prev.map((w) => (w.id === id ? updated : w)))
    } catch (e) { setError(e.message) } finally { setBusyId(null) }
  }

  const remove = async (id) => {
    setBusyId(id)
    try {
      await deleteWatch(id)
      setWatches((prev) => prev.filter((w) => w.id !== id))
    } catch (e) { setError(e.message) } finally { setBusyId(null) }
  }

  return (
    <main className="app">
      <header className="top">
        <h1>Flight<span>Hunter</span></h1>
        <p className="muted">Track flight prices over time and spot the drop.</p>
        {provider === 'mock' && (
          <p className="notice">Demo data: prices are simulated, not real fares.</p>
        )}
      </header>

      <form className="form" onSubmit={submit}>
        <input name="origin" value={form.origin} onChange={change} placeholder="From (BKK)" maxLength={3} required />
        <input name="destination" value={form.destination} onChange={change} placeholder="To (CNX)" maxLength={3} required />
        <input name="departure_date" type="date" value={form.departure_date} onChange={change} required />
        <input name="target_price" type="number" min="1" value={form.target_price} onChange={change} placeholder="Target price (THB, optional)" />
        <button type="submit">Track route</button>
      </form>

      {error && <div className="error" role="alert">{error}</div>}

      {loading ? <p className="muted">Loading…</p> : watches.length === 0 ? (
        <p className="empty">No routes yet. Add one above to start tracking.</p>
      ) : (
        <section className="grid">
          {watches.map((w) => (
            <WatchCard key={w.id} w={w} busy={busyId === w.id} onRefresh={refresh} onDelete={remove} />
          ))}
        </section>
      )}
    </main>
  )
}
