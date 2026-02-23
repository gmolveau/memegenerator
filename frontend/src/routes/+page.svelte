<script lang="ts">
	import MemeEditor from '$lib/components/MemeEditor.svelte';
	import TemplateGallery from '$lib/components/TemplateGallery.svelte';
	import { editor } from '$lib/stores/editor.svelte';
	import type { Template } from '$lib/types';

	type View = 'gallery' | 'editor';
	let view = $state<View>('gallery');

	function selectTemplate(template: Template) {
		editor.setTemplate(template);
		view = 'editor';
	}

	function backToGallery() {
		view = 'gallery';
	}
</script>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="border-b bg-white shadow-sm">
		<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
			<h1 class="text-xl font-bold tracking-tight text-indigo-700">Meme Generator</h1>
			{#if view === 'editor' && editor.template}
				<div class="flex items-center gap-3">
					<span class="text-sm text-gray-500">Editing: <strong>{editor.template.name}</strong></span
					>
					<button
						onclick={backToGallery}
						class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
					>
						&larr; Back to gallery
					</button>
				</div>
			{/if}
		</div>
	</header>

	<!-- Main content -->
	<main class="mx-auto max-w-6xl px-4 py-6">
		{#if view === 'gallery'}
			<div class="mb-6">
				<h2 class="text-2xl font-semibold text-gray-800">Choose a template</h2>
				<p class="mt-1 text-sm text-gray-500">
					Browse, search, or upload your own image to get started.
				</p>
			</div>
			<TemplateGallery onselect={selectTemplate} />
		{:else}
			<div class="mb-4 overflow-x-auto">
				<MemeEditor />
			</div>
		{/if}
	</main>
</div>
