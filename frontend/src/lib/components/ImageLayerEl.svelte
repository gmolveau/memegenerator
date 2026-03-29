<script lang="ts">
	import type { ImageLayer } from '$lib/types';
	import { createLayerInteractions } from './layerInteractions.svelte';

	interface Props {
		layer: ImageLayer;
		selected: boolean;
		canvasHovered: boolean;
		onselect: () => void;
		onupdate: (patch: Partial<ImageLayer>) => void;
		onremove: () => void;
	}

	let { layer, selected, canvasHovered, onselect, onupdate, onremove: _onremove }: Props = $props();

	let el = $state<HTMLDivElement | null>(null);

	const interactions = createLayerInteractions({
		getEl: () => el,
		getLayer: () => layer,
		onupdate,
		onselect,
		minWidth: 20,
		minHeight: 20
	});
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	bind:this={el}
	data-layer="image"
	role="button"
	tabindex="0"
	class="absolute cursor-move touch-none {selected || canvasHovered
		? 'ring-2 ring-indigo-500 ring-offset-1'
		: ''}"
	style="left:{layer.x}px; top:{layer.y}px; width:{layer.width}px; height:{layer.height}px; transform:rotate({layer.rotation}deg); transform-origin:center;"
	onpointerdown={interactions.onPointerDown}
	onpointermove={interactions.onPointerMove}
	onpointerup={interactions.onPointerUp}
>
	<img
		src={layer.src}
		alt="overlay"
		draggable="false"
		class="pointer-events-none h-full w-full object-cover"
	/>

	{#if selected}
		<!-- Rotation handle -->
		<div
			data-rotate="true"
			class="absolute -top-7 left-1/2 flex h-5 w-5 -translate-x-1/2 cursor-grab items-center justify-center rounded-full bg-indigo-500 text-xs text-white opacity-90 select-none active:cursor-grabbing"
			onpointerdown={interactions.onRotateDown}
			onpointermove={interactions.onRotateMove}
			onpointerup={interactions.onRotateUp}
		>
			↻
		</div>

		<!-- Resize handle -->
		<div
			data-resize="se"
			class="absolute right-0 bottom-0 h-4 w-4 cursor-se-resize bg-indigo-500 opacity-80"
			onpointerdown={interactions.onResizeDown}
			onpointermove={interactions.onResizeMove}
			onpointerup={interactions.onResizeUp}
		></div>
	{/if}
</div>
