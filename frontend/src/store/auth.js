import { create } from 'zustand'

const saved = JSON.parse(localStorage.getItem('user') || 'null')

export const useAuth = create((set) => ({
  user: saved,
  token: localStorage.getItem('token'),

  login: (d) => {
    localStorage.setItem('token', d.access_token)
    const u = {
      name: d.name,
      role: d.role,
      must_change_password: d.must_change_password,
    }
    localStorage.setItem('user', JSON.stringify(u))
    set({ user: u, token: d.access_token })
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ user: null, token: null })
  },

  setMustChange: (v) => {
    const current = JSON.parse(localStorage.getItem('user') || 'null') || {}
    const u = { ...current, must_change_password: v }
    localStorage.setItem('user', JSON.stringify(u))
    set({ user: u })
  },
}))