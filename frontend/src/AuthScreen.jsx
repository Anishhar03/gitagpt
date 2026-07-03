import { useEffect, useRef, useState } from 'react';
import { ArrowRight, BookOpen, ShieldCheck, Sparkles } from 'lucide-react';


export function AuthScreen({ config, onDevLogin, onGoogleLogin, error, loading }) {
  const [name, setName] = useState('Arjuna');
  const googleButton = useRef(null);

  useEffect(() => {
    if (config?.auth_mode !== 'google' || !config.google_client_id) return undefined;
    const initialize = () => {
      window.google?.accounts.id.initialize({
        client_id: config.google_client_id,
        callback: ({ credential }) => onGoogleLogin(credential),
      });
      if (googleButton.current) {
        window.google?.accounts.id.renderButton(googleButton.current, {
          theme: 'outline', size: 'large', width: 320,
        });
      }
    };
    if (window.google?.accounts) {
      initialize();
      return undefined;
    }
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.onload = initialize;
    document.head.appendChild(script);
    return () => script.remove();
  }, [config, onGoogleLogin]);

  return (
    <main className="auth-screen" style={{ backgroundImage: `linear-gradient(90deg, rgba(10, 32, 27, .96), rgba(10, 32, 27, .5)), url('${config?.imageUrl || ''}')` }}>
      <section className="auth-content">
        <div className="auth-brand"><BookOpen size={22} /><strong>Gita GPT</strong></div>
        <span className="eyebrow light">Grounded reflection</span>
        <h1>Clarity for the question in front of you.</h1>
        <p className="auth-lede">Explore the Bhagavad Gita through source-linked dialogue, practical reflection, and a knowledge base you can inspect.</p>
        <div className="auth-features">
          <span><ShieldCheck size={17} /> Source citations</span>
          <span><Sparkles size={17} /> Provider fallback</span>
        </div>

        <div className="auth-action">
          {config?.auth_mode === 'google' ? (
            <div ref={googleButton} className="google-button" />
          ) : (
            <form onSubmit={(event) => { event.preventDefault(); onDevLogin(name); }}>
              <label htmlFor="display-name">Display name</label>
              <div className="auth-input-row">
                <input id="display-name" value={name} maxLength={120} onChange={(event) => setName(event.target.value)} />
                <button type="submit" disabled={loading || !name.trim()} title="Continue">
                  <ArrowRight size={19} />
                </button>
              </div>
            </form>
          )}
          {error && <p className="auth-error" role="alert">{error}</p>}
        </div>
      </section>
    </main>
  );
}
