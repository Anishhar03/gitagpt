import { BookMarked, FileText, Trash2, UploadCloud } from 'lucide-react';
import { useState } from 'react';


export function BookmarksView({ bookmarks, onRemove }) {
  return (
    <section className="content-view">
      <header><span className="eyebrow">Personal library</span><h1>Saved passages</h1><p>Passages you marked for return and reflection.</p></header>
      <div className="bookmark-grid">
        {bookmarks.map((bookmark) => (
          <article key={bookmark.id}>
            <BookMarked size={18} />
            <blockquote>{bookmark.source.excerpt}</blockquote>
            <span>{bookmark.source.title}{bookmark.source.page_number ? ` - Page ${bookmark.source.page_number}` : ''}</span>
            <button className="icon-text-button" onClick={() => onRemove(bookmark.id)}><Trash2 size={15} /> Remove</button>
          </article>
        ))}
        {!bookmarks.length && <div className="empty-state"><BookMarked size={30} /><strong>No saved passages</strong><p>Open an answer's sources to bookmark a passage.</p></div>}
      </div>
    </section>
  );
}


export function AdminView({ documents, uploadPending, onUpload, onDelete }) {
  const [title, setTitle] = useState('');
  const [translation, setTranslation] = useState('');
  const [file, setFile] = useState(null);

  function submit(event) {
    event.preventDefault();
    if (!file || !title.trim()) return;
    const form = new FormData();
    form.append('title', title.trim());
    form.append('translation', translation.trim() || 'Unknown');
    form.append('file', file);
    onUpload(form).then(() => { setTitle(''); setTranslation(''); setFile(null); event.target.reset(); });
  }

  return (
    <section className="content-view">
      <header><span className="eyebrow">Administration</span><h1>Knowledge base</h1><p>Upload translations or commentaries and monitor asynchronous indexing.</p></header>
      <form className="upload-form" onSubmit={submit}>
        <label>Title<input value={title} maxLength={200} onChange={(event) => setTitle(event.target.value)} placeholder="Bhagavad Gita translation" /></label>
        <label>Translation or author<input value={translation} maxLength={120} onChange={(event) => setTranslation(event.target.value)} placeholder="Edition or commentary" /></label>
        <label className="file-input"><UploadCloud size={20} /><span>{file?.name || 'Choose a PDF'}</span><input type="file" accept="application/pdf" onChange={(event) => setFile(event.target.files[0])} /></label>
        <button className="primary-button" disabled={uploadPending || !file || !title.trim()}>{uploadPending ? 'Uploading...' : 'Upload and index'}</button>
      </form>
      <div className="document-list">
        {documents.map((document) => (
          <article key={document.id}>
            <FileText size={19} /><div><strong>{document.title}</strong><span>{document.translation} - {document.chunk_count} chunks</span></div>
            <span className={`status status-${document.status}`}>{document.status}</span>
            <button className="icon-button" onClick={() => onDelete(document.id)} title="Delete document"><Trash2 size={16} /></button>
          </article>
        ))}
      </div>
    </section>
  );
}
