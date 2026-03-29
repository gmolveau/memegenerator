<script lang="ts">
	import { auth } from '$lib/stores/auth.svelte';
	import { loginUrl } from '$lib/api/auth';
</script>

<header class="border-b bg-white shadow-sm">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
		<a href="/" class="text-xl font-bold tracking-tight text-indigo-700">Meme Generator</a>
		<div class="flex items-center gap-4">
			{#if auth.user}
				{#if auth.user.role === 'admin' || auth.user.role === 'superadmin'}
					<a href="/admin" class="text-sm text-gray-500 hover:text-indigo-600">Admin</a>
				{/if}
				<a
					href="/upload"
					class="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
					>Upload</a
				>
				<a href="/templates" class="text-sm font-medium text-gray-700 hover:text-indigo-600"
					>{auth.user.name}</a
				>
			{:else if auth.user === null}
				<a href={loginUrl('/')} class="text-sm text-indigo-600 hover:text-indigo-800">Login</a>
			{/if}
		</div>
	</div>
</header>
