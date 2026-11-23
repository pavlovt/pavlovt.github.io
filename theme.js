// Light/dark toggle. With no stored value the site follows the system setting.
// A click switches to the opposite of what is shown; switching back to the
// system's own scheme removes the stored value instead of pinning it.
const meta = document.querySelector('meta[name="color-scheme"]');
const systemDark = matchMedia('(prefers-color-scheme: dark)');

function readStored() {
  try { return localStorage.getItem('color-scheme'); } catch { return null; }
}

function apply(value) {
  meta.content = value ?? 'light dark';
}

document.getElementById('theme-toggle').addEventListener('click', () => {
  const system = systemDark.matches ? 'dark' : 'light';
  const shown = meta.content === 'light dark' ? system : meta.content;
  const target = shown === 'dark' ? 'light' : 'dark';
  const stored = target === system ? null : target;
  try {
    if (stored) localStorage.setItem('color-scheme', stored);
    else localStorage.removeItem('color-scheme');
  } catch {}
  apply(stored);
});

addEventListener('storage', (event) => {
  if (event.key === 'color-scheme' || event.key === null) apply(readStored());
});
