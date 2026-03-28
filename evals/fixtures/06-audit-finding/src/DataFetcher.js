/**
 * Fetches data from the given API endpoint.
 *
 * BUG: No timeout or AbortController — if the server hangs, the request
 * waits forever and the UI stays in a loading state indefinitely.
 */
export async function fetchData(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  const json = await response.json();
  return json;
}
