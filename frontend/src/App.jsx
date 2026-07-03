import { useCallback, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AlertCircle, Check, X } from 'lucide-react';

import { api } from './api';
import { AuthScreen } from './AuthScreen';
import { ChatView } from './ChatView';
import { AdminView, BookmarksView } from './KnowledgeViews';
import { MobileMenuButton, Sidebar } from './Sidebar';


const TOKEN_KEY = 'gitagpt_access_token';
const VISITOR_KEY = 'gitagpt_visitor_id';


function visitorEmail() {
  let visitorId = localStorage.getItem(VISITOR_KEY);
  if (!visitorId) {
    visitorId = crypto.randomUUID();
    localStorage.setItem(VISITOR_KEY, visitorId);
  }
  return `${visitorId}@demo.gitagpt.local`;
}


function Workspace({ token, user, onLogout, imageUrl }) {
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState(null);
  const [view, setView] = useState('chat');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notice, setNotice] = useState(null);

  const conversations = useQuery({ queryKey: ['conversations'], queryFn: () => api.conversations(token) });
  const activeId = selectedId || conversations.data?.[0]?.id || null;

  const conversation = useQuery({
    queryKey: ['conversation', activeId],
    queryFn: () => api.conversation(token, activeId),
    enabled: Boolean(activeId && view === 'chat'),
  });
  const daily = useQuery({ queryKey: ['daily'], queryFn: () => api.daily(token), retry: 3 });
  const bookmarks = useQuery({
    queryKey: ['bookmarks'], queryFn: () => api.bookmarks(token), enabled: view === 'bookmarks',
  });
  const documents = useQuery({
    queryKey: ['documents'], queryFn: () => api.documents(token), enabled: user.role === 'admin', refetchInterval: view === 'admin' ? 4000 : false,
  });

  const createConversation = useMutation({
    mutationFn: (payload = {}) => api.createConversation(token, { title: 'New reflection', intention: '', ...payload }),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      setSelectedId(created.id);
      setView('chat');
      setSidebarOpen(false);
    },
  });
  const ask = useMutation({
    mutationFn: async ({ id, question }) => api.ask(token, id, question),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
    onError: (error) => setNotice({ type: 'error', message: error.message }),
  });
  const archive = useMutation({
    mutationFn: (id) => api.archiveConversation(token, id),
    onSuccess: (_, id) => {
      if (activeId === id) setSelectedId(null);
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
  const feedback = useMutation({
    mutationFn: ({ messageId, rating }) => api.feedback(token, messageId, rating),
    onSuccess: () => setNotice({ type: 'success', message: 'Feedback saved. Thank you.' }),
  });
  const bookmark = useMutation({
    mutationFn: (chunkId) => api.bookmark(token, chunkId),
    onSuccess: () => {
      setNotice({ type: 'success', message: 'Passage saved to your library.' });
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] });
    },
    onError: (error) => setNotice({ type: 'error', message: error.status === 409 ? 'This passage is already saved.' : error.message }),
  });
  const removeBookmark = useMutation({
    mutationFn: (id) => api.removeBookmark(token, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bookmarks'] }),
  });
  const upload = useMutation({
    mutationFn: (form) => api.uploadDocument(token, form),
    onSuccess: () => {
      setNotice({ type: 'success', message: 'Document queued for indexing.' });
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: (error) => setNotice({ type: 'error', message: error.message }),
  });
  const deleteDocument = useMutation({
    mutationFn: (id) => api.deleteDocument(token, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
  });

  async function sendQuestion(question) {
    let id = activeId;
    if (!id) {
      const created = await createConversation.mutateAsync();
      id = created.id;
    }
    await ask.mutateAsync({ id, question });
  }

  async function exportConversation() {
    if (!activeId) return;
    const blob = await api.exportConversation(token, activeId);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `gita-gpt-${activeId}.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const selectedConversation = conversation.data || (activeId ? { id: activeId, title: 'Loading...', messages: [] } : null);

  return (
    <div className="workspace-shell">
      <Sidebar
        open={sidebarOpen}
        conversations={conversations.data || []}
        selectedId={activeId}
        view={view}
        user={user}
        onSelect={(id) => { setSelectedId(id); setView('chat'); setSidebarOpen(false); }}
        onNew={() => createConversation.mutate()}
        onView={(next) => { setView(next); setSidebarOpen(false); }}
        onClose={() => setSidebarOpen(false)}
        onLogout={onLogout}
        onArchive={(id) => archive.mutate(id)}
      />
      <main className="main-stage">
        <MobileMenuButton onClick={() => setSidebarOpen(true)} />
        {notice && (
          <div className={`toast toast-${notice.type}`} role="status">
            {notice.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
            <span>{notice.message}</span>
            <button onClick={() => setNotice(null)} title="Dismiss"><X size={15} /></button>
          </div>
        )}
        {view === 'chat' && (
          <ChatView
            conversation={selectedConversation}
            daily={daily.data}
            imageUrl={imageUrl}
            pending={ask.isPending || createConversation.isPending}
            onSend={sendQuestion}
            onFeedback={(messageId, rating) => feedback.mutate({ messageId, rating })}
            onBookmark={(chunkId) => bookmark.mutate(chunkId)}
            onExport={exportConversation}
          />
        )}
        {view === 'bookmarks' && <BookmarksView bookmarks={bookmarks.data || []} onRemove={(id) => removeBookmark.mutate(id)} />}
        {view === 'admin' && user.role === 'admin' && (
          <AdminView
            documents={documents.data || []}
            uploadPending={upload.isPending}
            onUpload={(form) => upload.mutateAsync(form)}
            onDelete={(id) => deleteDocument.mutate(id)}
          />
        )}
      </main>
    </div>
  );
}


export function App() {
  const queryClient = useQueryClient();
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY));
  const [loginError, setLoginError] = useState('');
  const config = useQuery({ queryKey: ['runtime-config'], queryFn: api.config });
  const me = useQuery({ queryKey: ['me', token], queryFn: () => api.me(token), enabled: Boolean(token), retry: false });

  const acceptLogin = useCallback((result) => {
    sessionStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    setLoginError('');
  }, []);
  const devLogin = useMutation({
    mutationFn: (name) => api.devLogin({ email: visitorEmail(), display_name: name }),
    onSuccess: acceptLogin,
    onError: (error) => setLoginError(error.message),
  });
  const googleLogin = useMutation({
    mutationFn: api.googleLogin,
    onSuccess: acceptLogin,
    onError: (error) => setLoginError(error.message),
  });

  const logout = useCallback(() => {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
    queryClient.clear();
  }, [queryClient]);

  if (config.isLoading || (token && me.isLoading)) return <div className="app-loading"><span /><strong>Preparing Gita GPT</strong></div>;
  if (config.isError) return <div className="fatal-state"><AlertCircle size={30} /><strong>Gita GPT is unavailable</strong><p>{config.error.message}</p></div>;
  if (!token || !me.data) {
    return (
      <AuthScreen
        config={{ ...config.data, imageUrl: `${api.origin}/assets/krishna` }}
        onDevLogin={(name) => devLogin.mutate(name)}
        onGoogleLogin={(credential) => googleLogin.mutate(credential)}
        error={loginError || (me.error?.status === 401 ? 'Your session expired. Sign in again.' : '')}
        loading={devLogin.isPending || googleLogin.isPending}
      />
    );
  }
  return <Workspace token={token} user={me.data} onLogout={logout} imageUrl={`${api.origin}/assets/krishna`} />;
}


export default App;
