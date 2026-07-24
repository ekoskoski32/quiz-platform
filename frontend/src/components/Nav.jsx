import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useProfile } from '../context/ProfileContext'

const AVATAR_COLORS = [
  '#ef4444','#f97316','#f59e0b','#16a34a',
  '#0891b2','#4f46e5','#9333ea','#db2777',
]

function Avatar({ user }) {
  const { profile, setColor } = useProfile()
  const [open, setOpen] = useState(false)
  const initials = user.username.startsWith('guest_')
    ? 'G'
    : user.username.slice(0, 2).toUpperCase()

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2"
        style={{ backgroundColor: profile.color }}
        aria-label="Open profile options"
        aria-expanded={open}
      >
        {initials}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-11 z-20 bg-white rounded-2xl shadow-xl border border-stone-200 p-4 w-56">
            <p className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-1">
              {user.username.startsWith('guest_') ? 'Guest session' : 'Signed in as'}
            </p>
            <p className="text-sm font-medium text-stone-900 mb-3 truncate">{user.username}</p>
            <p className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-2">Avatar color</p>
            <div className="grid grid-cols-4 gap-2 mb-3">
              {AVATAR_COLORS.map(c => (
                <button
                  key={c}
                  onClick={() => { setColor(c); setOpen(false) }}
                  className="w-8 h-8 rounded-full focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-1"
                  style={{ backgroundColor: c, outline: profile.color === c ? '2px solid #f59e0b' : 'none', outlineOffset: '2px' }}
                  aria-label={`Set avatar color to ${c}`}
                />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default function Nav() {
  const { user } = useAuth()
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const isGuest = !user || user.username?.startsWith('guest_')

  const tab = (label, to) => {
    const active = pathname === to || (to === '/quiz' && pathname === '/')
    return (
      <Link
        to={to}
        className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
          active
            ? 'bg-amber-100 text-amber-700'
            : 'text-stone-500 hover:text-stone-900 hover:bg-stone-100'
        }`}
      >
        {label}
      </Link>
    )
  }

  return (
    <nav className="sticky top-0 z-30 bg-white border-b border-stone-200 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto h-14 flex items-center justify-between gap-4">
        {/* Left — brand */}
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <span className="w-7 h-7 rounded-lg bg-amber-400 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </span>
          <span className="font-semibold text-stone-900 text-sm">Quiz Platform</span>
        </Link>

        {/* Center — tabs */}
        <div className="flex items-center gap-1">
          {tab('Quiz', '/')}
          {isGuest ? (
            <span
              className="px-4 py-1.5 rounded-full text-sm font-medium text-stone-300 cursor-not-allowed select-none"
              title="Sign in to view history"
            >
              History
            </span>
          ) : (
            tab('History', '/history')
          )}
        </div>

        {/* Right — avatar or sign in */}
        <div className="shrink-0">
          {isGuest ? (
            <Link
              to="/login"
              className="px-4 py-1.5 rounded-full text-sm font-medium bg-amber-400 text-white hover:bg-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2"
            >
              Sign in
            </Link>
          ) : (
            <Avatar user={user} />
          )}
        </div>
      </div>
    </nav>
  )
}