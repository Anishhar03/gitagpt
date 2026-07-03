import {
  Archive, BookMarked, BookOpen, ChevronRight, LogOut, Menu, MessageSquarePlus, Settings, X,
} from 'lucide-react';


export function Sidebar({
  open, conversations, selectedId, view, user, onSelect, onNew, onView, onClose, onLogout, onArchive,
}) {
  return (
    <>
      <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <span><BookOpen size={19} /></span><strong>Gita GPT</strong>
          <button className="icon-button mobile-close" onClick={onClose} title="Close navigation"><X size={19} /></button>
        </div>
        <button className="new-chat-button" onClick={onNew}><MessageSquarePlus size={17} /> New reflection</button>

        <nav className="primary-nav" aria-label="Workspace views">
          <button className={view === 'chat' ? 'active' : ''} onClick={() => onView('chat')}><BookOpen size={17} /> Dialogue</button>
          <button className={view === 'bookmarks' ? 'active' : ''} onClick={() => onView('bookmarks')}><BookMarked size={17} /> Saved passages</button>
          {user.role === 'admin' && <button className={view === 'admin' ? 'active' : ''} onClick={() => onView('admin')}><Settings size={17} /> Knowledge base</button>}
        </nav>

        <div className="conversation-section">
          <span className="nav-label">Recent conversations</span>
          <div className="conversation-list">
            {conversations.map((conversation) => (
              <div className={`conversation-row ${selectedId === conversation.id && view === 'chat' ? 'active' : ''}`} key={conversation.id}>
                <button onClick={() => onSelect(conversation.id)}>
                  <span>{conversation.title}</span><ChevronRight size={14} />
                </button>
                <button className="archive-button" onClick={() => onArchive(conversation.id)} title="Archive conversation"><Archive size={14} /></button>
              </div>
            ))}
            {!conversations.length && <p className="empty-nav">No conversations yet.</p>}
          </div>
        </div>

        <div className="sidebar-user">
          <div className="avatar">{user.display_name.slice(0, 1).toUpperCase()}</div>
          <div><strong>{user.display_name}</strong><span>{user.role}</span></div>
          <button className="icon-button" onClick={onLogout} title="Sign out"><LogOut size={17} /></button>
        </div>
      </aside>
      {open && <button className="sidebar-scrim" onClick={onClose} aria-label="Close navigation" />}
    </>
  );
}


export function MobileMenuButton({ onClick }) {
  return <button className="icon-button mobile-menu" onClick={onClick} title="Open navigation"><Menu size={20} /></button>;
}
