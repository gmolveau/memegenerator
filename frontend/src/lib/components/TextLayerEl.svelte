<script lang="ts">
	import type { TextLayer } from '$lib/types';
	import { createLayerInteractions } from './layerInteractions.svelte';

	interface Props {
		layer: TextLayer;
		selected: boolean;
		canvasHovered: boolean;
		onselect: () => void;
		onupdate: (patch: Partial<TextLayer>) => void;
		onremove: () => void;
	}

	let { layer, selected, canvasHovered, onselect, onupdate, onremove }: Props = $props();

	let el = $state<HTMLDivElement | null>(null);
	let textareaEl = $state<HTMLTextAreaElement | null>(null);

	// --- Inline editing ---
	let editing = $state(false);

	function startEditing(e: MouseEvent) {
		e.stopPropagation();
		onselect();
		editing = true;
	}

	function stopEditing() {
		editing = false;
	}

	function onTextareaKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			e.stopPropagation();
			stopEditing();
		}
		// Allow Enter for new lines — do not stop propagation
	}

	// Auto-focus and select-all when editing begins
	$effect(() => {
		if (editing && textareaEl) {
			textareaEl.focus();
			textareaEl.select();
		}
	});

	const interactions = createLayerInteractions({
		getEl: () => el,
		getLayer: () => layer,
		onupdate,
		onselect,
		isEditing: () => editing,
		minWidth: 60,
		minHeight: 30
	});

	// --- Derived styles ---
	const fontStyle = $derived(
		`${layer.italic ? 'italic ' : ''}${layer.bold ? 'bold ' : ''}${layer.fontSize}px ${layer.fontFamily}`
	);
	const textShadow = $derived(
		layer.outlineWidth > 0
			? `${layer.outlineWidth}px ${layer.outlineWidth}px 0 ${layer.outlineColor},
         -${layer.outlineWidth}px -${layer.outlineWidth}px 0 ${layer.outlineColor},
         ${layer.outlineWidth}px -${layer.outlineWidth}px 0 ${layer.outlineColor},
         -${layer.outlineWidth}px ${layer.outlineWidth}px 0 ${layer.outlineColor}`
			: 'none'
	);
	const vJustify = $derived(
		layer.verticalAlign === 'middle'
			? 'center'
			: layer.verticalAlign === 'bottom'
				? 'flex-end'
				: 'flex-start'
	);

	const sharedTextStyle = $derived(`
		font: ${fontStyle};
		color: ${layer.color};
		text-align: ${layer.align};
		text-shadow: ${textShadow};
		text-transform: ${layer.allCaps ? 'uppercase' : 'none'};
		line-height: 1.2;
		padding: 4px;
	`);
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	bind:this={el}
	data-layer="text"
	role="button"
	tabindex="0"
	class="absolute touch-none {editing ? 'cursor-text' : 'cursor-move'} {selected || canvasHovered
		? 'ring-2 ring-indigo-500 ring-offset-1'
		: ''}"
	style="left:{layer.x}px; top:{layer.y}px; width:{layer.width}px; height:{layer.height}px; transform:rotate({layer.rotation}deg); transform-origin:center;"
	onpointerdown={interactions.onPointerDown}
	onpointermove={interactions.onPointerMove}
	onpointerup={interactions.onPointerUp}
	ondblclick={startEditing}
>
	{#if editing}
		<textarea
			bind:this={textareaEl}
			value={layer.text}
			oninput={(e) => onupdate({ text: (e.currentTarget as HTMLTextAreaElement).value })}
			onblur={stopEditing}
			onkeydown={onTextareaKeydown}
			class="absolute inset-0 h-full w-full resize-none bg-transparent break-words outline-none"
			style={sharedTextStyle}
		></textarea>
	{:else}
		<div
			style="display:flex; flex-direction:column; justify-content:{vJustify}; height:100%; width:100%; overflow:hidden;"
		>
			<div class="break-words whitespace-pre-wrap" style={sharedTextStyle}>
				{layer.text}
			</div>
		</div>
	{/if}

	{#if selected && !editing}
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
