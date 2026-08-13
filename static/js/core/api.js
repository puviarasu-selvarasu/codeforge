// Simple fetch wrapper
async function apiFetch(endpoint, options = {}) {
    const response = await fetch(endpoint, {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
        },
        ...options,
    });
    if (!response.ok) {
        const error = await response.text();
        throw new Error(error || 'API request failed');
    }
    return response.json();
}