<script lang="ts">
	import { page } from '$app/stores';
	import TemplateEditorView from '$lib/components/TemplateEditorView.svelte';

	const templateId = $derived(Number($page.params.id));
</script>

<TemplateEditorView {templateId} />
