<script lang="ts">
	import MemeEditor from '$lib/components/MemeEditor.svelte';
	import { editor } from '$lib/stores/editor.svelte';
	import { goto } from '$app/navigation';

	// Redirect to home if no template is loaded (e.g. direct navigation or page refresh)
	$effect(() => {
		if (!editor.template) {
			goto('/');
		}
	});
</script>

{#if editor.template}
	<div class="min-h-screen bg-gray-50">
		<header class="border-b bg-white shadow-sm">
			<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
				<h1 class="text-xl font-bold tracking-tight text-indigo-700">Meme Generator</h1>
				<div class="flex items-center gap-3">
					<span class="text-sm text-gray-500"
						>Editing: <strong>{editor.template.name}</strong></span
					>
					<a
						href="/"
						class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
					>
						&larr; Back to gallery
					</a>
				</div>
			</div>
		</header>

		<main class="mx-auto max-w-6xl px-4 py-6">
			<div class="overflow-x-auto">
				<MemeEditor />
			</div>
		</main>
	</div>
{/if}
