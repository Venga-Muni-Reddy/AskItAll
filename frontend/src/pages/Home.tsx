import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Terminal,
  PlayCircle,
  Database,
  Search,
  Activity,
  ArrowRight,
  Lock,
  Layers,
  FileText,
  Code,
  Table,
  Headphones,
  Image,
  ExternalLink,
  ChevronRight,
  Copy,
  Zap,
  Cpu,
  Server
} from 'lucide-react';

export default function Home() {
  const [activeQueryIndex, setActiveQueryIndex] = useState(0);

  const queryExamples = [
    {
      prompt: "Summarize mandatory VPN and hardware security compliance for offshore engineering contractors.",
      latency: "380ms",
      sources: "3 verified chunks",
      hash: "8f4e..9a21",
      points: [
        {
          text: "Offshore personnel must establish an active tunnel via WireGuard Enterprise Dual-Hop VPN with FIPS 140-3 compliant hardware keys prior to touching internal git repositories.",
          citation: "[1] pg.14",
          color: "emerald"
        },
        {
          text: "Workstations require encrypted volume mounts with BitLocker or LUKS2 utilizing TPM 2.0 chips; non-compliant devices receive immediate token revocation within 60 seconds.",
          citation: "[2] pg.22",
          color: "indigo"
        },
        {
          text: "Bi-weekly automated MDM attestation is enforced via Zero-Trust device compliance hooks; split-tunneling is strictly disabled at the gateway layer.",
          citation: "[3] pg.04",
          color: "sky"
        }
      ],
      inspector: {
        title: "Enterprise_Security_2026.pdf",
        docId: "doc_sec_8921b • Page 14",
        cosine: "0.982",
        snippet: "...All offshore contractors accessing VPC subnet 10.200.0.0/16 must maintain persistent WireGuard Dual-Hop tunneling. Split-tunneling is strictly prohibited and leads to immediate credential isolation...",
        sha: "e3b0c44298fc1c14...",
        cluster: "eu-west-pg-04",
        indexed: "12m ago",
        footprint: "512 Tokens (84%)"
      }
    },
    {
      prompt: "What is the recovery point objective (RPO) and disaster recovery failover procedure for PostgreSQL pgvector clusters?",
      latency: "290ms",
      sources: "4 verified chunks",
      hash: "3c91..b712",
      points: [
        {
          text: "Continuous Write-Ahead Log (WAL) archiving via pgBackRest guarantees an RPO of < 60 seconds across primary and standby availability zones.",
          citation: "[1] pg.08",
          color: "emerald"
        },
        {
          text: "Automated patroni failover elects a new leader node within 15 seconds upon health check timeout, with zero human intervention required.",
          citation: "[2] pg.19",
          color: "sky"
        }
      ],
      inspector: {
        title: "Cloud_Infrastructure_SLA_Spec.pdf",
        docId: "doc_infra_3301a • Page 8",
        cosine: "0.974",
        snippet: "...High-availability replication topology uses synchronous multi-AZ standby nodes with strict quorum fencing. WAL streaming achieves sub-minute RPO...",
        sha: "a910f5431bc761a2...",
        cluster: "us-east-pg-01",
        indexed: "1h ago",
        footprint: "420 Tokens (78%)"
      }
    }
  ];

  const currentExample = queryExamples[activeQueryIndex];

  return (
    <div className="min-h-screen bg-[#0e131f] text-[#dde2f3] font-sans selection:bg-sky-500 selection:text-white">
      {/* HEADER NAVBAR */}
      <header className="fixed top-0 left-0 right-0 z-50 h-16 bg-[#161c28]/85 backdrop-blur-xl border-b border-white/5 shadow-lg">
        <div className="h-16 max-w-7xl mx-auto px-6 flex items-center justify-between gap-4">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-transform">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-lg text-white tracking-tight leading-none">AskItAll</span>
                <span className="text-[10px] font-mono text-sky-400 tracking-widest uppercase mt-0.5">Knowledge Intel</span>
              </div>
            </Link>

            <nav className="hidden lg:flex items-center gap-1 text-sm font-medium">
              <a href="#platform" className="px-3 py-1.5 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">Platform</a>
              <a href="#pipeline" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors">Pipeline</a>
              <a href="#graph" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors">Knowledge Graph</a>
              <a href="#provenance" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors">Provenance</a>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 bg-[#080e1a] px-3 py-1.5 rounded-lg border border-white/5 text-xs text-slate-400">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-mono text-emerald-400">Vector Cluster: Active</span>
            </div>

            <Link
              to="/login"
              className="px-4 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-sm shadow-lg shadow-sky-500/25 transition-all"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* MAIN CONTAINER */}
      <main className="relative pt-24 pb-20 px-6 max-w-7xl mx-auto flex flex-col gap-16">
        {/* HERO SECTION */}
        <section className="relative flex flex-col gap-8 pt-6 overflow-hidden">
          {/* Ambient Glows */}
          <div className="absolute -top-24 left-1/4 w-96 h-96 bg-sky-500/10 rounded-full blur-[120px] pointer-events-none -z-10"></div>
          <div className="absolute top-12 right-12 w-80 h-80 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none -z-10"></div>

          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
            <div className="flex flex-col gap-3 max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#242a36] border border-white/5 w-fit">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-[11px] font-mono text-emerald-400 tracking-wider uppercase font-semibold">
                  Zero Hallucination Grounding • 100% Cryptographic Provenance
                </span>
              </div>
              <h1 className="text-4xl lg:text-5xl font-bold text-white tracking-tight leading-tight">
                Enterprise Knowledge,{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-teal-300 to-indigo-400">
                  Verifiably Grounded.
                </span>
              </h1>
              <p className="text-slate-400 text-base lg:text-lg max-w-2xl leading-relaxed">
                Continuous multi-tenant vector ingestion, sub-50ms hybrid retrieval, and deterministic citation telemetry across petabyte-scale unstructured enterprise silos.
              </p>
            </div>

            <div className="flex items-center gap-3 self-start lg:self-end">
              <Link
                to="/dashboard"
                className="px-5 py-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-sm flex items-center gap-2 shadow-lg shadow-sky-500/25 transition-all cursor-pointer"
              >
                <Terminal className="w-4 h-4" />
                <span>Launch Workspace</span>
              </Link>
              <Link
                to="/signup"
                className="px-5 py-3 rounded-xl bg-[#242a36] hover:bg-[#2f3542] text-white border border-white/5 font-medium text-sm flex items-center gap-2 transition-all cursor-pointer"
              >
                <PlayCircle className="w-4 h-4 text-sky-400" />
                <span>Start Free Pilot</span>
              </Link>
            </div>
          </div>

          {/* REAL-TIME METRICS HUD */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-[#161c28]/90 backdrop-blur-xl p-3 rounded-2xl border border-white/5 shadow-2xl">
            <div className="bg-[#080e1a] p-4 rounded-xl flex flex-col gap-1 border border-white/5">
              <div className="flex items-center justify-between text-xs text-slate-400 font-mono uppercase tracking-wider">
                <span>Sync State</span>
                <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white">48</span>
                <span className="text-xs font-mono text-emerald-400">Repos Active</span>
              </div>
              <div className="text-[11px] font-mono text-slate-500">
                GitHub • Confluence • S3 • Notion
              </div>
            </div>

            <div className="bg-[#080e1a] p-4 rounded-xl flex flex-col gap-1 border border-white/5">
              <div className="flex items-center justify-between text-xs text-slate-400 font-mono uppercase tracking-wider">
                <span>Index Depth</span>
                <Database className="w-3.5 h-3.5 text-sky-400" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white">1,248,910</span>
              </div>
              <div className="text-[11px] font-mono text-slate-500">
                <span className="text-sky-400 font-semibold">1536-dim</span> HNSW Vectors
              </div>
            </div>

            <div className="bg-[#080e1a] p-4 rounded-xl flex flex-col gap-1 border border-white/5">
              <div className="flex items-center justify-between text-xs text-slate-400 font-mono uppercase tracking-wider">
                <span>Query Latency</span>
                <span className="text-[10px] font-mono bg-sky-500/10 text-sky-400 px-1.5 py-0.5 rounded">p99</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-sky-400">41.8<span className="text-sm">ms</span></span>
              </div>
              <div className="text-[11px] font-mono text-slate-500">
                Sub-second Hybrid Rerank
              </div>
            </div>

            <div className="bg-[#080e1a] p-4 rounded-xl flex flex-col gap-1 border border-white/5">
              <div className="flex items-center justify-between text-xs text-slate-400 font-mono uppercase tracking-wider">
                <span>Isolation</span>
                <Lock className="w-3.5 h-3.5 text-indigo-400" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white">0.00%</span>
                <span className="text-xs font-mono text-emerald-400">Leakage</span>
              </div>
              <div className="text-[11px] font-mono text-slate-500">
                <span className="text-indigo-400 font-semibold">SOC2 Type II</span> • Nitro Enclave
              </div>
            </div>
          </div>
        </section>

        {/* 4-STAGE PIPELINE VISUAL STEPPER */}
        <section id="pipeline" className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-sky-400" />
              <h2 className="text-xl font-bold text-white">Multimodal Grounding Pipeline Architecture</h2>
            </div>
            <span className="text-xs font-mono text-slate-400 bg-[#242a36] px-2.5 py-1 rounded-md border border-white/5">
              STREAMING REALTIME INGEST
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Stage 1 */}
            <div className="bg-[#161c28] p-5 rounded-2xl flex flex-col justify-between gap-4 border border-white/5 hover:border-sky-500/30 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-sky-400 uppercase tracking-widest font-semibold">01 // INGESTION</span>
                <span className="h-2 w-2 rounded-full bg-sky-400 animate-pulse"></span>
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">Multimodal Sources</h3>
                <p className="text-xs text-slate-400 mt-1">Unstructured raw stream</p>
              </div>
              <div className="grid grid-cols-3 gap-1.5">
                <div className="flex items-center gap-1.5 bg-[#080e1a] px-2 py-1.5 rounded-lg border border-white/5 text-xs">
                  <FileText className="w-3.5 h-3.5 text-rose-400" />
                  <span>PDFs</span>
                </div>
                <div className="flex items-center gap-1.5 bg-[#080e1a] px-2 py-1.5 rounded-lg border border-white/5 text-xs">
                  <Code className="w-3.5 h-3.5 text-sky-400" />
                  <span>Repo</span>
                </div>
                <div className="flex items-center gap-1.5 bg-[#080e1a] px-2 py-1.5 rounded-lg border border-white/5 text-xs">
                  <Table className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Sheets</span>
                </div>
                <div className="flex items-center gap-1.5 bg-[#080e1a] px-2 py-1.5 rounded-lg border border-white/5 text-xs">
                  <Headphones className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Audio</span>
                </div>
                <div className="flex items-center gap-1.5 bg-[#080e1a] px-2 py-1.5 rounded-lg border border-white/5 text-xs">
                  <FileText className="w-3.5 h-3.5 text-sky-300" />
                  <span>Docs</span>
                </div>
                <div className="flex items-center gap-1.5 bg-[#080e1a] px-2 py-1.5 rounded-lg border border-white/5 text-xs">
                  <Image className="w-3.5 h-3.5 text-teal-300" />
                  <span>Vision</span>
                </div>
              </div>
              <div className="bg-[#080e1a] p-2.5 rounded-lg flex items-center justify-between border border-white/5 text-xs">
                <span className="text-slate-400">Throughput</span>
                <span className="text-emerald-400 font-mono font-semibold">14.2 MB/s</span>
              </div>
            </div>

            {/* Stage 2 */}
            <div className="bg-[#161c28] p-5 rounded-2xl flex flex-col justify-between gap-4 border border-white/5 hover:border-emerald-500/30 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-emerald-400 uppercase tracking-widest font-semibold">02 // INSPECTION</span>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">PII Redaction Guard</h3>
                <p className="text-xs text-slate-400 mt-1">Zero-knowledge heuristic parsing</p>
              </div>
              <div className="bg-[#080e1a] p-3 rounded-xl flex flex-col gap-2 border border-white/5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Sanitization Rate</span>
                  <span className="text-emerald-400 font-semibold font-mono">100% Secure</span>
                </div>
                <div className="w-full bg-[#2f3542] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-400 h-full w-full rounded-full"></div>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span>0 False Positives</span>
                  <span>AES-256 GCM</span>
                </div>
              </div>
              <div className="bg-[#080e1a] p-2.5 rounded-lg flex items-center justify-between border border-white/5 text-xs">
                <span className="text-slate-400">Anonymized Tokens</span>
                <span className="text-sky-400 font-mono font-semibold">89,204</span>
              </div>
            </div>

            {/* Stage 3 */}
            <div className="bg-[#161c28] p-5 rounded-2xl flex flex-col justify-between gap-4 border border-white/5 hover:border-indigo-500/30 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-indigo-400 uppercase tracking-widest font-semibold">03 // CHUNKING & GRAPH</span>
                <Activity className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">Ontology Linker</h3>
                <p className="text-xs text-slate-400 mt-1">Context-aware hierarchical nodes</p>
              </div>
              <div className="bg-[#080e1a] p-2 rounded-xl flex items-center justify-center h-20 border border-white/5">
                <svg className="w-full h-full text-slate-600" viewBox="0 0 160 60">
                  <line stroke="currentColor" strokeDasharray="2,2" strokeWidth="1.5" x1="20" x2="60" y1="30" y2="15"></line>
                  <line stroke="currentColor" strokeWidth="1.5" x1="20" x2="60" y1="30" y2="45"></line>
                  <line stroke="currentColor" strokeWidth="1.5" x1="60" x2="110" y1="15" y2="30"></line>
                  <line stroke="currentColor" strokeWidth="1.5" x1="60" x2="110" y1="45" y2="30"></line>
                  <line stroke="#0ea5e9" strokeWidth="2" x1="110" x2="145" y1="30" y2="30"></line>
                  <circle cx="20" cy="30" fill="#89ceff" r="5"></circle>
                  <circle cx="60" cy="15" fill="#c0c1ff" r="4"></circle>
                  <circle cx="60" cy="45" fill="#4edea3" r="4"></circle>
                  <circle cx="110" cy="30" fill="#0ea5e9" r="6"></circle>
                  <circle cx="145" cy="30" fill="#89ceff" r="4"></circle>
                </svg>
              </div>
              <div className="bg-[#080e1a] p-2.5 rounded-lg flex items-center justify-between border border-white/5 text-xs">
                <span className="text-slate-400">Cosine Edge Density</span>
                <span className="text-indigo-400 font-mono font-semibold">0.94 avg</span>
              </div>
            </div>

            {/* Stage 4 */}
            <div className="bg-[#161c28] p-5 rounded-2xl flex flex-col justify-between gap-4 border border-white/5 hover:border-sky-500/30 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-sky-400 uppercase tracking-widest font-semibold">04 // VECTOR STORE</span>
                <Database className="w-4 h-4 text-sky-400" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">pgvector Shard Cluster</h3>
                <p className="text-xs text-slate-400 mt-1">Distributed spatial indexes</p>
              </div>
              <div className="bg-[#080e1a] p-3 rounded-xl flex flex-col gap-2 border border-white/5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Memory Allocation</span>
                  <span className="text-sky-400 font-semibold font-mono">7.4 / 20 GB</span>
                </div>
                <div className="w-full bg-[#2f3542] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-sky-400 h-full w-[37%] rounded-full"></div>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span>32 Shards Up</span>
                  <span>Replica x3</span>
                </div>
              </div>
              <div className="bg-[#080e1a] p-2.5 rounded-lg flex items-center justify-between border border-white/5 text-xs">
                <span className="text-slate-400">Search Mode</span>
                <span className="text-emerald-400 font-mono font-semibold">BM25 + Dense</span>
              </div>
            </div>
          </div>
        </section>

        {/* LIVE SPLIT-SCREEN WORKBENCH PREVIEW: QUERY ENGINE & EVIDENCE PROVENANCE */}
        <section id="provenance" className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-sky-400" />
              <h2 className="text-xl font-bold text-white">Grounded Synthesis & Provenance Inspector</h2>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
                HASH: {currentExample.hash}
              </span>
              <div className="flex gap-1">
                {queryExamples.map((_, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveQueryIndex(idx)}
                    className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                      activeQueryIndex === idx
                        ? 'bg-sky-500 text-slate-950 font-bold'
                        : 'bg-[#242a36] text-slate-400 hover:text-white'
                    }`}
                  >
                    Query #{idx + 1}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            {/* Left Pane: Grounded Answer */}
            <div className="lg:col-span-7 bg-[#161c28] rounded-2xl p-6 flex flex-col gap-4 border border-white/5 shadow-xl">
              <div className="bg-[#080e1a] p-3 rounded-xl flex items-center gap-3 border border-white/5">
                <Search className="w-5 h-5 text-sky-400 shrink-0" />
                <span className="text-sm font-medium text-white flex-1">
                  "{currentExample.prompt}"
                </span>
              </div>

              <div className="bg-[#080e1a]/80 p-5 rounded-xl flex flex-col gap-4 border border-white/5">
                <div className="flex items-center justify-between pb-2 border-b border-white/5">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-mono text-emerald-400 uppercase tracking-wider font-semibold">
                      100% Grounded Answer
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="h-6 px-2.5 rounded bg-[#242a36] hover:bg-[#2f3542] text-slate-300 text-xs flex items-center gap-1 transition-colors">
                      <Copy className="w-3 h-3" /> Copy
                    </button>
                  </div>
                </div>

                <ul className="flex flex-col gap-3 text-sm text-slate-300">
                  {currentExample.points.map((pt, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-sky-400 font-bold">•</span>
                      <span className="leading-relaxed">
                        {pt.text}{' '}
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 mx-1 rounded bg-sky-500/15 text-sky-400 text-xs font-mono font-medium">
                          {pt.citation}
                        </span>
                      </span>
                    </li>
                  ))}
                </ul>

                <div className="flex items-center justify-between pt-2 border-t border-white/5 text-xs text-slate-400 font-mono">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    <span>Synthesis complete in {currentExample.latency} • {currentExample.sources} linked</span>
                  </div>
                  <span className="text-emerald-400">Temp: 0.0 • Deterministic</span>
                </div>
              </div>

              <div className="bg-[#080e1a] p-2.5 rounded-xl flex items-center gap-3 border border-white/5">
                <input
                  type="text"
                  placeholder="Ask a verified follow-up question..."
                  className="bg-transparent border-none outline-none text-xs text-white placeholder-slate-500 flex-1 px-2"
                  readOnly
                />
                <Link
                  to="/dashboard"
                  className="h-8 px-3 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-colors"
                >
                  <span>Chat Live</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Right Pane: Provenance Inspector */}
            <div className="lg:col-span-5 bg-[#161c28] rounded-2xl p-6 flex flex-col gap-4 border border-white/5 shadow-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-sm font-semibold text-white">Active Provenance Inspector</span>
                </div>
                <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">
                  Rank #1 Match
                </span>
              </div>

              <div className="bg-[#080e1a] p-4 rounded-xl flex flex-col gap-3 border border-white/5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <FileText className="w-5 h-5 text-rose-400 shrink-0" />
                    <div>
                      <div className="text-xs font-semibold text-white">{currentExample.inspector.title}</div>
                      <div className="text-[11px] text-slate-500 font-mono">{currentExample.inspector.docId}</div>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-emerald-400 bg-[#242a36] px-2 py-1 rounded">
                    Cosine: {currentExample.inspector.cosine}
                  </span>
                </div>

                <div className="bg-[#1a202c] p-3 rounded-lg text-xs font-mono text-slate-300 leading-relaxed border border-white/5">
                  "{currentExample.inspector.snippet}"
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
                  <span className="flex items-center gap-1 text-emerald-400">
                    <Lock className="w-3 h-3" /> SHA-256 Validated
                  </span>
                  <span>{currentExample.inspector.sha}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-[#080e1a] p-3 rounded-xl flex flex-col gap-1 border border-white/5">
                  <span className="text-[11px] text-slate-400 font-mono">Vector Cluster</span>
                  <span className="text-xs font-bold text-sky-400 font-mono">{currentExample.inspector.cluster}</span>
                  <span className="text-[10px] text-emerald-400">Indexed: {currentExample.inspector.indexed}</span>
                </div>
                <div className="bg-[#080e1a] p-3 rounded-xl flex flex-col gap-1 border border-white/5">
                  <span className="text-[11px] text-slate-400 font-mono">Chunk Footprint</span>
                  <span className="text-xs font-bold text-white font-mono">{currentExample.inspector.footprint}</span>
                  <span className="text-[10px] text-slate-500">Overlap: 64 tok</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 3 BESPOKE CAPABILITY TILES */}
        <section id="graph" className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-[#161c28] p-6 rounded-2xl flex flex-col justify-between gap-4 border border-white/5 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-sky-400" />
                <h3 className="text-base font-semibold text-white">Live Ontology Graph</h3>
              </div>
              <span className="text-xs font-mono text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded">Dynamic</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Connects disparate entity nodes automatically across silos without manual tagging or brittle taxonomy rules.
            </p>
            <div className="bg-[#080e1a] p-3 rounded-xl flex items-center justify-center h-28 border border-white/5">
              <svg className="w-full h-full text-slate-600" viewBox="0 0 200 90">
                <circle cx="40" cy="45" fill="#161c28" r="16" stroke="#3e4850" strokeWidth="1.5"></circle>
                <text fill="#89ceff" fontFamily="monospace" fontSize="8" textAnchor="middle" x="40" y="48">AWS_IAM</text>
                <circle cx="100" cy="25" fill="#161c28" r="14" stroke="#3e4850" strokeWidth="1.5"></circle>
                <text fill="#4edea3" fontFamily="monospace" fontSize="8" textAnchor="middle" x="100" y="28">POLICY</text>
                <circle cx="100" cy="65" fill="#161c28" r="14" stroke="#3e4850" strokeWidth="1.5"></circle>
                <text fill="#c0c1ff" fontFamily="monospace" fontSize="8" textAnchor="middle" x="100" y="68">VPN_GW</text>
                <circle cx="160" cy="45" fill="#161c28" r="16" stroke="#3e4850" strokeWidth="1.5"></circle>
                <text fill="#dde2f3" fontFamily="monospace" fontSize="8" textAnchor="middle" x="160" y="48">SOC2_RPT</text>
                <line stroke="#89ceff" strokeDasharray="2,2" strokeWidth="1.5" x1="56" x2="86" y1="40" y2="28"></line>
                <line stroke="#89ceff" strokeWidth="1.5" x1="56" x2="86" y1="50" y2="62"></line>
                <line stroke="#4edea3" strokeWidth="1.5" x1="114" x2="144" y1="28" y2="40"></line>
                <line stroke="#c0c1ff" strokeWidth="1.5" x1="114" x2="144" y1="62" y2="50"></line>
              </svg>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono pt-2 border-t border-white/5">
              <span>142K Entity Vertices</span>
              <span className="text-emerald-400">99.2% Accuracy</span>
            </div>
          </div>

          <div className="bg-[#161c28] p-6 rounded-2xl flex flex-col justify-between gap-4 border border-white/5 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-semibold text-white">Retrieval Velocity</h3>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">pgvector + HNSW</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Sub-50ms vector cosine lookups with native reciprocal rank fusion (RRF) across concurrent tenant requests.
            </p>
            <div className="bg-[#080e1a] p-4 rounded-xl flex flex-col gap-3 border border-white/5">
              <div className="flex items-baseline justify-between">
                <span className="text-xl font-bold text-sky-400 font-mono">2,450 <span className="text-xs font-normal text-slate-400">tok/sec</span></span>
                <span className="text-xs font-mono text-emerald-400 font-semibold">+18% Peak</span>
              </div>
              <div className="w-full flex items-center gap-1.5 h-6">
                <div className="h-full bg-sky-500/40 rounded flex-1"></div>
                <div className="h-4/5 bg-sky-500/50 rounded flex-1"></div>
                <div className="h-full bg-sky-500/70 rounded flex-1"></div>
                <div className="h-3/4 bg-sky-500/60 rounded flex-1"></div>
                <div className="h-full bg-sky-400 rounded flex-1"></div>
                <div className="h-5/6 bg-sky-500/80 rounded flex-1"></div>
                <div className="h-full bg-emerald-400 rounded flex-1"></div>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono pt-2 border-t border-white/5">
              <span>Median Query: 38ms</span>
              <span className="text-sky-400 font-semibold">Zero Jitter</span>
            </div>
          </div>

          <div className="bg-[#161c28] p-6 rounded-2xl flex flex-col justify-between gap-4 border border-white/5 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-semibold text-white">Zero-Retention Enclave</h3>
              </div>
              <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">Air-Gapped</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              In-memory inference pipeline with zero persistent disk logging, ephemeral decryption, and customer KMS keys.
            </p>
            <div className="bg-[#080e1a] p-4 rounded-xl flex flex-col gap-2.5 border border-white/5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-white font-medium">AWS Nitro Enclave</span>
                <span className="text-emerald-400 font-mono font-semibold">Attested</span>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
                <span>BYOK Encryption</span>
                <span className="text-white">AES-256</span>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
                <span>Model Training Policy</span>
                <span className="text-rose-400 font-bold">STRICT ZERO</span>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono pt-2 border-t border-white/5">
              <span>FedRAMP Ready</span>
              <span className="text-indigo-400 font-semibold">SOC2 Certified</span>
            </div>
          </div>
        </section>

        {/* BOTTOM ACTION STRIP */}
        <section className="bg-[#161c28] rounded-2xl p-6 flex flex-col lg:flex-row items-center justify-between gap-6 border border-white/5 shadow-2xl">
          <div className="flex flex-col gap-1 w-full lg:w-auto">
            <span className="text-xs font-mono text-sky-400 uppercase tracking-widest font-semibold">
              QUICK BENCHMARK SIMULATOR
            </span>
            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="px-3 py-1 rounded-full bg-[#080e1a] border border-white/5 text-xs text-slate-300 flex items-center gap-1 font-mono">
                <span className="text-emerald-400">#</span> SOC2 Type II Baseline
              </span>
              <span className="px-3 py-1 rounded-full bg-[#080e1a] border border-white/5 text-xs text-slate-300 flex items-center gap-1 font-mono">
                <span className="text-sky-400">#</span> Offshore Hardware Policy
              </span>
              <span className="px-3 py-1 rounded-full bg-[#080e1a] border border-white/5 text-xs text-slate-300 flex items-center gap-1 font-mono">
                <span className="text-indigo-400">#</span> API Rate Limits & Quotas
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full lg:w-auto justify-end">
            <Link
              to="/login"
              className="px-5 py-2.5 rounded-xl bg-[#242a36] hover:bg-[#2f3542] text-white border border-white/5 text-sm font-medium transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-sky-500/25 transition-all flex items-center gap-2"
            >
              <span>Get Started</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
