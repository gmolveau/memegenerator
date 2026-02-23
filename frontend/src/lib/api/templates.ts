import type { Template } from '$lib/types';

const BASE = import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000';

export async function fetchTemplates(
	search?: string,
	limit = 40,
	offset = 0
): Promise<{ templates: Template[]; total: number }> {
	const url = new URL(`${BASE}/api/templates`);
	if (search) url.searchParams.set('search', search);
	url.searchParams.set('limit', String(limit));
	url.searchParams.set('offset', String(offset));
	const res = await fetch(url.toString());
	if (!res.ok) throw new Error(`Failed to fetch templates: ${res.status}`);
	const data = await res.json();
	return {
		templates: data.templates.map((t: Template) => ({
			...t,
			image_url: t.image_url.startsWith('http') ? t.image_url : `${BASE}${t.image_url}`
		})),
		total: data.total
	};
}

export async function updateTemplate(
	id: number,
	name: string,
	keywords: string[]
): Promise<Template> {
	const res = await fetch(`${BASE}/api/templates/${id}`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ name, keywords })
	});
	if (!res.ok) throw new Error(`Update failed: ${res.status}`);
	const t: Template = await res.json();
	return {
		...t,
		image_url: t.image_url.startsWith('http') ? t.image_url : `${BASE}${t.image_url}`
	};
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
	const res = await fetch(`${BASE}/api/templates`, { method: 'POST', body: form });
	if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
	const t: Template = await res.json();
	return {
		...t,
		image_url: t.image_url.startsWith('http') ? t.image_url : `${BASE}${t.image_url}`
	};
}
