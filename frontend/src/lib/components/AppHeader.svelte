<script lang="ts">
	import { resolve } from '$app/paths';
	import { loginUrl } from '$lib/api/auth';
	import { auth } from '$lib/stores/auth.svelte';
</script>

<header class="border-b bg-white shadow-sm">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
		<div class="flex items-baseline gap-2">
			<a href={resolve('/')} class="text-xl font-bold tracking-tight text-indigo-700"
				>Meme Generator</a
			>
			<span class="text-xs text-gray-400">v{__APP_VERSION__}</span>
		</div>
		<div class="flex items-center gap-4">
			{#if auth.user}
				{#if auth.user.role === 'admin' || auth.user.role === 'superadmin'}
					<a href={resolve('/admin')} class="text-sm text-gray-500 hover:text-indigo-600">Admin</a>
				{/if}
				<a
					href={resolve('/upload')}
					class="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
					>Upload</a
				>
				<a
					href={resolve('/templates')}
					class="text-sm font-medium text-gray-700 hover:text-indigo-600">{auth.user.name}</a
				>
			{:else if auth.user === null}
				<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
				<a href={loginUrl('/')} class="text-sm text-indigo-600 hover:text-indigo-800">Login</a>
			{/if}
		</div>
	</div>
</header>
