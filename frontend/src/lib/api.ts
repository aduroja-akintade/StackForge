import { supabase, isSupabaseConfigured } from './supabaseClient';

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL || 'https://stackforge-backend.onrender.com'
).replace(/\/$/, '');

async function requestJSON(path: string, body?: object, timeoutMs = 30000) {
  if (!isSupabaseConfigured) {
    throw new Error('Authentication is not configured. Contact the site administrator.');
  }
  const { data, error } = await supabase.auth.getSession();
  if (error || !data.session?.access_token) {
    throw new Error('Please sign in with Google before using this feature.');
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: body ? 'POST' : 'GET',
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
      signal: controller.signal,
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      const detail = payload?.detail;
      throw new Error(
        typeof detail === 'string' ? detail :
        response.status === 401 ? 'Your session has expired. Sign in again.' :
        `Request failed (HTTP ${response.status}).`
      );
    }
    return payload;
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('The service did not respond in time. Please try again.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export async function analyseJD(jdText: string, _userId?: string) {
  return requestJSON('/analyse/', { jd_text: jdText });
}

export async function getAnalysisHistory(_userId?: string) {
  return requestJSON('/analyse/history');
}

export async function recommendProjects(jdText: string, currentSkills?: string[], _userId?: string) {
  return requestJSON('/recommend/', { jd_text: jdText, current_skills: currentSkills });
}

export async function generateImplementationPlan(
  projectTitle: string, projectDescription?: string, techStack?: string, _userId?: string
) {
  return requestJSON('/implement/', {
    project_title: projectTitle,
    project_description: projectDescription,
    tech_stack: techStack,
  }, 90000);
}

export async function generateUpgradeAdvice(projectDescription: string, currentTechStack?: string) {
  return requestJSON('/upgrade/', {
    project_description: projectDescription,
    current_tech_stack: currentTechStack,
  }, 60000);
}
