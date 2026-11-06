import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from '../src/App'

// Mock fetch
global.fetch = vi.fn((url) => {
  if (url === '/api/health') {
    return Promise.resolve({ json: () => Promise.resolve({ status: 'ok' }) })
  }
  if (url === '/api/items') {
    return Promise.resolve({
      json: () => Promise.resolve([
        { id: 1, name: 'Learn Docker' },
        { id: 2, name: 'Learn Jenkins' },
      ])
    })
  }
  return Promise.reject(new Error('not found'))
})

describe('App', () => {
  it('renders the title', async () => {
    render(<App />)
    await waitFor(() => {
      expect(screen.getByText('Jenkins CI/CD Demo')).toBeInTheDocument()
    })
  })

  it('shows backend health status', async () => {
    render(<App />)
    await waitFor(() => {
      expect(screen.getByText('ok')).toBeInTheDocument()
    })
  })
})