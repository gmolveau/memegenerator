<script lang="ts">
	import { editor } from '$lib/stores/editor.svelte';
	import TextLayerEl from './TextLayerEl.svelte';
	import ImageLayerEl from './ImageLayerEl.svelte';
	import EditorToolbar from './EditorToolbar.svelte';
	import LayerListPanel from './LayerListPanel.svelte';

	interface Props {
		templateMode?: boolean;
		onsave?: () => void;
		ondelete?: () => void;
		onimageupload?: (file: File) => void;
	}

	let { templateMode = false, onsave, ondelete, onimageupload }: Props = $props();

	const CANVAS_WIDTH = 600;
	let canvasHeight = $state(450);
	let templateImg = $state<HTMLImageElement | null>(null);
	let canvasHovered = $state(false);

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
	<EditorToolbar {canvasHeight} {templateImg} {templateMode} {onsave} {ondelete} />

	<!-- Editor canvas -->
	<div class="flex flex-1 flex-col gap-3">
		{#if !editor.template && onimageupload}
			<label
				class="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-gray-300 bg-white text-gray-400 hover:border-indigo-400 hover:text-indigo-500"
				style="width:{CANVAS_WIDTH}px; height:{canvasHeight}px;"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-12 w-12"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M3 16.5V19a1.5 1.5 0 001.5 1.5h15A1.5 1.5 0 0021 19v-2.5M12 3v13m0 0l-3.5-3.5M12 16l3.5-3.5"
					/>
				</svg>
				<span class="text-sm font-medium">Click to upload an image</span>
				<input
					type="file"
					accept="image/jpeg,image/png,image/webp,image/bmp"
					class="hidden"
					onchange={(e) => {
						const f = (e.currentTarget as HTMLInputElement).files?.[0];
						if (f) onimageupload(f);
					}}
				/>
			</label>
		{:else}
			<div
				onclick={deselect}
				role="presentation"
				class="relative select-none"
				style="width:{CANVAS_WIDTH}px; height:{canvasHeight}px;"
				onmouseenter={() => (canvasHovered = true)}
				onmouseleave={() => (canvasHovered = false)}
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
						{canvasHovered}
						onselect={() => editor.selectLayer(layer.id)}
						onupdate={(patch) => editor.updateImageLayer(layer.id, patch)}
						onremove={() => editor.removeImageLayer(layer.id)}
					/>
				{/each}

				{#each editor.textLayers as layer (layer.id)}
					<TextLayerEl
						{layer}
						selected={editor.selectedLayerId === layer.id}
						{canvasHovered}
						onselect={() => editor.selectLayer(layer.id)}
						onupdate={(patch) => editor.updateTextLayer(layer.id, patch)}
						onremove={() => editor.removeTextLayer(layer.id)}
					/>
				{/each}
			</div>
		{/if}
	</div>

	<LayerListPanel canvasWidth={CANVAS_WIDTH} />
</div>
