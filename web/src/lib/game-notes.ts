import type { Component } from 'svelte';

const noteModules = import.meta.glob('/src/routes/games/*/*/notes/+page.md', { eager: true });

interface NotesModule {
	default?: Component;
	metadata?: {
		title?: string;
	};
}

export function getNotesComponent(consoleId: string, gameId: string): Component | null {
	const routePath = `/src/routes/games/${consoleId}/${gameId}/notes/+page.md`;
	const module = noteModules[routePath] as NotesModule | undefined;
	return module?.default ?? null;
}
