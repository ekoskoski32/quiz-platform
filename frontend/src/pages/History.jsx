import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'
import Nav from '../components/Nav'

function StatBar({ label, pct, correct, total }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-stone-700 font-medium">{label}</span>
        <span className="text-sm text-stone-500">{correct}/{total} · {pct}%</span>
      </div>
      <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${pct}%`,
            backgroundColor: pct >= 80 ? '#16a34a' : pct >= 60 ? '#f59e0b' : '#ef4444'
          }}
        />
      </div>
    </div>
  )
}

function LockedState() {
  return (
    <div className="min-h-screen bg-[#f7f6f3]">
      <Nav />
      <div className="max-w-md mx-auto px-4 py-24 text-center">
        <div className="w-16 h-16 rounded-2xl bg-stone-100 flex items-center justify-center mx-auto mb-6">
          <svg className="w-8 h-8 text-stone-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
          </svg>
        </div>
        <h2 className="text-xl font-bold text-stone-900 mb-2">Sign in to view history</h2>
        <p className="text-stone-500 text-sm mb-8">Your quiz history and stats are saved to your account. Sign in to track your progress over time.</p>
        <Link to="/login"
          className="inline-block bg-amber-400 hover:bg-amber-500 text-white rounded-2xl px-8 py-3 font-semibold text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 transition-colors">
          Sign in
        </Link>
      </div>
    </div>
  )
}

export default function History() {
  const { user } = useAuth()
  const isGuest = !user || user.username?.startsWith('guest_')
  const [attempts, setAttempts] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isGuest) return
    Promise.all([api.get('/attempts/'), api.get('/attempts/stats/')])
      .then(([a, s]) => { setAttempts(a.data); setStats(s.data) })
      .finally(() => setLoading(false))
  }, [isGuest])

  if (isGuest) return <LockedState />

  return (
    <div className="min-h-screen bg-[#f7f6f3]">
      <Nav />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        <h1 className="text-2xl font-bold text-stone-900">History</h1>

        {/* Stats cards */}
        {stats && (
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white border border-stone-200 rounded-2xl p-5 shadow-sm">
              <p className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1">Overall score</p>
              <p className="text-4xl font-bold text-amber-500">{stats.overall_pct}<span className="text-xl text-stone-300">%</span></p>
              <p className="text-xs text-stone-400 mt-1">{stats.total_attempts} quiz{stats.total_attempts !== 1 ? 'zes' : ''} taken</p>
            </div>
            <div className="bg-white border border-stone-200 rounded-2xl p-5 shadow-sm">
              <p className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1">Strongest subject</p>
              {stats.by_category.length > 0 ? (
                <>
                  <p className="text-2xl font-bold text-stone-900 mt-1">{stats.by_category[0].category}</p>
                  <p className="text-xs text-green-600 font-medium mt-1">{stats.by_category[0].pct}% correct</p>
                </>
              ) : (
                <p className="text-sm text-stone-400 mt-2">Take a quiz first</p>
              )}
            </div>
          </div>
        )}

        {/* Subject breakdown */}
        {stats?.by_category.length > 0 && (
          <div className="bg-white border border-stone-200 rounded-2xl p-5 shadow-sm space-y-4">
            <h2 className="text-sm font-semibold text-stone-700">Performance by subject</h2>
            {stats.by_category.map(c => (
              <StatBar key={c.category} label={c.category} pct={c.pct} correct={c.correct} total={c.total} />
            ))}
          </div>
        )}

        {/* Attempt list */}
        <div>
          <h2 className="text-sm font-semibold text-stone-700 mb-3">All attempts</h2>
          {loading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => <div key={i} className="h-16 bg-stone-100 rounded-2xl animate-pulse" />)}
            </div>
          ) : attempts.length === 0 ? (
            <div className="text-center py-12 text-stone-400">
              <p>No quizzes yet.</p>
              <Link to="/" className="mt-3 inline-block text-amber-500 hover:underline font-medium text-sm">Start one →</Link>
            </div>
          ) : (
            <ul className="space-y-2">
              {attempts.map(a => (
                <li key={a.id}>
                  <Link to={`/results/${a.id}`}
                    className="flex items-center justify-between bg-white border border-stone-200 hover:border-amber-300 rounded-2xl px-5 py-4 group transition-colors shadow-sm"
                    aria-label={`Attempt ${a.id}`}>
                    <div>
                      <p className="text-sm font-semibold text-stone-800 group-hover:text-amber-700">Attempt #{a.id}</p>
                      <p className="text-xs text-stone-400 mt-0.5">
                        {new Date(a.started_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    {a.submitted_at ? (
                      <span className="text-lg font-bold text-amber-500">{a.score} <span className="text-sm text-stone-300 font-normal">/ 5</span></span>
                    ) : (
                      <span className="text-xs bg-stone-100 text-stone-500 rounded-full px-2.5 py-1">In progress</span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}