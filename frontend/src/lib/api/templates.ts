import { API_URL, apiFetch } from '$lib/api/client';
import type { Template, TemplateTextLayer } from '$lib/types';

function normalizeUrl(url: string): string {
	return url.startsWith('http') ? url : `${API_URL}${url}`;
}

function toTemplate(t: Template): Template {
	return { ...t, image_url: normalizeUrl(t.image_url) };
}

export async function fetchTemplates(
	search?: string,
	limit = 40,
	offset = 0
): Promise<{ templates: Template[]; total: number }> {
	const url = new URL(`${API_URL}/templates`);
	if (search) url.searchParams.set('search', search);
	url.searchParams.set('limit', String(limit));
	url.searchParams.set('offset', String(offset));
	const res = await fetch(url.toString());
	if (!res.ok) throw new Error(`Failed to fetch templates: ${res.status}`);
	const data = await res.json();
	return { templates: data.templates.map(toTemplate), total: data.total };
}

export async function incrementPopularity(id: number): Promise<void> {
	await apiFetch(`/templates/${id}/popularity`, { method: 'POST' });
}

export async function fetchTemplate(id: number): Promise<Template> {
	const res = await fetch(`${API_URL}/templates/${id}`);
	if (!res.ok) throw new Error(`Failed to fetch template: ${res.status}`);
	return toTemplate(await res.json());
}

export async function updateTemplate(
	id: number,
	name: string,
	keywords: string[],
	text_layers?: TemplateTextLayer[]
): Promise<Template> {
	const body: Record<string, unknown> = { name, keywords };
	if (text_layers !== undefined) body.text_layers = text_layers;
	const res = await apiFetch(`/templates/${id}`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});
	if (!res.ok) throw new Error(`Update failed: ${res.status}`);
	return toTemplate(await res.json());
}

export async function fetchMyTemplates(
	limit = 40,
	offset = 0
): Promise<{ templates: Template[]; total: number }> {
	const res = await apiFetch(`/templates/mine?limit=${limit}&offset=${offset}`);
	if (!res.ok) throw new Error(`Failed to fetch templates: ${res.status}`);
	const data = await res.json();
	return { templates: data.templates.map(toTemplate), total: data.total };
}

export async function uploadTemplate(
	name: string,
	keywords: string[],
	file: File
): Promise<Template> {
	const form = new FormData();
	form.append('name', name);
	form.append('keywords', keywords.join(','));
	form.append('file', file);
	const res = await apiFetch('/templates', { method: 'POST', body: form });
	if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
	return toTemplate(await res.json());
}
