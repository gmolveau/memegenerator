<script lang="ts">
	import type { ImageLayer } from '$lib/types';

	interface Props {
		layer: ImageLayer;
		selected: boolean;
		onselect: () => void;
		onupdate: (patch: Partial<ImageLayer>) => void;
		onremove: () => void;
	}

	let { layer, selected, onselect, onupdate, onremove }: Props = $props();

	let el = $state<HTMLDivElement | null>(null);

	// --- Drag ---
	let dragging = $state(false);
	let startX = 0,
		startY = 0,
		startLayerX = 0,
		startLayerY = 0;

	function onPointerDown(e: PointerEvent) {
		const target = e.target as HTMLElement;
		if (target.dataset.resize || target.dataset.rotate) return;
		e.stopPropagation();
		onselect();
		dragging = true;
		startX = e.clientX;
		startY = e.clientY;
		startLayerX = layer.x;
		startLayerY = layer.y;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onPointerMove(e: PointerEvent) {
		if (!dragging) return;
		onupdate({
			x: Math.max(0, startLayerX + (e.clientX - startX)),
			y: Math.max(0, startLayerY + (e.clientY - startY))
		});
	}

	function onPointerUp() {
		dragging = false;
	}

	// --- Resize ---
	let resizing = $state(false);
	let startW = 0,
		startH = 0;

	function onResizeDown(e: PointerEvent) {
		e.stopPropagation();
		resizing = true;
		startX = e.clientX;
		startY = e.clientY;
		startW = layer.width;
		startH = layer.height;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onResizeMove(e: PointerEvent) {
		if (!resizing) return;
		onupdate({
			width: Math.max(20, startW + (e.clientX - startX)),
			height: Math.max(20, startH + (e.clientY - startY))
		});
	}

	function onResizeUp() {
		resizing = false;
	}

	// --- Rotate ---
	let rotating = $state(false);
	let centerX = 0,
		centerY = 0,
		startAngle = 0,
		startRotation = 0;

	function onRotateDown(e: PointerEvent) {
		e.stopPropagation();
		rotating = true;
		const rect = el!.getBoundingClientRect();
		centerX = rect.left + rect.width / 2;
		centerY = rect.top + rect.height / 2;
		startAngle = Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);
		startRotation = layer.rotation;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onRotateMove(e: PointerEvent) {
		if (!rotating) return;
		const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);
		onupdate({ rotation: startRotation + (angle - startAngle) });
	}

	function onRotateUp() {
		rotating = false;
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	bind:this={el}
	data-layer="image"
	role="button"
	tabindex="0"
	class="absolute cursor-move touch-none {selected ? 'ring-2 ring-indigo-500 ring-offset-1' : ''}"
	style="left:{layer.x}px; top:{layer.y}px; width:{layer.width}px; height:{layer.height}px; transform:rotate({layer.rotation}deg); transform-origin:center;"
	onpointerdown={onPointerDown}
	onpointermove={onPointerMove}
	onpointerup={onPointerUp}
	onkeydown={(e) => e.key === 'Delete' && onremove()}
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
			onpointerdown={onRotateDown}
			onpointermove={onRotateMove}
			onpointerup={onRotateUp}
		>
			↻
		</div>

		<!-- Resize handle -->
		<div
			data-resize="se"
			class="absolute right-0 bottom-0 h-4 w-4 cursor-se-resize bg-indigo-500 opacity-80"
			onpointerdown={onResizeDown}
			onpointermove={onResizeMove}
			onpointerup={onResizeUp}
		></div>
	{/if}
</div>
