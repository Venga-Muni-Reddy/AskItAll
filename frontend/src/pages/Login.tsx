import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Lock, Eye, EyeOff, ShieldCheck, ArrowRight, AlertCircle, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setIsLoading(true);

    try {
      const res = await api.login({ email, password });
      const { access_token, refresh_token, user } = res.data;
      localStorage.setItem('askitall_token', access_token);
      localStorage.setItem('askitall_refresh_token', refresh_token);
      if (user) {
        localStorage.setItem('askitall_user', JSON.stringify(user));
      }
      navigate('/dashboard');
    } catch (err: any) {
      const detail = err.response?.data?.error?.message || 'Invalid email or password.';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0e131f] text-[#dde2f3] flex flex-col justify-between relative overflow-hidden font-sans selection:bg-sky-500 selection:text-white">
      {/* Dynamic Background Glow & Grid */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden flex items-center justify-center">
        <div className="absolute w-[680px] h-[680px] rounded-full bg-gradient-to-tr from-indigo-900/30 via-sky-600/20 to-teal-500/10 blur-[130px] opacity-70"></div>
        <div className="absolute w-[360px] h-[360px] rounded-full bg-sky-500/15 blur-[90px] opacity-60"></div>
        
        {/* Subtle grid pattern */}
        <div 
          className="absolute inset-0 opacity-15"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)`,
            backgroundSize: '36px 36px',
          }}
        />
      </div>

      {/* Top Header */}
      <header className="relative z-20 h-16 w-full px-8 flex items-center justify-between border-b border-white/5 bg-[#080e1a]/80 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg text-white tracking-tight">AskItAll</span>
            <span className="px-2 py-0.5 rounded text-[11px] font-mono tracking-wider uppercase font-semibold bg-[#242a36] text-sky-400 border border-white/5">
              Enterprise
            </span>
          </div>
          <div className="hidden md:flex items-center gap-2 pl-3 border-l border-white/10 text-xs text-slate-400">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-mono text-[11px]">Enclave v1.0 Active</span>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <span className="text-slate-400">Don't have an account?</span>
          <Link
            to="/signup"
            className="px-3.5 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 font-medium transition-all"
          >
            Create Workspace
          </Link>
        </div>
      </header>

      {/* Main Authentication Card */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center p-6 my-8">
        <div className="w-full max-w-[480px] rounded-3xl bg-[#080e1a]/85 border border-white/10 backdrop-blur-2xl p-8 md:p-10 shadow-2xl shadow-black/80">
          {/* Ambient card top border glow */}
          <div className="h-px w-full bg-gradient-to-r from-transparent via-sky-500/40 to-transparent -mt-8 mb-8"></div>

          <div className="mb-6 text-left">
            <h1 className="text-2xl font-bold text-white tracking-tight">Welcome back</h1>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Authenticate with your enterprise credentials to access your isolated knowledge workspaces.
            </p>
          </div>

          {/* Enterprise SSO Buttons */}
          <div className="grid grid-cols-2 gap-3 mb-6">
            <button
              type="button"
              className="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-[#161c28] hover:bg-[#1a202c] border border-white/5 text-xs font-medium text-slate-200 hover:text-white transition-all"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z" fill="#4285F4"/>
                <path d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z" fill="#34A853"/>
                <path d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.17 0 9.97 0 12s.45 3.83 1.25 5.42l4.03-3.15z" fill="#FBBC05"/>
                <path d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z" fill="#EA4335"/>
              </svg>
              <span>Google SSO</span>
            </button>

            <button
              type="button"
              className="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-[#161c28] hover:bg-[#1a202c] border border-white/5 text-xs font-medium text-slate-200 hover:text-white transition-all"
            >
              <ShieldCheck className="w-4 h-4 text-sky-400" />
              <span>Okta / SAML</span>
            </button>
          </div>

          <div className="relative flex items-center justify-center my-6">
            <div className="w-full h-px bg-white/10"></div>
            <span className="absolute bg-[#080e1a] px-3 font-mono text-[10px] text-slate-500 uppercase tracking-widest">
              Or continue with work email
            </span>
          </div>

          {errorMessage && (
            <div className="mb-5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
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
                  placeholder="name@company.com"
                  className="w-full bg-[#161c28] border border-white/10 focus:border-sky-500/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500/50 transition-all"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-medium">
                  Password
                </label>
                <a href="#forgot" className="text-xs text-sky-400 hover:underline">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
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
            </div>

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-400">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-white/20 bg-slate-800 text-sky-500 focus:ring-0"
                />
                <span>Remember this device</span>
              </label>

              <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> 2FA Active
              </span>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 disabled:opacity-50 text-white font-medium text-sm flex items-center justify-center gap-2 shadow-lg shadow-sky-500/25 transition-all mt-4"
            >
              <span>{isLoading ? 'Authenticating...' : 'Sign In to Workspace'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Security Strip */}
          <div className="mt-8 pt-6 border-t border-white/10 text-center">
            <div className="flex items-center justify-center gap-4 text-[10px] font-mono text-slate-500 uppercase tracking-wider">
              <span>AES-256 Storage</span>
              <span>•</span>
              <span>Zero Model Training</span>
              <span>•</span>
              <span>SOC2 Type II</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-4 text-center text-xs text-slate-600 border-t border-white/5">
        AskItAll Enterprise Platform &copy; 2026. All rights reserved.
      </footer>
    </div>
  );
}
