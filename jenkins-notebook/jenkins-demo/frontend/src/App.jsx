import { useState, useEffect } from 'react'

function App() {
  const [items, setItems] = useState([])
  const [health, setHealth] = useState('')

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data.status))
      .catch(() => setHealth('unreachable'))

    fetch('/api/items')
      .then(res => res.json())
      .then(data => setItems(data))
      .catch(() => setItems([]))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center">Jenkins CI/CD Demo</h1>

        <div className="mb-4 p-3 bg-green-50 rounded text-center">
          Backend: <span className="font-mono font-bold">{health || 'loading...'}</span>
        </div>

        <ul className="space-y-2">
          {items.map(item => (
            <li key={item.id} className="p-3 bg-gray-50 rounded flex justify-between">
              <span className="text-gray-500">#{item.id}</span>
              <span className="font-medium">{item.name}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default App