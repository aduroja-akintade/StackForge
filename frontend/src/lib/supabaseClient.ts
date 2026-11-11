import { createClient } from '@supabase/supabase-js';

// NEXT_PUBLIC_SUPABASE_ANON_KEY is intended to be public. Never expose a service-role key.
const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const isSupabaseConfigured = Boolean(url && anonKey);

// Safe inert placeholders permit static builds when CI has no deployment secrets.
// Authentication is explicitly disabled unless both environment variables exist.
export const supabase = createClient(
  url || 'https://example.supabase.co',
  anonKey || 'unconfigured-public-key',
  {
    auth: {
      persistSession: isSupabaseConfigured,
      autoRefreshToken: isSupabaseConfigured,
      detectSessionInUrl: isSupabaseConfigured,
    },
  }
);
