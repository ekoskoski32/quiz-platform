import { useRef } from 'react'

function SingleChoice({ question, value, onChange }) {
  return (
    <fieldset className="mt-3 space-y-2">
      <legend className="sr-only">{question.prompt}</legend>
      {question.choices.map(c => (
        <label key={c.id}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl border cursor-pointer transition-all ${
            value === c.id
              ? 'border-amber-400 bg-amber-50'
              : 'border-stone-200 bg-white hover:border-amber-300 hover:bg-amber-50/50'
          }`}>
          <input type="radio" name={`q-${question.id}`} value={c.id}
            checked={value === c.id} onChange={() => onChange(c.id)}
            className="accent-amber-400 focus:ring-amber-400" />
          <span className="text-sm text-stone-800">{c.text}</span>
        </label>
      ))}
    </fieldset>
  )
}

function MultipleChoice({ question, value = [], onChange }) {
  function toggle(id) {
    onChange(value.includes(id) ? value.filter(v => v !== id) : [...value, id])
  }
  return (
    <fieldset className="mt-3">
      <legend className="sr-only">{question.prompt}</legend>
      <p className="text-xs text-stone-400 mb-2">Select all that apply</p>
      <div className="space-y-2">
        {question.choices.map(c => (
          <label key={c.id}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl border cursor-pointer transition-all ${
              value.includes(c.id)
                ? 'border-amber-400 bg-amber-50'
                : 'border-stone-200 bg-white hover:border-amber-300 hover:bg-amber-50/50'
            }`}>
            <input type="checkbox" value={c.id} checked={value.includes(c.id)}
              onChange={() => toggle(c.id)}
              className="accent-amber-400 focus:ring-amber-400 rounded" />
            <span className="text-sm text-stone-800">{c.text}</span>
          </label>
        ))}
      </div>
    </fieldset>
  )
}

function NumericalInput({ question, value, onChange }) {
  return (
    <div className="mt-3">
      <label htmlFor={`num-${question.id}`} className="sr-only">{question.prompt}</label>
      <input id={`num-${question.id}`} type="number" step="any"
        value={value || ''} onChange={e => onChange(e.target.value)}
        placeholder="Enter a number…"
        className="w-full border border-stone-300 rounded-xl px-4 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400" />
    </div>
  )
}

function TextResponse({ question, value, onChange }) {
  return (
    <div className="mt-3">
      <label htmlFor={`text-${question.id}`} className="sr-only">{question.prompt}</label>
      <textarea id={`text-${question.id}`} value={value || ''}
        onChange={e => onChange(e.target.value)}
        placeholder="Write your answer here…" rows={4}
        className="w-full border border-stone-300 rounded-xl px-4 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400 resize-none" />
    </div>
  )
}

function ImageUpload({ question, value, onChange }) {
  const inputRef = useRef()
  return (
    <div className="mt-3 space-y-2">
      <label htmlFor={`img-${question.id}`} className="block text-sm text-stone-500">Upload an image:</label>
      <input ref={inputRef} id={`img-${question.id}`} type="file" accept="image/*"
        onChange={e => onChange(e.target.files[0] || null)}
        aria-label="Upload your answer image"
        className="block w-full text-sm text-stone-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-amber-50 file:text-amber-700 hover:file:bg-amber-100 focus:outline-none" />
      {value && (
        <img src={URL.createObjectURL(value)} alt="Preview"
          className="mt-2 max-h-40 rounded-xl border border-stone-200 object-contain" />
      )}
    </div>
  )
}

const TYPE_LABEL = { single: 'Single choice', multiple: 'Multiple choice', numerical: 'Numerical', text: 'Free response', image: 'Image upload' }

export default function QuestionCard({ question, index, response, onResponseChange }) {
  const RENDERERS = { single: SingleChoice, multiple: MultipleChoice, numerical: NumericalInput, text: TextResponse, image: ImageUpload }
  const Renderer = RENDERERS[question.type]

  return (
    <div className="bg-white rounded-2xl border border-stone-200 shadow-sm p-5">
      <div className="flex items-start gap-4">
        <span className="shrink-0 w-8 h-8 rounded-xl bg-amber-100 text-amber-700 font-bold text-sm flex items-center justify-center">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap gap-1.5 mb-2.5">
            <span className="text-xs bg-stone-100 text-stone-500 rounded-full px-2.5 py-0.5">{question.category}</span>
            <span className={`text-xs rounded-full px-2.5 py-0.5 capitalize ${
              question.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
              question.difficulty === 'medium' ? 'bg-amber-100 text-amber-700' :
              'bg-red-100 text-red-700'}`}>
              {question.difficulty}
            </span>
            <span className="text-xs bg-stone-100 text-stone-400 rounded-full px-2.5 py-0.5">{TYPE_LABEL[question.type]}</span>
          </div>
          <p className="text-stone-900 font-medium text-sm leading-relaxed">{question.prompt}</p>
          {Renderer && <Renderer question={question} value={response} onChange={onResponseChange} />}
        </div>
      </div>
    </div>
  )
}