<script lang="ts">
	import type { Template } from '$lib/types';

	interface Props {
		template: Template;
		editingId: number | null;
		editName: string;
		editKeywords: string[];
		keywordInput: string;
		saving: boolean;
		saveError: string;
		canSave: boolean;
		showId?: boolean;
		onstartEdit: (t: Template) => void;
		oncancelEdit: () => void;
		onremoveKeyword: (kw: string) => void;
		onkeywordKeydown: (e: KeyboardEvent) => void;
		onaddKeyword: () => void;
		onhandleSave: () => void;
	}

	let {
		template,
		editingId,
		editName = $bindable(),
		editKeywords,
		keywordInput = $bindable(),
		saving,
		saveError,
		canSave,
		showId = false,
		onstartEdit,
		oncancelEdit,
		onremoveKeyword,
		onkeywordKeydown,
		onaddKeyword,
		onhandleSave
	}: Props = $props();

	const isEditing = $derived(editingId === template.id);
</script>

<div
	class="overflow-hidden rounded-lg border-2 bg-white shadow-sm transition {isEditing
		? 'border-indigo-500'
		: 'border-transparent hover:border-gray-300'}"
>
	<a href="/templates/{template.id}/edit" class="group relative block w-full overflow-hidden">
		<img
			src={template.image_url}
			alt={template.name}
			loading="lazy"
			class="aspect-square w-full object-cover"
		/>
		<div
			class="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 transition group-hover:opacity-100"
		>
			<span class="rounded bg-white px-2 py-1 text-xs font-medium text-gray-800">Edit</span>
		</div>
	</a>

	<div class="p-3">
		{#if isEditing}
			<div class="flex flex-col gap-2">
				<input
					type="text"
					bind:value={editName}
					placeholder="Name *"
					class="rounded border px-2 py-1 text-sm focus:ring-2 focus:outline-none {editName.trim()
						.length === 0
						? 'border-red-400 focus:ring-red-400'
						: 'border-gray-300 focus:ring-indigo-500'}"
				/>

				<div
					class="flex min-h-[2.25rem] flex-wrap items-center gap-1 rounded border bg-white px-2 py-1 text-sm focus-within:ring-2 focus-within:ring-indigo-500 {editKeywords.length ===
						0 && keywordInput === ''
						? 'border-red-400'
						: 'border-gray-300'}"
				>
					{#each editKeywords as kw}
						<span
							class="flex items-center gap-0.5 rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700"
						>
							{kw}
							<button
								type="button"
								onclick={() => onremoveKeyword(kw)}
								class="leading-none text-indigo-400 hover:text-indigo-700"
								aria-label="Remove {kw}">&times;</button
							>
						</span>
					{/each}
					<input
						type="text"
						bind:value={keywordInput}
						onkeydown={onkeywordKeydown}
						onblur={onaddKeyword}
						placeholder={editKeywords.length === 0 ? 'Keywords *' : ''}
						class="min-w-[4rem] flex-1 border-none bg-transparent text-xs outline-none placeholder:text-gray-400"
					/>
				</div>

				{#if saveError}
					<p class="text-xs text-red-600">{saveError}</p>
				{/if}

				<div class="flex gap-2">
					<button
						onclick={onhandleSave}
						disabled={!canSave || saving}
						class="flex-1 rounded bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
					>
						{saving ? 'Saving…' : 'Save'}
					</button>
					<a
						href="/templates/{template.id}/edit"
						class="rounded border border-indigo-300 px-2 py-1 text-xs text-indigo-600 hover:bg-indigo-50"
					>
						Edit Layers
					</a>
					<button
						onclick={oncancelEdit}
						class="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
					>
						Cancel
					</button>
				</div>
			</div>
		{:else}
			<p class="truncate text-sm font-medium text-gray-800">{template.name}</p>
			{#if showId}
				<p class="text-xs text-gray-400">#{template.id}</p>
			{/if}
			{#if template.keywords.length > 0}
				<div class="mt-1 flex flex-wrap gap-1">
					{#each template.keywords as kw}
						<span class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{kw}</span>
					{/each}
				</div>
			{/if}
		{/if}
	</div>
</div>
