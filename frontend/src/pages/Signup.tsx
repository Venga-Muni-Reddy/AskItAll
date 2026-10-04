import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Lock, User, Building, Eye, EyeOff, ShieldCheck, CheckCircle2, ArrowRight, AlertCircle, FileText, Database } from 'lucide-react';
import { api } from '../services/api';

export default function Signup() {
  const navigate = useNavigate();
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Password strength calculation
  const getPasswordStrength = () => {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  };

  const strength = getPasswordStrength();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    if (password.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }

    setIsLoading(true);

    try {
      const res = await api.register({
        email,
        password,
        display_name: displayName,
        organization_name: organizationName || undefined,
      });

      const { access_token, refresh_token, user } = res.data;
      localStorage.setItem('askitall_token', access_token);
      localStorage.setItem('askitall_refresh_token', refresh_token);
      if (user) {
        localStorage.setItem('askitall_user', JSON.stringify(user));
      }

      navigate('/dashboard');
    } catch (err: any) {
      const detail = err.response?.data?.error?.message || 'Registration failed. Please check your details.';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0e131f] text-[#dde2f3] flex flex-col font-sans selection:bg-sky-500 selection:text-white">
      {/* Top Navbar */}
      <header className="h-16 w-full px-8 flex items-center justify-between border-b border-white/5 bg-[#080e1a]/80 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg text-white tracking-tight">AskItAll</span>
          <span className="px-2 py-0.5 rounded text-[11px] font-mono tracking-wider uppercase font-semibold bg-[#242a36] text-sky-400 border border-white/5">
            Enterprise
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <span className="text-slate-400">Already registered?</span>
          <Link
            to="/login"
            className="px-3.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium transition-all"
          >
            Sign In
          </Link>
        </div>
      </header>

      {/* Main Split Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 max-w-7xl mx-auto w-full p-6 md:p-10 gap-10 items-center">
        {/* Left Showcase Column */}
        <div className="lg:col-span-6 space-y-8 pr-0 lg:pr-6">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-mono">
              <ShieldCheck className="w-3.5 h-3.5" />
              Zero-Hallucination Enterprise RAG
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight leading-tight">
              Turn scattered documents into verified, evidence-grounded intelligence.
            </h1>
            <p className="text-sm text-slate-400 leading-relaxed">
              Connect PDFs, Word documents, Markdown, and spreadsheets into an isolated organizational knowledge layer with cryptographic citation traceability.
            </p>
          </div>

          {/* Value Cards */}
          <div className="space-y-4">
            <div className="p-4 rounded-2xl bg-[#161c28]/60 border border-white/5 backdrop-blur-md flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center flex-shrink-0">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Deterministic Parsing</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Preserves tables, hierarchy, headings, and equations before vectorization.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#161c28]/60 border border-white/5 backdrop-blur-md flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Verifiable Citations</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Every answer references verbatim text chunks with page numbers and section provenance.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#161c28]/60 border border-white/5 backdrop-blur-md flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center flex-shrink-0">
                <Database className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Multi-Tenant Isolation</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Strict schema isolation across Organizations, Workspaces, and Knowledge Bases.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Registration Form */}
        <div className="lg:col-span-6 w-full">
          <div className="rounded-3xl bg-[#080e1a]/90 border border-white/10 backdrop-blur-2xl p-8 md:p-10 shadow-2xl shadow-black/80">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-white tracking-tight">Create your workspace account</h2>
              <p className="text-xs text-slate-400 mt-1">
                Enter your details to initialize your organization's knowledge intelligence workbench.
              </p>
            </div>

            {errorMessage && (
              <div className="mb-5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 font-medium mb-1.5">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="e.g. Dr. Sarah Chen"
                    className="w-full bg-[#161c28] border border-white/10 focus:border-sky-500/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500/50 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 font-medium mb-1.5">
                  Work Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="sarah@company.com"
                    className="w-full bg-[#161c28] border border-white/10 focus:border-sky-500/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500/50 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 font-medium mb-1.5">
                  Organization / Company Name
                </label>
                <div className="relative">
                  <Building className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    value={organizationName}
                    onChange={(e) => setOrganizationName(e.target.value)}
                    placeholder="e.g. Acme Global Tech"
                    className="w-full bg-[#161c28] border border-white/10 focus:border-sky-500/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500/50 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 font-medium mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Minimum 8 characters"
                    className="w-full bg-[#161c28] border border-white/10 focus:border-sky-500/60 rounded-xl py-2.5 pl-10 pr-10 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500/50 transition-all font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-3 text-slate-500 hover:text-slate-300"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>

                {/* Real-time Password Strength Meter */}
                {password && (
                  <div className="mt-2 space-y-1.5">
                    <div className="flex gap-1 h-1">
                      {[1, 2, 3, 4].map((step) => (
                        <div
                          key={step}
                          className={`flex-1 rounded-full transition-all duration-300 ${
                            strength >= step
                              ? strength === 4
                                ? 'bg-emerald-400'
                                : strength >= 2
                                ? 'bg-sky-400'
                                : 'bg-amber-400'
                              : 'bg-white/10'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">
                      Strength: {strength === 4 ? 'Very Strong' : strength >= 2 ? 'Moderate' : 'Weak'}
                    </span>
                  </div>
                )}
              </div>

              {/* Privacy Pledge Card */}
              <div className="p-3 rounded-xl bg-sky-500/5 border border-sky-500/20 text-[11px] text-slate-400 flex items-start gap-2">
                <ShieldCheck className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
                <span>
                  <strong className="text-slate-200">Zero-Training Pledge:</strong> Your organizational files, embeddings, and chat messages are strictly private and never used to train external LLMs.
                </span>
              </div>

              <div className="pt-2">
                <label className="flex items-start gap-2 cursor-pointer text-xs text-slate-400">
                  <input
                    type="checkbox"
                    checked={agreeTerms}
                    onChange={(e) => setAgreeTerms(e.target.checked)}
                    className="mt-0.5 rounded border-white/20 bg-slate-800 text-sky-500 focus:ring-0"
                  />
                  <span>I agree to the Enterprise Terms of Service and Master Subscription Agreement.</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={isLoading || !agreeTerms}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 disabled:opacity-50 text-white font-medium text-sm flex items-center justify-center gap-2 shadow-lg shadow-sky-500/25 transition-all mt-4"
              >
                <span>{isLoading ? 'Creating Workspace...' : 'Create Workspace & Get Started'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
