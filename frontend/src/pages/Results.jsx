import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api/client'
import Nav from '../components/Nav'

function useCountUp(target, duration = 800) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    if (target === 0) return
    const steps = 30
    const step = target / steps
    const interval = duration / steps
    let current = 0
    const timer = setInterval(() => {
      current = Math.min(current + step, target)
      setCount(Math.round(current * 10) / 10)
      if (current >= target) clearInterval(timer)
    }, interval)
    return () => clearInterval(timer)
  }, [target])
  return count
}

function ScoreCard({ score, total }) {
  const animated = useCountUp(score)
  const pct = score / total
  const { bg, text, ring, label } = pct >= 0.8
    ? { bg: 'bg-green-50', text: 'text-green-600', ring: 'ring-green-200', label: '🎉 Excellent!' }
    : pct >= 0.6
    ? { bg: 'bg-amber-50', text: 'text-amber-600', ring: 'ring-amber-200', label: '👍 Good job!' }
    : { bg: 'bg-red-50', text: 'text-red-500', ring: 'ring-red-200', label: '📚 Keep practicing!' }

  return (
    <div className={`${bg} ring-1 ${ring} rounded-2xl p-8 text-center`}>
      <p className="text-sm font-medium text-stone-500 mb-1">Your Score</p>
      <p className={`text-7xl font-bold ${text}`} aria-live="polite" aria-label={`${score} out of ${total}`}>
        {animated}
        <span className="text-3xl text-stone-300 font-medium"> / {total}</span>
      </p>
      <p className="mt-3 text-stone-600 font-medium">{label}</p>
    </div>
  )
}

function AnswerReview({ answer }) {
  const [expanded, setExpanded] = useState(false)
  const q = answer.question
  const correct = answer.is_correct === true
  const incorrect = answer.is_correct === false

  return (
    <div className={`bg-white rounded-2xl border shadow-sm overflow-hidden ${
      correct ? 'border-green-200' : incorrect ? 'border-red-200' : 'border-stone-200'
    }`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-stone-50 transition-colors"
        aria-expanded={expanded}
      >
        <span className="text-xl shrink-0" aria-hidden>
          {correct ? '✅' : incorrect ? '❌' : '⏳'}
        </span>
        <p className="flex-1 text-sm font-medium text-stone-800 line-clamp-1">{q.prompt}</p>
        <span className="text-xs text-stone-400 shrink-0">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="px-5 pb-5 space-y-3 border-t border-stone-100 pt-4">
          {/* User's answer */}
          {(q.type === 'text' || q.type === 'numerical') && answer.text_response && (
            <div>
              <p className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1">Your answer</p>
              <p className="text-sm text-stone-700 bg-stone-50 rounded-xl px-3 py-2">{answer.text_response}</p>
            </div>
          )}
          {(q.type === 'single' || q.type === 'multiple') && answer.selected_choices?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1">Your answer</p>
              <ul className="space-y-1">
                {answer.selected_choices.map(c => (
                  <li key={c.id} className="text-sm text-stone-700 bg-stone-50 rounded-xl px-3 py-2">{c.text}</li>
                ))}
              </ul>
            </div>
          )}
          {q.type === 'image' && answer.image_response && (
            <div>
              <p className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1">Your image</p>
              <img src={`http://localhost:8000${answer.image_response}`} alt="Your upload"
                className="max-h-32 rounded-xl border border-stone-200 object-contain" />
            </div>
          )}

          {/* Correct answer — only shown if wrong */}
          {incorrect && (
            <div>
              <p className="text-xs font-semibold text-green-600 uppercase tracking-wide mb-1">Correct answer</p>
              {q.correct_answer ? (
                <p className="text-sm text-stone-700 bg-green-50 rounded-xl px-3 py-2">{q.correct_answer}</p>
              ) : (
                <ul className="space-y-1">
                  {answer.correct_choices?.map(c => (
                    <li key={c.id} className="text-sm text-stone-700 bg-green-50 rounded-xl px-3 py-2">{c.text}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {answer.ai_feedback && (
            <p className="text-xs text-stone-400 italic border-t border-stone-100 pt-2">{answer.ai_feedback}</p>
          )}
        </div>
      )}
    </div>
  )
}

export default function Results() {
  const { id } = useParams()
  const [attempt, setAttempt] = useState(null)

  useEffect(() => {
    api.get(`/attempts/${id}/`).then(r => setAttempt(r.data))
  }, [id])

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

  return (
    <div className="min-h-screen bg-[#f7f6f3]">
      <Nav />
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        <ScoreCard score={attempt.score ?? 0} total={attempt.questions.length} />

        <div className="flex gap-3">
          <Link to="/"
            className="flex-1 text-center bg-amber-400 hover:bg-amber-500 text-white rounded-2xl py-3 font-semibold text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 transition-colors">
            New Quiz
          </Link>
          <Link to="/history"
            className="flex-1 text-center bg-white border border-stone-200 hover:border-stone-300 text-stone-700 rounded-2xl py-3 font-semibold text-sm focus:outline-none focus:ring-2 focus:ring-stone-300 focus:ring-offset-2 transition-colors">
            View History
          </Link>
        </div>

        <div>
          <h2 className="text-base font-semibold text-stone-800 mb-3">Review answers</h2>
          <div className="space-y-2">
            {attempt.answers.map(ans => <AnswerReview key={ans.id} answer={ans} />)}
          </div>
        </div>
      </div>
    </div>
  )
}