import React, { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:8000/api'

export default function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState(localStorage.getItem('access') || '')
  const [dashboard, setDashboard] = useState(null)
  const [meals, setMeals] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (token) localStorage.setItem('access', token)
  }, [token])

  async function login() {
    setMessage('')
    try {
      const res = await fetch(`${API_BASE}/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      if (!res.ok) {
        setMessage('Login failed')
        return
      }
      const data = await res.json()
      setToken(data.access)
      setMessage('Logged in')
    } catch (e) {
      setMessage('Network error')
    }
  }

  async function fetchDashboard() {
    setMessage('')
    try {
      const res = await fetch(`${API_BASE}/dashboard/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      const data = await res.json()
      if (!res.ok) setMessage(data.error || 'Failed to load dashboard')
      else setDashboard(data)
    } catch (e) {
      setMessage('Network error')
    }
  }

  async function fetchMeals() {
    setMessage('')
    try {
      const res = await fetch(`${API_BASE}/meals/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      const data = await res.json()
      if (!res.ok) setMessage(data.error || 'Failed to load meals')
      else setMeals(data)
    } catch (e) {
      setMessage('Network error')
    }
  }

  function logout() {
    setToken('')
    localStorage.removeItem('access')
    setDashboard(null)
    setMeals(null)
    setMessage('Logged out')
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: 24 }}>
      <h1>NutriTracker Frontend</h1>
      <p>
        Backend: <a href="http://localhost:8000">http://localhost:8000</a>
      </p>

      {!token ? (
        <div style={{ maxWidth: 420 }}>
          <h3>Login</h3>
          <input placeholder="username" value={username} onChange={e => setUsername(e.target.value)} />
          <br />
          <input placeholder="password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
          <br />
          <button onClick={login}>Login</button>
          <p style={{ color: 'red' }}>{message}</p>
        </div>
      ) : (
        <div style={{ maxWidth: 900 }}>
          <p>Authenticated as <strong>{username}</strong></p>
          <button onClick={fetchDashboard}>Load Dashboard</button>
          <button onClick={fetchMeals}>Load Meals</button>
          <button onClick={logout}>Logout</button>
          <p style={{ color: 'red' }}>{message}</p>

          {dashboard && (
            <div style={{ marginTop: 12 }}>
              <h3>Dashboard</h3>
              <pre>{JSON.stringify(dashboard, null, 2)}</pre>
            </div>
          )}

          {meals && (
            <div style={{ marginTop: 12 }}>
              <h3>Meals</h3>
              <ul>
                {meals.map(m => (
                  <li key={m.id}>{m.name} — {m.calories} cal</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
