import { createContext, useContext, useState } from 'react'

const ProfileContext = createContext(null)

const DEFAULT_COLORS = [
  '#ef4444','#f97316','#f59e0b','#16a34a',
  '#0891b2','#4f46e5','#9333ea','#db2777',
]

function randomColor() {
  return DEFAULT_COLORS[Math.floor(Math.random() * DEFAULT_COLORS.length)]
}

export function ProfileProvider({ children }) {
  const [profile, setProfile] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('quiz_profile') || '{}')
      return { color: saved.color || randomColor() }
    } catch {
      return { color: randomColor() }
    }
  })

  function setColor(color) {
    const next = { ...profile, color }
    setProfile(next)
    localStorage.setItem('quiz_profile', JSON.stringify(next))
  }

  return (
    <ProfileContext.Provider value={{ profile, setColor }}>
      {children}
    </ProfileContext.Provider>
  )
}

export const useProfile = () => useContext(ProfileContext)