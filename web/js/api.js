'use strict';

/**
 * Fetch data from a URL.
 * @param {string} url - The URL to fetch data from.
 * @returns {Promise<Object>} - A promise that resolves to the fetched data.
 */
export async function startFetch(url, json) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        if (json) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
}
