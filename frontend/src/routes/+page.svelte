<script lang="ts">
	import TemplateGallery from '$lib/components/TemplateGallery.svelte';
	import { editor } from '$lib/stores/editor.svelte';
	import type { Template } from '$lib/types';
	import { goto } from '$app/navigation';

	function selectTemplate(template: Template) {
		editor.setTemplate(template);
		goto('/editor');
	}
</script>

<div class="min-h-screen bg-gray-50">
	<header class="border-b bg-white shadow-sm">
		<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
			<h1 class="text-xl font-bold tracking-tight text-indigo-700">Meme Generator</h1>
			<a href="/admin" class="text-sm text-gray-500 hover:text-indigo-600">Admin</a>
		</div>
	</header>

	<main class="mx-auto max-w-6xl px-4 py-6">
		<div class="mb-6">
			<h2 class="text-2xl font-semibold text-gray-800">Choose a template</h2>
			<p class="mt-1 text-sm text-gray-500">
				Browse, search, or upload your own image to get started.
			</p>
		</div>
		<TemplateGallery onselect={selectTemplate} />
	</main>
</div>
