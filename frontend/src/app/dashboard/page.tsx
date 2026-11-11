'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { getAnalysisHistory } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Clock, BookOpen, ChevronRight, Settings } from 'lucide-react';

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/');
      return;
    }

    if (user) {
      const fetchHistory = async () => {
        try {
          const data = await getAnalysisHistory(user.id);
          setHistory(data.history || []);
        } catch (err: any) {
          setError(err.message || 'Failed to load history');
        } finally {
          setLoading(false);
        }
      };
      fetchHistory();
    }
  }, [user, authLoading, router]);

  if (authLoading || (Boolean(user) && loading)) {
    return (
      <div className="flex h-screen items-center justify-center bg-black">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-t-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-6xl">
      <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-4xl font-extrabold text-white mb-2">Welcome Back</h1>
          <p className="text-gray-400">Manage your analyses and implementation roadmaps.</p>
        </div>
        <div className="flex gap-4">
          <div className="px-4 py-2 bg-zinc-900 border border-gray-800 rounded-lg text-sm text-gray-400 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            Free Tier
          </div>
          <button className="p-2 bg-zinc-900 border border-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors">
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        <div className="lg:col-span-2 space-y-8">
          <section>
            <div className="flex items-center gap-3 mb-6">
              <Clock className="w-5 h-5 text-blue-500" />
              <h2 className="text-xl font-bold text-white">Recent Analyses</h2>
            </div>
            
            {history.length === 0 ? (
              <div className="p-12 border border-dashed border-gray-800 rounded-3xl text-center">
                <p className="text-gray-500 mb-6">No analysis history yet.</p>
                <button 
                  onClick={() => router.push('/analyse')}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-bold transition-all"
                >
                  Start Your First Analysis
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {history.map((item, idx) => (
                  <div key={idx} className="p-6 border border-gray-800 rounded-2xl bg-zinc-900/40 hover:bg-zinc-900 transition-all flex items-center justify-between group">
                    <div className="max-w-md">
                      <h3 className="font-bold text-white mb-1 truncate">
                        {item.jd_text.substring(0, 60)}...
                      </h3>
                      <p className="text-xs text-gray-500">
                        {new Date(item.created_at).toLocaleDateString()} • {item.analysis_json.required_skills?.length || 0} Skills identified
                      </p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-blue-500 transition-colors" />
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        <div className="space-y-8">
          <section className="p-8 border border-gray-800 rounded-3xl bg-zinc-900/60">
            <div className="flex items-center gap-3 mb-6">
              <BookOpen className="w-5 h-5 text-purple-500" />
              <h2 className="text-xl font-bold text-white">Your Projects</h2>
            </div>
            <p className="text-sm text-gray-500 mb-6">
              Save implementation plans to see them listed here for quick access.
            </p>
            <div className="space-y-4">
              <div className="text-center py-8 grayscale opacity-50">
                <span className="text-4xl block mb-4">📂</span>
                <p className="text-xs font-bold uppercase tracking-widest">Coming Soon</p>
              </div>
            </div>
          </section>

          <section className="p-8 border border-blue-900/20 bg-blue-900/5 rounded-3xl">
            <h2 className="text-lg font-bold text-white mb-4">Upgrade to Pro</h2>
            <p className="text-sm text-gray-400 mb-6">
              Get unlimited analyses, custom implementation roadmaps, and priority AI access.
            </p>
            <button 
              onClick={() => alert("Pro Tier Coming Soon! Subscribe to our newsletter for early access.")}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-xl text-sm font-bold transition-all shadow-lg shadow-blue-900/40"
            >
              Unlock Unlimited Access
            </button>
          </section>
        </div>
      </div>
    </div>
  );
}
