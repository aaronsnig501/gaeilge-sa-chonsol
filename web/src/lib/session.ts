import { writable } from 'svelte/store';
import type { Session } from '@supabase/supabase-js';

export const supabaseSession = writable<Session | null>(null);
export const supabaseEnabled = writable(false);
