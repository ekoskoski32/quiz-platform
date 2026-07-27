import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../api/client'
import Nav from '../components/Nav'
import QuestionCard from '../components/QuestionCard'

export default function Quiz() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState(null)
  const [responses, setResponses] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get(`/attempts/${id}/`).then(r => setAttempt(r.data))
  }, [id])

  function setResponse(questionId, value) {
    setResponses(prev => ({ ...prev, [questionId]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      const formData = new FormData()
      const answers = attempt.questions.map(q => {
        const res = responses[q.id]
        if (q.type === 'single') return { question_id: q.id, selected_choice_ids: res ? [res] : [] }
        if (q.type === 'multiple') return { question_id: q.id, selected_choice_ids: res || [] }
        return { question_id: q.id, text_response: res || '' }
      })
      formData.append('answers', JSON.stringify(answers))
      attempt.questions.forEach(q => {
        if (q.type === 'image' && responses[q.id] instanceof File) {
          formData.append(`image_${q.id}`, responses[q.id])
        }
      })
      const { data } = await api.post(`/attempts/${id}/submit/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      navigate(`/results/${data.id}`)
    } catch (err) {
      setError(err.response?.data?.error || 'Submission failed.')
      setSubmitting(false)
    }
  }

  if (!attempt) return (
    <div className="min-h-screen bg-[#f7f6f3]">
      <Nav />
      <div className="flex items-center justify-center h-64">
        <div className="flex gap-1.5">
          {[0,1,2].map(i => (
            <div key={i} className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: `${i*0.15}s` }} />
          ))}
        </div>
      </div>
    </div>
  )

  const answered = attempt.questions.filter(q => {
    const r = responses[q.id]
    if (q.type === 'single') return !!r
    if (q.type === 'multiple') return r?.length > 0
    if (q.type === 'image') return r instanceof File
    return !!r?.trim()
  }).length
  const total = attempt.questions.length

  return (
    <div className="min-h-screen bg-[#f7f6f3]">
      <Nav />
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">

        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-xl font-bold text-stone-900">{attempt.questions[0]?.category || 'Quiz'}</h1>
            <span className="text-sm text-stone-500">{answered}/{total} answered</span>
          </div>
          {/* Progress bar */}
          <div className="h-1.5 bg-stone-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-amber-400 rounded-full transition-all duration-300"
              style={{ width: `${(answered / total) * 100}%` }}
            />
          </div>
        </div>

        {error && (
          <p role="alert" className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2 mb-4">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {attempt.questions.map((q, i) => (
            <QuestionCard
              key={q.id}
              question={q}
              index={i}
              response={responses[q.id]}
              onResponseChange={val => setResponse(q.id, val)}
            />
          ))}

          <button type="submit" disabled={submitting}
            className="w-full bg-amber-400 hover:bg-amber-500 text-white rounded-2xl py-3.5 font-semibold text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 disabled:opacity-50 mt-2">
            {submitting ? 'Grading…' : 'Submit Quiz'}
          </button>
        </form>
      </div>
    </div>
  )
}