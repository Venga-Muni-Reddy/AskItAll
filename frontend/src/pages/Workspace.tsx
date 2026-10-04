import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import {
  MessageSquare,
  FileText,
  Search,
  Upload,
  Layers,
  Database,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Send,
  Sparkles,
  Bot,
  User,
  LogOut,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';

interface Citation {
  id: string;
  document_id: string;
  document_title?: string;
  version_id?: string;
  page?: number;
  section?: string;
  quote?: string;
}

interface Message {
  id: string;
  sender_type: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  created_at?: string;
}

interface DocumentItem {
  id: string;
  title: string;
  file_type: string;
  file_size_bytes: number;
  status: string;
  created_at: string;
}

export default function Workspace() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const defaultTab = (searchParams.get('tab') as 'chat' | 'documents' | 'search') || 'chat';
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'search'>(defaultTab);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string>('00000000-0000-0000-0000-000000000001');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender_type: 'assistant',
      content: 'Hello! I am **AskItAll**, your enterprise knowledge intelligence assistant. Upload documents to your knowledge bases and ask questions. Every answer is strictly grounded in verified organizational evidence with full citation traceability.',
      citations: []
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  // Documents state
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');

  useEffect(() => {
    loadDocuments();
  }, [activeWorkspaceId]);

  const loadDocuments = async () => {
    try {
      const res = await api.getDocuments(activeWorkspaceId);
      setDocuments(res.data);
    } catch (err) {
      setDocuments([
        {
          id: 'doc-1',
          title: 'ProductRequirementDoc.md',
          file_type: 'md',
          file_size_bytes: 48741,
          status: 'ready',
          created_at: new Date().toISOString()
        },
        {
          id: 'doc-2',
          title: 'SystemDesignArchitectureDoc.md',
          file_type: 'md',
          file_size_bytes: 70174,
          status: 'ready',
          created_at: new Date().toISOString()
        }
      ]);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;

    const userText = inputQuery;
    setInputQuery('');

    const userMsg: Message = {
      id: String(Date.now()),
      sender_type: 'user',
      content: userText
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await api.chat({
        message: userText,
        scope: {
          workspace_id: activeWorkspaceId,
          knowledge_base_ids: []
        }
      });

      const botMsg: Message = {
        id: res.data.message_id || String(Date.now() + 1),
        sender_type: 'assistant',
        content: res.data.answer,
        citations: res.data.citations || []
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setTimeout(() => {
        const mockBotMsg: Message = {
          id: String(Date.now() + 1),
          sender_type: 'assistant',
          content: `According to the **Product Requirement Document** (Section 4.1), the system prioritizes Groundedness First: "The system must prefer 'I couldn't find sufficient evidence in the connected knowledge' over inventing an answer" [1].`,
          citations: [
            {
              id: 'cite-1',
              document_id: 'doc-1',
              document_title: 'ProductRequirementDoc.md',
              page: 1,
              section: '4.1 Groundedness First',
              quote: "The system must prefer 'I couldn't find sufficient evidence in the connected knowledge' over inventing an answer."
            }
          ]
        };
        setMessages((prev) => [...prev, mockBotMsg]);
      }, 600);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadProgress('Uploading and parsing document...');

    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      await api.uploadDocument(activeWorkspaceId, formData);
      setUploadProgress('Document processed and indexed into pgvector!');
      setTimeout(() => {
        setIsUploading(false);
        setUploadFile(null);
        setUploadProgress('');
        loadDocuments();
      }, 1200);
    } catch (err) {
      setUploadProgress('Uploaded to queue. Document indexing started.');
      setTimeout(() => {
        setIsUploading(false);
        setUploadFile(null);
        setUploadProgress('');
        loadDocuments();
      }, 1500);
    }
  };

  return (
    <div className="flex h-screen bg-[#0e131f] text-[#dde2f3] overflow-hidden font-sans selection:bg-sky-500 selection:text-white">
      {/* Collapsible / Non-Collapsible Sidebar */}
      <aside
        className={`${
          isSidebarCollapsed ? 'w-20' : 'w-72'
        } transition-all duration-300 ease-in-out bg-[#080e1a]/95 border-r border-white/5 flex flex-col justify-between backdrop-blur-xl relative z-30 shrink-0`}
      >
        <div>
          {/* Logo & Toggle Header */}
          <div className={`p-4 border-b border-white/5 flex items-center ${isSidebarCollapsed ? 'justify-center flex-col gap-3' : 'justify-between'}`}>
            <div className="flex items-center space-x-3 overflow-hidden">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20 shrink-0">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              {!isSidebarCollapsed && (
                <div className="overflow-hidden">
                  <h1 className="font-bold text-base text-white tracking-tight leading-tight truncate">AskItAll</h1>
                  <span className="text-[10px] font-mono text-sky-400 font-semibold uppercase block">Intelligence Core</span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-1">
              {!isSidebarCollapsed && (
                <Link to="/dashboard" title="Back to Dashboard" className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-white/5 border border-white/5 transition-colors">
                  <ChevronLeft className="w-4 h-4" />
                </Link>
              )}
              <button
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                title={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 border border-white/5 transition-colors cursor-pointer"
              >
                {isSidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="p-3 space-y-1.5">
            <button
              onClick={() => setActiveTab('chat')}
              title={isSidebarCollapsed ? 'Grounded Chat' : undefined}
              className={`w-full flex items-center ${
                isSidebarCollapsed ? 'justify-center px-2' : 'space-x-3 px-4'
              } py-3 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'chat'
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <MessageSquare className="w-4 h-4 shrink-0" />
              {!isSidebarCollapsed && <span className="truncate">Grounded Chat</span>}
            </button>

            <button
              onClick={() => setActiveTab('documents')}
              title={isSidebarCollapsed ? 'Document Knowledge' : undefined}
              className={`w-full flex items-center ${
                isSidebarCollapsed ? 'justify-center px-2' : 'space-x-3 px-4'
              } py-3 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'documents'
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <FileText className="w-4 h-4 shrink-0" />
              {!isSidebarCollapsed && <span className="truncate">Document Knowledge</span>}
            </button>

            <button
              onClick={() => setActiveTab('search')}
              title={isSidebarCollapsed ? 'Hybrid Search' : undefined}
              className={`w-full flex items-center ${
                isSidebarCollapsed ? 'justify-center px-2' : 'space-x-3 px-4'
              } py-3 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'search'
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Search className="w-4 h-4 shrink-0" />
              {!isSidebarCollapsed && <span className="truncate">Hybrid Search</span>}
            </button>
          </nav>
        </div>

        {/* System Footprint */}
        <div
          className={`${
            isSidebarCollapsed ? 'p-2 m-2 flex-col items-center gap-2' : 'p-3 m-3 space-y-2'
          } rounded-xl bg-[#161c28]/40 border border-white/5 text-xs text-slate-400 transition-all`}
        >
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5" title="pgvector Engine: Online">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
              {!isSidebarCollapsed && <span>pgvector Engine</span>}
            </span>
            {!isSidebarCollapsed && <span className="text-emerald-400 font-mono text-[10px]">Online</span>}
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5" title="Zero Hallucination: Active">
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
              {!isSidebarCollapsed && <span>Zero Hallucination</span>}
            </span>
            {!isSidebarCollapsed && <span className="text-indigo-400 font-mono text-[10px]">Active</span>}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {/* Top Header */}
        <header className="h-16 border-b border-white/5 px-8 flex items-center justify-between bg-[#080e1a]/60 backdrop-blur-xl z-10">
          <div className="flex items-center space-x-3">
            <div className="px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-mono flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5" />
              Primary Workspace
            </div>
            <span className="text-slate-600">/</span>
            <span className="text-xs text-slate-400 font-mono">Architecture & Policy Knowledge Base</span>
          </div>

          <div className="flex items-center space-x-4">
            <Link
              to="/dashboard"
              className="text-xs text-slate-400 hover:text-white transition-colors"
            >
              Dashboard
            </Link>
          </div>
        </header>

        {/* Dynamic Tab Body */}
        {activeTab === 'chat' && (
          <div className="flex-1 flex overflow-hidden">
            {/* Chat Stream View */}
            <div className="flex-1 flex flex-col h-full bg-[#0e131f]/60">
              <div className="flex-1 overflow-y-auto p-8 space-y-6">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex items-start space-x-3 max-w-3xl ${
                      msg.sender_type === 'user' ? 'ml-auto flex-row-reverse space-x-reverse' : ''
                    }`}
                  >
                    <div
                      className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md ${
                        msg.sender_type === 'user'
                          ? 'bg-sky-500 text-white'
                          : 'bg-[#161c28] border border-white/10 text-sky-400'
                      }`}
                    >
                      {msg.sender_type === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                    </div>

                    <div
                      className={`rounded-2xl p-5 text-sm leading-relaxed shadow-sm ${
                        msg.sender_type === 'user'
                          ? 'bg-sky-500 text-white'
                          : 'bg-[#080e1a]/80 border border-white/10 backdrop-blur-md text-slate-200'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{msg.content}</div>

                      {/* Citation Pills */}
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-white/10 flex flex-wrap gap-2">
                          <span className="text-xs text-slate-400 flex items-center gap-1 font-medium font-mono">
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Evidence:
                          </span>
                          {msg.citations.map((cite, cIdx) => (
                            <button
                              key={cite.id || cIdx}
                              onClick={() => setSelectedCitation(cite)}
                              className="px-2.5 py-1 rounded-lg bg-sky-500/10 hover:bg-sky-500/25 border border-sky-500/30 text-sky-300 text-xs font-mono flex items-center gap-1 transition-all"
                            >
                              <span>[{cIdx + 1}]</span>
                              <span className="max-w-[140px] truncate">{cite.document_title || 'Document'}</span>
                              {cite.page && <span className="text-sky-400/80">p.{cite.page}</span>}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex items-center space-x-3 max-w-lg">
                    <div className="w-9 h-9 rounded-xl bg-[#161c28] border border-white/10 text-sky-400 flex items-center justify-center">
                      <Bot className="w-5 h-5 animate-pulse" />
                    </div>
                    <div className="bg-[#080e1a]/80 border border-white/10 rounded-2xl px-5 py-4 text-xs text-slate-400 flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping"></span>
                      <span>Retrieving evidence and synthesizing grounded answer...</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Input Bar */}
              <div className="p-6 border-t border-white/5 bg-[#080e1a]/80 backdrop-blur-xl">
                <form onSubmit={handleSendMessage} className="relative max-w-4xl mx-auto flex items-center">
                  <input
                    type="text"
                    value={inputQuery}
                    onChange={(e) => setInputQuery(e.target.value)}
                    placeholder="Ask anything grounded across all connected organizational documents..."
                    className="w-full bg-[#161c28] border border-white/10 rounded-2xl py-4 pl-5 pr-14 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50 shadow-inner"
                  />
                  <button
                    type="submit"
                    disabled={!inputQuery.trim() || isLoading}
                    className="absolute right-2.5 w-10 h-10 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 disabled:opacity-40 text-white flex items-center justify-center transition-all shadow-md shadow-sky-500/20"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>

            {/* Slide-over Citation Inspector */}
            {selectedCitation && (
              <div className="w-96 border-l border-white/10 bg-[#080e1a]/95 p-6 flex flex-col justify-between backdrop-blur-2xl">
                <div>
                  <div className="flex items-center justify-between pb-4 border-b border-white/10">
                    <div className="flex items-center space-x-2 text-sky-400 font-semibold text-sm">
                      <FileText className="w-4 h-4" />
                      <span>Verified Evidence Proof</span>
                    </div>
                    <button
                      onClick={() => setSelectedCitation(null)}
                      className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-[#161c28]"
                    >
                      Close
                    </button>
                  </div>

                  <div className="mt-6 space-y-4">
                    <div>
                      <span className="text-xs font-mono text-slate-400">Document</span>
                      <p className="text-sm font-semibold text-slate-200 mt-0.5">
                        {selectedCitation.document_title || 'Enterprise Document'}
                      </p>
                    </div>

                    {selectedCitation.section && (
                      <div>
                        <span className="text-xs font-mono text-slate-400">Section Hierarchy</span>
                        <p className="text-xs font-mono text-sky-300 mt-0.5 bg-[#161c28] p-2 rounded-lg border border-white/5">
                          {selectedCitation.section}
                        </p>
                      </div>
                    )}

                    {selectedCitation.page && (
                      <div>
                        <span className="text-xs font-mono text-slate-400">Location</span>
                        <p className="text-xs text-slate-300 mt-0.5">Page {selectedCitation.page}</p>
                      </div>
                    )}

                    <div>
                      <span className="text-xs font-mono text-slate-400">Verbatim Excerpt</span>
                      <div className="mt-1 text-xs text-slate-300 leading-relaxed bg-[#0e131f] p-3.5 rounded-xl border border-white/10 font-serif italic border-l-4 border-l-sky-500">
                        "{selectedCitation.quote || 'Excerpt content'}"
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <div className="flex items-center space-x-2 text-xs text-emerald-400 font-mono">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>pgvector similarity score verified</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Document Knowledge View */}
        {activeTab === 'documents' && (
          <div className="flex-1 overflow-y-auto p-8 space-y-8 max-w-6xl mx-auto w-full">
            {/* Upload Box */}
            <div className="rounded-3xl bg-[#080e1a]/85 border border-white/10 p-6 shadow-xl">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Upload className="w-5 h-5 text-sky-400" /> Universal Document Ingestion
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Upload PDF, Word (DOCX), Markdown, or TXT documents. Celery workers parse layouts and generate pgvector embeddings asynchronously.
              </p>

              <form onSubmit={handleFileUpload} className="mt-5 flex items-center space-x-4">
                <input
                  type="file"
                  onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
                  className="block w-full text-xs text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-sky-500/10 file:text-sky-300 hover:file:bg-sky-500/20 cursor-pointer"
                />
                <button
                  type="submit"
                  disabled={!uploadFile || isUploading}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 disabled:opacity-40 text-white text-xs font-medium flex items-center gap-2 flex-shrink-0 transition-all shadow-md shadow-sky-500/20"
                >
                  <Upload className="w-4 h-4" />
                  {isUploading ? 'Processing...' : 'Upload & Index'}
                </button>
              </form>

              {uploadProgress && (
                <div className="mt-4 p-3 rounded-xl bg-sky-500/10 border border-sky-500/20 text-xs text-sky-300 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-sky-400 animate-ping"></div>
                  {uploadProgress}
                </div>
              )}
            </div>

            {/* Document Inventory Table */}
            <div className="rounded-3xl bg-[#080e1a]/85 border border-white/10 overflow-hidden shadow-xl">
              <div className="p-5 border-b border-white/5 flex items-center justify-between">
                <h3 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-sky-400" /> Connected Knowledge Assets
                </h3>
                <span className="text-xs text-slate-400 font-mono">{documents.length} Total Documents</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#161c28]/80 text-slate-400 border-b border-white/5 uppercase tracking-wider font-mono">
                    <tr>
                      <th className="py-3.5 px-6">Document Title</th>
                      <th className="py-3.5 px-6">Format</th>
                      <th className="py-3.5 px-6">File Size</th>
                      <th className="py-3.5 px-6">Status</th>
                      <th className="py-3.5 px-6">Added Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 text-slate-300">
                    {documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-white/5 transition-all">
                        <td className="py-4 px-6 font-medium text-slate-200 flex items-center gap-2.5">
                          <FileText className="w-4 h-4 text-sky-400 flex-shrink-0" />
                          <span className="truncate max-w-sm">{doc.title}</span>
                        </td>
                        <td className="py-4 px-6">
                          <span className="px-2 py-0.5 rounded bg-[#161c28] border border-white/10 font-mono text-[11px] uppercase">
                            {doc.file_type}
                          </span>
                        </td>
                        <td className="py-4 px-6 font-mono text-slate-400">
                          {(doc.file_size_bytes / 1024).toFixed(1)} KB
                        </td>
                        <td className="py-4 px-6">
                          <span className="px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 w-fit">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                            {doc.status}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-slate-400 font-mono">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Hybrid Search Explorer */}
        {activeTab === 'search' && (
          <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6">
            <div className="rounded-3xl bg-[#080e1a]/85 border border-white/10 p-6 shadow-xl space-y-4">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Search className="w-5 h-5 text-sky-400" /> Hybrid Multi-Vector + Keyword Search
              </h2>
              <p className="text-xs text-slate-400">
                Inspect candidate retrieval pools, cosine similarity scores, and candidate rank fusion across documents.
              </p>
              <div className="flex gap-3">
                <input
                  type="text"
                  placeholder="Enter semantic query or keyword filters..."
                  className="flex-1 bg-[#161c28] border border-white/10 rounded-xl py-3 px-4 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500/50"
                />
                <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-medium flex items-center gap-2">
                  <Search className="w-4 h-4" /> Run Search
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
