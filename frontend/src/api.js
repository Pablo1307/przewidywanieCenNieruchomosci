export async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL || ''}/api${path}`, { ...options, signal: controller.signal });
    const data = await response.json();
    if (!response.ok) {
      const message = Array.isArray(data.detail) ? data.detail.map(item => `${item.loc.at(-1)}: ${item.msg}`).join('; ') : data.detail;
      throw new Error(message || 'Nie udało się pobrać danych.');
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Przekroczono czas oczekiwania na API. Spróbuj ponownie.');
    if (error instanceof TypeError || error instanceof SyntaxError) throw new Error('Nie można połączyć się z API. Uruchom backend na porcie 8000.');
    throw error;
  } finally { clearTimeout(timeout); }
}
