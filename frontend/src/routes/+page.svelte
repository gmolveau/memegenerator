<script lang="ts">
	import TemplateGallery from '$lib/components/TemplateGallery.svelte';
	import { editor } from '$lib/stores/editor.svelte';
	import type { Template } from '$lib/types';
	import { goto } from '$app/navigation';
	import { getMe, loginUrl, logout, type User } from '$lib/api/auth';

	let user = $state<User | null>(null);

	$effect(() => {
		getMe().then((u) => (user = u));
	});

	function selectTemplate(template: Template) {
		editor.setTemplate(template);
		goto('/editor');
	}
</script>

<div class="min-h-screen bg-gray-50">
	<header class="border-b bg-white shadow-sm">
		<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
			<h1 class="text-xl font-bold tracking-tight text-indigo-700">Meme Generator</h1>
			<div class="flex items-center gap-4">
				{#if user}
					{#if user.role === 'admin' || user.role === 'superadmin'}
						<a href="/admin" class="text-sm text-gray-500 hover:text-indigo-600">Admin</a>
					{/if}
					<a href="/templates" class="text-sm text-gray-500 hover:text-indigo-600">Templates</a>
					<span class="text-sm font-medium text-gray-700">{user.name}</span>
					<button
						onclick={() => logout().then(() => (user = null))}
						class="text-sm text-gray-400 hover:text-red-500">(logout)</button
					>
				{:else}
					<a href={loginUrl('/')} class="text-sm text-indigo-600 hover:text-indigo-800">Login</a>
				{/if}
			</div>
		</div>
	</header>

	<main class="mx-auto max-w-6xl px-4 py-6">
		<div class="mb-6">
			<h2 class="text-2xl font-semibold text-gray-800">Choose a template</h2>
			<p class="mt-1 text-sm text-gray-500">
				Browse, search, or upload your own image to get started.
			</p>
		</div>
		<TemplateGallery onselect={selectTemplate} authenticated={!!user} />
	</main>
</div>
