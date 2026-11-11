'use client';

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';

const features = [
  {
    title: "Job Description Analyser",
    description: "Paste a Cloud/DevOps job description and identify exactly which skills and projects you&apos;re missing.",
    href: "/analyse",
    icon: "🔍",
  },
  {
    title: "Project Recommender",
    description: "Get a ranked list of 3-5 high-impact projects tailored to the roles you actually want.",
    href: "/recommend",
    icon: "🎯",
  },
  {
    title: "Implementation Plans",
    description: "Step-by-step technical guides with architecture, file structures, and verification steps.",
    href: "/implement",
    icon: "🛠️",
  },
  {
    title: "Project Upgrader",
    description: "Analyse your existing projects and learn how to upgrade them to production-grade quality.",
    href: "/upgrade",
    icon: "🚀",
  }
];

export default function Home() {
  const { user } = useAuth();
  return (
    <div className="relative min-h-screen">
      {/* Custom Background for Landing Page */}
      <div 
        className="fixed inset-0 z-[-1] transition-all duration-1000 ease-in-out"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('/background.jpeg')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      />

      <div className="flex flex-col items-center justify-center py-20 text-white">
        {/* Hero Section */}
        <section className="text-center px-4 max-w-4xl mx-auto mb-24">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8">
            Bridge the Gap Between <span className="text-blue-500">Skills</span> and <span className="text-blue-500">Success</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-400 mb-10 leading-relaxed max-w-2xl mx-auto">
            StackForge helps Cloud and DevOps engineers build the high-impact portfolios that top tech companies actually hire.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href={user ? "/dashboard" : "/analyse"} className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-lg font-bold transition-all shadow-lg shadow-blue-900/40">
              {user ? "Go to Dashboard" : "Get Started Free"}
            </Link>
            <Link href="/recommend" className="px-8 py-4 border border-gray-700 hover:bg-gray-800 rounded-lg text-lg font-bold transition-all bg-black/30 backdrop-blur-sm">
              See Recommendations
            </Link>
          </div>
        </section>

        {/* Feature Section */}
        <section className="container mx-auto px-4 py-20">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, idx) => (
              <Link key={idx} href={feature.href} className="group p-8 border border-gray-800 rounded-2xl bg-zinc-900/60 backdrop-blur-md hover:bg-zinc-900 transition-all hover:border-blue-500/50">
                <div className="text-4xl mb-6">{feature.icon}</div>
                <h2 className="text-xl font-bold mb-4 group-hover:text-blue-500 transition-colors">
                  {feature.title}
                </h2>
                <p className="text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </Link>
            ))}
          </div>
        </section>

        {/* Trust Section */}
        <section className="mt-20 py-10 opacity-50 text-center w-full max-w-3xl mx-auto border-t border-gray-900">
          <p className="text-sm font-medium uppercase tracking-widest text-gray-500">Designed for Engineers working on</p>
          <div className="flex justify-center gap-12 mt-8 text-2xl font-bold grayscale hover:grayscale-0 transition-all">
            <span>AWS</span>
            <span>Azure</span>
            <span>GCP</span>
            <span>Kubernetes</span>
            <span>Terraform</span>
          </div>
        </section>
      </div>
    </div>
  );
}
