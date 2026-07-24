import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import Nav from '../components/Nav'

const CATEGORY_ICONS = {
  'Geography':   '🌍',
  'Science':     '🔬',
  'Math':        '➗',
  'History':     '📜',
  'Technology':  '💻',
  'Biology':     '🧬',
  'Art':         '🎨',
  'Pop Culture': '🎬',
}

export default function Home() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(null)
  const [err, setErr] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/questions/categories/').then(r => setCategories(r.data)).finally(() => setLoading(false))
  }, [])

  async function startQuiz(category = 'random') {
    setStarting(category)
    setErr('')
    try {
      const body = category === 'random' ? {} : { category }
      const { data } = await api.post('/attempts/', body)
      navigate(`/quiz/${data.id}`)
    } catch (e) {
      const msg = e.response?.data?.error || 'Could not start quiz.'
      setErr(msg)
      setStarting(null)
    }
  }

  return (
    <div className="min-h-screen bg-[#f7f6f3]">
      <Nav />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10">

        {/* Hero */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-stone-900 mb-2">Pick a category</h1>
          <p className="text-stone-500">5 questions per quiz, graded instantly.</p>
        </div>

        {err && (
          <p role="alert" className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2 mb-2">{err}</p>
        )}

        {/* Random card */}
        <button
          onClick={() => startQuiz('random')}
          disabled={!!starting}
          className="w-full mb-6 flex items-center gap-4 bg-amber-400 hover:bg-amber-500 disabled:opacity-60 text-white rounded-2xl px-6 py-5 text-left focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 shadow-sm"
        >
          <span className="text-3xl">🎲</span>
          <div>
            <p className="font-semibold text-lg leading-tight">
              {starting === 'random' ? 'Starting…' : 'Random Quiz'}
            </p>
            <p className="text-amber-100 text-sm">Mix of all categories</p>
          </div>
          <svg className="ml-auto w-5 h-5 text-amber-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7"/>
          </svg>
        </button>

        {/* Category grid */}
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-24 bg-stone-100 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {categories.map(({ category, count }) => (
              <button
                key={category}
                onClick={() => startQuiz(category)}
                disabled={!!starting}
                className="group flex flex-col gap-2 bg-white hover:bg-amber-50 border border-stone-200 hover:border-amber-300 disabled:opacity-60 rounded-2xl px-5 py-4 text-left focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 shadow-sm"
              >
                <span className="text-2xl">{CATEGORY_ICONS[category] || '📚'}</span>
                <div>
                  <p className="font-semibold text-stone-900 text-sm group-hover:text-amber-700 leading-tight">
                    {starting === category ? 'Starting…' : category}
                  </p>
                  <p className="text-xs text-stone-400">{count} questions</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}