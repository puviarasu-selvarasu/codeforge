// Alpine.js global store
document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        // global state
        isLoading: false,
        error: null,
        // we'll expand later
    });
});