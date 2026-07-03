import { useEffect, useRef, useState } from 'react';
import { Bookmark, Download, ExternalLink, Send, Sparkles, ThumbsDown, ThumbsUp, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';


export function ChatView({ conversation, daily, imageUrl, pending, onSend, onFeedback, onBookmark, onExport }) {
  const [question, setQuestion] = useState('');
  const [activeSources, setActiveSources] = useState([]);
  const endRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [conversation?.messages, pending]);

  async function submit(event) {
    event.preventDefault();
    const value = question.trim();
    if (!value || pending) return;
    setQuestion('');
    await onSend(value);
  }

  return (
    <div className="chat-layout">
      <header className="chat-header">
        <div><span className="eyebrow">Dialogue</span><h1>{conversation?.title || 'New reflection'}</h1></div>
        {conversation && <button className="icon-text-button" onClick={onExport}><Download size={16} /> Export</button>}
      </header>

      <div className="message-scroll">
        {!conversation?.messages?.length && (
          <>
            {daily && (
              <section className="daily-wisdom" style={{ '--wisdom-image': `url('${imageUrl}')` }}>
                <span className="eyebrow light"><Sparkles size={14} /> Daily wisdom</span>
                <blockquote>{daily.source.excerpt.slice(0, 360)}</blockquote>
                <p>{daily.reflection}</p>
              </section>
            )}
            <section className="prompt-starters">
              <h2>What would you like to understand?</h2>
              <div>
                {['How can I act without fear of the outcome?', 'What does duty mean when every option feels difficult?', 'How can I remain steady during uncertainty?'].map((prompt) => (
                  <button key={prompt} onClick={() => setQuestion(prompt)}>{prompt}</button>
                ))}
              </div>
            </section>
          </>
        )}

        {conversation?.messages?.map((message) => (
          <article className={`message message-${message.role}`} key={message.id}>
            <div className="message-label">{message.role === 'user' ? 'You' : 'Gita GPT'}</div>
            <div className="message-body"><ReactMarkdown>{message.content}</ReactMarkdown></div>
            {message.role === 'assistant' && (
              <div className="message-actions">
                {!!message.citations?.length && <button onClick={() => setActiveSources(message.citations)}><ExternalLink size={14} /> {message.citations.length} sources</button>}
                <button onClick={() => onFeedback(message.id, 1)} title="Helpful"><ThumbsUp size={14} /></button>
                <button onClick={() => onFeedback(message.id, -1)} title="Not helpful"><ThumbsDown size={14} /></button>
                <span>{message.provider} {message.latency_ms ? `- ${message.latency_ms} ms` : ''}</span>
              </div>
            )}
          </article>
        ))}
        {pending && <div className="thinking"><span /><span /><span /> Retrieving and reflecting</div>}
        <div ref={endRef} />
      </div>

      <form className="chat-composer" onSubmit={submit}>
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about duty, fear, purpose, grief, focus..." maxLength={2000} rows={2} />
        <button type="submit" disabled={pending || !question.trim()} title="Send question"><Send size={18} /></button>
      </form>

      {activeSources.length > 0 && (
        <aside className="source-drawer">
          <div className="source-head"><div><span className="eyebrow">Retrieved context</span><h2>Source passages</h2></div><button className="icon-button" onClick={() => setActiveSources([])} title="Close sources"><X size={18} /></button></div>
          <div className="source-list">
            {activeSources.map((source, index) => (
              <article key={source.chunk_id}>
                <div><strong>Source {index + 1}</strong><span>{source.title}{source.page_number ? ` - Page ${source.page_number}` : ''}</span></div>
                <p>{source.excerpt}</p>
                <button onClick={() => onBookmark(source.chunk_id)}><Bookmark size={14} /> Save passage</button>
              </article>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
}
