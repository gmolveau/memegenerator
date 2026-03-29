<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import AppHeader from '$lib/components/AppHeader.svelte';
	import TemplateGallery from '$lib/components/TemplateGallery.svelte';
	import { editor } from '$lib/stores/editor.svelte';
	import type { Template } from '$lib/types';

	function selectTemplate(template: Template) {
		editor.setTemplate(template);
		goto(resolve(`/templates/${template.id}`));
	}
</script>

<div class="min-h-screen bg-gray-50">
	<AppHeader />

	<main class="mx-auto max-w-6xl px-4 py-6">
		<div class="mb-6">
			<h2 class="text-2xl font-semibold text-gray-800">Choose a template</h2>
			<p class="mt-1 text-sm text-gray-500">
				Browse, search, or upload your own image to get started.- Login to create new templates. -
				All templates are public.
			</p>
		</div>
		<TemplateGallery onselect={selectTemplate} />
	</main>
</div>
