const API_BASE = '';
const HISTORY_KEY = 'osint_history';
const HISTORY_MAX = 10;

const form = document.getElementById('searchForm');
const domainInput = document.getElementById('domainInput');
const submitBtn = document.getElementById('submitBtn');
const results = document.getElementById('results');
const emptyState = document.getElementById('emptyState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const domainLabel = document.getElementById('domainLabel');
const timeline = document.getElementById('timeline');
const timelineView = document.getElementById('timelineView');
const graphView = document.getElementById('graphView');
const graphContainer = document.getElementById('graphContainer');
const exposuresSection = document.getElementById('exposuresSection');
const exposuresList = document.getElementById('exposuresList');
const historySection = document.getElementById('historySection');
const historyChips = document.getElementById('historyChips');

let currentData = null;

function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(domain) {
  let hist = loadHistory();
  hist = [domain, ...hist.filter((d) => d !== domain)].slice(0, HISTORY_MAX);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(hist));
  renderHistory();
}

function renderHistory() {
  const hist = loadHistory();
  if (hist.length === 0) {
    historySection.hidden = true;
    return;
  }
  historySection.hidden = false;
  historyChips.innerHTML = hist
    .map(
      (d) =>
        `<button type="button" class="history-chip" data-domain="${escapeHtml(d)}">${escapeHtml(d)}</button>`
    )
    .join('');
  historyChips.querySelectorAll('.history-chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      domainInput.value = btn.dataset.domain;
      form.requestSubmit();
    });
  });
}

renderHistory();

document.getElementById('clearHistoryBtn').addEventListener('click', () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
});

const THEME_KEY = 'osint_theme';
const themeToggle = document.getElementById('themeToggle');
const themeIcon = themeToggle.querySelector('.theme-icon');

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || 'dark';
  document.documentElement.setAttribute('data-theme', saved === 'light' ? 'light' : 'dark');
  themeIcon.textContent = saved === 'light' ? '☀️' : '🌙';
}

themeToggle.addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  themeIcon.textContent = next === 'light' ? '☀️' : '🌙';
  localStorage.setItem(THEME_KEY, next);
});

initTheme();

const langSelect = document.getElementById('langSelect');
langSelect.value = getLang();
langSelect.addEventListener('change', () => {
  setLang(langSelect.value);
  applyTranslations();
});

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const domain = domainInput.value.trim().toLowerCase();
  if (!domain) return;

  setLoading(true);
  hideError();
  hideResults();

  try {
    const res = await fetch(`${API_BASE}/recon/timeline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.message || 'Erro ao processar');
    }

    renderResults(data);
    saveHistory(domain);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
});

document.querySelectorAll('.tab-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    const view = btn.dataset.view;
    timelineView.hidden = view !== 'timeline';
    graphView.hidden = view !== 'graph';
    if (view === 'graph' && currentData) {
      renderGraph(currentData);
    }
  });
});

function setLoading(loading) {
  submitBtn.disabled = loading;
  submitBtn.classList.toggle('loading', loading);
}

function hideError() {
  errorState.hidden = true;
}

function showError(message) {
  errorMessage.textContent = message;
  errorState.hidden = false;
  emptyState.hidden = true;
}

function hideResults() {
  results.hidden = true;
  emptyState.hidden = false;
}

function renderResults(data) {
  emptyState.hidden = true;
  errorState.hidden = true;
  currentData = data;

  domainLabel.textContent = data.domain;

  timeline.innerHTML = '';
  const years = Object.keys(data.timeline).sort((a, b) => {
    if (a === 'unknown') return 1;
    if (b === 'unknown') return -1;
    return Number(a) - Number(b);
  });

  years.forEach((year) => {
    const assets = data.timeline[year];
    const yearEl = document.createElement('div');
    yearEl.className = 'timeline-year';
    yearEl.innerHTML = `
      <div class="year-header">${year}</div>
      <ul class="year-assets">
        ${assets.map((a) => `<li>${escapeHtml(a)}</li>`).join('')}
      </ul>
    `;
    timeline.appendChild(yearEl);
  });

  if (data.exposures && data.exposures.length > 0) {
    exposuresSection.hidden = false;
    exposuresList.innerHTML = data.exposures
      .map((e) => `<li>${escapeHtml(e)}</li>`)
      .join('');
  } else {
    exposuresSection.hidden = true;
  }

  results.hidden = false;

  document.querySelector('.tab-btn[data-view="timeline"]').classList.add('active');
  document.querySelector('.tab-btn[data-view="graph"]').classList.remove('active');
  timelineView.hidden = false;
  graphView.hidden = true;
}

const LABEL_MAX_LEN = 35;

function truncateLabel(str) {
  if (str.length <= LABEL_MAX_LEN) return str;
  return str.slice(0, LABEL_MAX_LEN - 3) + '...';
}

function buildGraphData(data, yearFilter = null) {
  const domain = data.domain;
  const nodes = [{ id: domain, name: domain, isRoot: true, year: null }];
  const links = [];
  const seen = new Set([domain]);

  Object.entries(data.timeline).forEach(([year, assets]) => {
    if (yearFilter && year !== yearFilter) return;
    assets.forEach((asset) => {
      if (!seen.has(asset)) {
        seen.add(asset);
        nodes.push({ id: asset, name: asset, year, isRoot: false });
        links.push({ source: domain, target: asset });
      }
    });
  });

  return { nodes, links };
}

function renderGraph(data) {
  graphContainer.innerHTML = '';
  const yearFilter = document.getElementById('graphYearFilter').value || null;
  const { nodes, links } = buildGraphData(data, yearFilter);

  const yearSelect = document.getElementById('graphYearFilter');
  yearSelect.innerHTML = '<option value="">' + (typeof t !== 'undefined' ? t('allYears') : 'Todos') + '</option>';
  const years = Object.keys(data.timeline).filter((y) => y !== 'unknown').sort((a, b) => Number(a) - Number(b));
  years.forEach((y) => {
    const opt = document.createElement('option');
    opt.value = y;
    opt.textContent = y;
    if (y === yearFilter) opt.selected = true;
    yearSelect.appendChild(opt);
  });
  yearSelect.onchange = () => renderGraph(data);

  const width = graphContainer.clientWidth;
  const height = graphContainer.clientHeight;

  const simulation = d3
    .forceSimulation(nodes)
    .force(
      'link',
      d3.forceLink(links).id((d) => d.id).distance(120)
    )
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(40));

  const svg = d3
    .select(graphContainer)
    .append('svg')
    .attr('viewBox', [0, 0, width, height])
    .attr('preserveAspectRatio', 'xMidYMid meet');

  const g = svg.append('g');

  const zoom = d3.zoom()
    .scaleExtent([0.3, 4])
    .on('zoom', (event) => g.attr('transform', event.transform));

  svg.call(zoom);

  const link = g
    .append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('class', 'link')
    .attr('stroke-width', 1);

  const node = g
    .append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .attr('class', (d) => `node ${d.isRoot ? 'root' : ''}`)
    .call(
      d3
        .drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );

  node.append('circle').attr('r', (d) => (d.isRoot ? 10 : 5));

  const textEl = node
    .append('text')
    .attr('dx', 14)
    .attr('dy', 5)
    .attr('title', (d) => d.name)
    .text((d) => truncateLabel(d.name));
  textEl.clone(true).lower().attr('stroke', 'var(--bg-dark)').attr('stroke-width', 3);

  simulation.on('tick', () => {
    link
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y);

    node.attr('transform', (d) => `translate(${d.x},${d.y})`);
  });
}

document.getElementById('exportJsonBtn').addEventListener('click', () => {
  if (!currentData) return;
  const blob = new Blob([JSON.stringify(currentData, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `osint-${currentData.domain}-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
});

document.getElementById('exportPdfBtn').addEventListener('click', () => {
  if (!currentData) return;
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  const domain = currentData.domain;

  doc.setFontSize(18);
  doc.text(`OSINT Time Machine - ${domain}`, 20, 20);
  doc.setFontSize(12);
  doc.text(`Gerado em ${new Date().toLocaleString('pt-BR')}`, 20, 28);

  let y = 40;
  doc.setFontSize(14);
  doc.text('Attack Surface Timeline', 20, y);
  y += 10;

  const years = Object.keys(currentData.timeline).sort((a, b) => {
    if (a === 'unknown') return 1;
    if (b === 'unknown') return -1;
    return Number(a) - Number(b);
  });

  years.forEach((year) => {
    if (y > 270) {
      doc.addPage();
      y = 20;
    }
    doc.setFontSize(11);
    doc.setTextColor(50, 150, 50);
    doc.text(year, 20, y);
    doc.setTextColor(0, 0, 0);
    y += 6;

    currentData.timeline[year].forEach((asset) => {
      if (y > 275) {
        doc.addPage();
        y = 20;
      }
      doc.setFontSize(9);
      doc.text(`  • ${asset}`, 25, y);
      y += 5;
    });
    y += 4;
  });

  if (currentData.exposures?.length > 0) {
    y += 10;
    if (y > 250) {
      doc.addPage();
      y = 20;
    }
    doc.setFontSize(14);
    doc.text('Exposições Detectadas', 20, y);
    y += 8;
    currentData.exposures.forEach((e) => {
      if (y > 275) {
        doc.addPage();
        y = 20;
      }
      doc.setFontSize(9);
      doc.text(`⚠ ${e}`, 20, y);
      y += 6;
    });
  }

  doc.save(`osint-${domain}-${Date.now()}.pdf`);
});

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
