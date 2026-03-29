import { env } from '$env/dynamic/public';

export const API_URL = env.PUBLIC_API_URL;

export function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
	return fetch(`${API_URL}${path}`, { ...init, credentials: 'include' });
}
