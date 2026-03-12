const LANG_KEY = 'osint_lang';

const translations = {
  pt: {
    recent: 'Recentes:',
    clearHistory: 'Limpar',
    analyze: 'Analisar',
    timelineTitle: 'Attack Surface Timeline',
    timeline: 'Timeline',
    graph: 'Grafo',
    graphTitle: 'Attack Surface Evolution Graph',
    filterByYear: 'Filtrar por ano:',
    allYears: 'Todos',
    graphHint: 'Use o scroll para zoom • Arraste para mover • Arraste os nós para reposicionar',
    exportJson: 'Exportar JSON',
    exportPdf: 'Exportar PDF',
    emptyText: 'Digite um domínio para descobrir subdomínios históricos, certificados TLS e endpoints antigos.',
    emptyHint: 'Ex: github.com, google.com, microsoft.com',
    dataSources: 'Dados: crt.sh · Wayback Machine · DNS · GitHub',
  },
  en: {
    recent: 'Recent:',
    clearHistory: 'Clear',
    analyze: 'Analyze',
    timelineTitle: 'Attack Surface Timeline',
    timeline: 'Timeline',
    graph: 'Graph',
    graphTitle: 'Attack Surface Evolution Graph',
    filterByYear: 'Filter by year:',
    allYears: 'All',
    graphHint: 'Use scroll to zoom • Drag to pan • Drag nodes to reposition',
    exportJson: 'Export JSON',
    exportPdf: 'Export PDF',
    emptyText: 'Enter a domain to discover historical subdomains, TLS certificates and old endpoints.',
    emptyHint: 'E.g: github.com, google.com, microsoft.com',
    dataSources: 'Data: crt.sh · Wayback Machine · DNS · GitHub',
  },
  es: {
    recent: 'Recientes:',
    clearHistory: 'Limpiar',
    analyze: 'Analizar',
    timelineTitle: 'Attack Surface Timeline',
    timeline: 'Timeline',
    graph: 'Grafo',
    graphTitle: 'Attack Surface Evolution Graph',
    filterByYear: 'Filtrar por año:',
    allYears: 'Todos',
    graphHint: 'Usa el scroll para zoom • Arrastra para mover • Arrastra los nodos para reposicionar',
    exportJson: 'Exportar JSON',
    exportPdf: 'Exportar PDF',
    emptyText: 'Ingresa un dominio para descubrir subdominios históricos, certificados TLS y endpoints antiguos.',
    emptyHint: 'Ej: github.com, google.com, microsoft.com',
    dataSources: 'Datos: crt.sh · Wayback Machine · DNS · GitHub',
  },
};

function getLang() {
  return localStorage.getItem(LANG_KEY) || 'pt';
}

function setLang(lang) {
  localStorage.setItem(LANG_KEY, lang);
  const langMap = { pt: 'pt-BR', en: 'en', es: 'es' };
  document.documentElement.lang = langMap[lang] || 'pt-BR';
}

function t(key) {
  const lang = getLang();
  return translations[lang]?.[key] ?? translations.pt[key] ?? key;
}

window.getLang = getLang;
window.setLang = setLang;
window.t = t;
window.applyTranslations = applyTranslations;

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    const text = t(key);
    if (text) el.textContent = text;
  });
  const exportJson = document.getElementById('exportJsonBtn');
  const exportPdf = document.getElementById('exportPdfBtn');
  if (exportJson) exportJson.textContent = t('exportJson');
  if (exportPdf) exportPdf.textContent = t('exportPdf');
  const emptyP = document.querySelector('.empty-state > p:first-of-type');
  const emptyHint = document.querySelector('.empty-state .hint');
  if (emptyP) emptyP.textContent = t('emptyText');
  if (emptyHint) emptyHint.textContent = t('emptyHint');
  const footer = document.querySelector('.footer p');
  if (footer) footer.textContent = t('dataSources');
  const domainInput = document.getElementById('domainInput');
  const placeholders = { pt: 'exemplo.com', en: 'example.com', es: 'ejemplo.com' };
  if (domainInput) domainInput.placeholder = placeholders[getLang()] || 'example.com';
}
