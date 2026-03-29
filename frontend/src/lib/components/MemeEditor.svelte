<script lang="ts">
	import { editor } from '$lib/stores/editor.svelte';
	import TextLayerEl from './TextLayerEl.svelte';
	import ImageLayerEl from './ImageLayerEl.svelte';
	import EditorToolbar from './EditorToolbar.svelte';
	import LayerListPanel from './LayerListPanel.svelte';

	const CANVAS_WIDTH = 600;
	let canvasHeight = $state(450);
	let templateImg = $state<HTMLImageElement | null>(null);

	// Recompute canvas height when template changes.
	// crossOrigin must be set BEFORE src so the browser makes a CORS request,
	// which is required for canvas.toDataURL() to work without tainting the canvas.
	$effect(() => {
		if (!editor.template) return;
		const img = new Image();
		img.crossOrigin = 'anonymous';
		img.onload = () => {
			canvasHeight = Math.round((img.naturalHeight / img.naturalWidth) * CANVAS_WIDTH);
			templateImg = img;
		};
		img.src = editor.template.image_url;
	});

	const filterMap: Record<string, string> = {
		none: 'none',
		grayscale: 'grayscale(100%)',
		blur: 'blur(3px)',
		sharpen: 'contrast(1.4) brightness(1.1)',
		sepia: 'sepia(100%)',
		invert: 'invert(100%)'
	};

	function deselect(e: MouseEvent) {
		if ((e.target as HTMLElement).closest('[data-layer]')) return;
		editor.selectLayer(null);
	}
</script>

<div class="flex flex-col gap-4 lg:flex-row">
	<EditorToolbar {canvasHeight} {templateImg} />

	<!-- Editor canvas -->
	<div class="flex flex-1 flex-col gap-3">
		<div
			onclick={deselect}
			role="presentation"
			class="relative select-none"
			style="width:{CANVAS_WIDTH}px; height:{canvasHeight}px;"
		>
			<!-- Background image clipped to rounded border -->
			<div
				class="pointer-events-none absolute inset-0 overflow-hidden rounded-lg border border-gray-300 bg-gray-900"
			>
				{#if editor.template}
					<img
						src={editor.template.image_url}
						alt={editor.template.name}
						draggable="false"
						crossorigin="anonymous"
						class="h-full w-full object-cover"
						style="filter:{filterMap[editor.effect]}"
					/>
				{/if}
			</div>

			<!-- Layers (overflow allowed for rotation handles) -->
			{#each editor.imageLayers as layer (layer.id)}
				<ImageLayerEl
					{layer}
					selected={editor.selectedLayerId === layer.id}
					onselect={() => editor.selectLayer(layer.id)}
					onupdate={(patch) => editor.updateImageLayer(layer.id, patch)}
					onremove={() => editor.removeImageLayer(layer.id)}
				/>
			{/each}

			{#each editor.textLayers as layer (layer.id)}
				<TextLayerEl
					{layer}
					selected={editor.selectedLayerId === layer.id}
					onselect={() => editor.selectLayer(layer.id)}
					onupdate={(patch) => editor.updateTextLayer(layer.id, patch)}
					onremove={() => editor.removeTextLayer(layer.id)}
				/>
			{/each}
		</div>
	</div>

	<LayerListPanel canvasWidth={CANVAS_WIDTH} />
</div>
