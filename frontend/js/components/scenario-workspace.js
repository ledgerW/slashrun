import { api } from '../api.js';
import { simulationSocket } from '../websocket.js';
import { StateInspector } from './state-inspector.js';
import {
    createElement,
    clearChildren,
    formatNumber,
    formatPercent,
    downloadJSON,
    toggleHidden
} from '../utils/dom.js';

class ScenarioWorkspace {
    constructor() {
        this.workspace = document.getElementById('scenario-workspace');
        this.title = document.getElementById('workspace-title');
        this.description = document.getElementById('workspace-description');
        this.timelineTrack = document.getElementById('timeline-track');
        this.timelineStatus = document.getElementById('timeline-status');
        this.timelineTemplate = document.getElementById('timeline-card-template');
        this.auditTemplate = document.getElementById('audit-row-template');
        this.auditLog = document.getElementById('audit-log');
        this.auditSummary = document.getElementById('audit-summary');
        this.stateInspector = new StateInspector(document.getElementById('state-tree'));
        this.exportButton = document.getElementById('export-state');
        this.stepButton = document.getElementById('step-simulation');
        this.playButton = document.getElementById('timeline-play');
        this.timelinePrev = document.getElementById('timeline-prev');
        this.timelineNext = document.getElementById('timeline-next');
        this.lensPanels = {
            macro: document.getElementById('lens-macro'),
            networks: document.getElementById('lens-networks'),
            policy: document.getElementById('lens-policy'),
            events: document.getElementById('lens-events')
        };
        this.currentScenario = null;
        this.history = [];
        this.currentStepIndex = 0;
        this.autoplayTimer = null;
    }

    initialize() {
        if (!this.workspace) return;

        this.exportButton?.addEventListener('click', () => {
            if (this.currentScenario && this.history.length > 0) {
                const current = this.history[this.currentStepIndex];
                downloadJSON(current.state, `${this.currentScenario.name}-t${current.timestep}.json`);
            }
        });

        this.stepButton?.addEventListener('click', async () => {
            if (!this.currentScenario) return;
            this.stepButton.disabled = true;
            try {
                const step = await api.post(`/simulation/scenarios/${this.currentScenario.id}/step`);
                await this.appendStep(step);
            } catch (error) {
                this.timelineStatus.textContent = `Step failed: ${error.message}`;
            } finally {
                this.stepButton.disabled = false;
            }
        });

        this.playButton?.addEventListener('click', () => {
            if (this.autoplayTimer) {
                clearInterval(this.autoplayTimer);
                this.autoplayTimer = null;
                this.playButton.textContent = 'Play';
            } else {
                this.playButton.textContent = 'Pause';
                this.autoplayTimer = setInterval(async () => {
                    if (!this.currentScenario) return;
                    try {
                        const step = await api.post(`/simulation/scenarios/${this.currentScenario.id}/step`);
                        await this.appendStep(step);
                    } catch (error) {
                        this.timelineStatus.textContent = `Auto-play halted: ${error.message}`;
                        clearInterval(this.autoplayTimer);
                        this.autoplayTimer = null;
                        this.playButton.textContent = 'Play';
                    }
                }, 2500);
            }
        });

        document.querySelectorAll('.lens-tab').forEach((tab) => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.lens-tab').forEach((btn) => btn.classList.remove('active'));
                tab.classList.add('active');
                const target = tab.dataset.tab;
                Object.entries(this.lensPanels).forEach(([key, panel]) => {
                    toggleHidden(panel, key !== target);
                });
            });
        });

        document.getElementById('expand-all')?.addEventListener('click', () => this.stateInspector.expandAll());
        document.getElementById('collapse-all')?.addEventListener('click', () => this.stateInspector.collapseAll());

        this.timelinePrev?.addEventListener('click', () => this.focusTimelineStep(this.currentStepIndex - 1));
        this.timelineNext?.addEventListener('click', () => this.focusTimelineStep(this.currentStepIndex + 1));
    }

    async loadScenario(scenario) {
        this.currentScenario = scenario;
        this.title.textContent = scenario.name;
        this.description.textContent = scenario.description || 'No description provided.';
        this.timelineStatus.textContent = 'Loading timeline…';
        this.timelineTrack?.focus();
        if (this.autoplayTimer) {
            clearInterval(this.autoplayTimer);
            this.autoplayTimer = null;
            if (this.playButton) {
                this.playButton.textContent = 'Play';
            }
        }

        try {
            const [detail, history] = await Promise.all([
                api.get(`/simulation/scenarios/${scenario.id}`),
                api.get(`/simulation/scenarios/${scenario.id}/history`)
            ]);
            this.history = history.sort((a, b) => a.timestep - b.timestep);
            if (this.history.length === 0 && detail.current_state) {
                this.history.push({
                    id: (globalThis.crypto && globalThis.crypto.randomUUID)
                        ? globalThis.crypto.randomUUID()
                        : `state-${Date.now()}`,
                    scenario_id: scenario.id,
                    timestep: detail.current_timestep,
                    state: detail.current_state,
                    audit: detail.current_state ? {
                        reducer_sequence: [],
                        triggers_fired: [],
                        errors: [],
                        timestep: detail.current_timestep
                    } : null,
                    created_at: detail.updated_at
                });
            }
            this.renderTimeline();
            this.focusTimelineStep(this.history.length - 1);
            this.timelineStatus.textContent = `Loaded ${this.history.length} steps.`;
            document.dispatchEvent(new CustomEvent('scenario:selected', { detail: { scenario: detail } }));
            simulationSocket.connect(scenario.id);
            simulationSocket.on('simulation_step_complete', async (payload) => {
                if (String(payload.scenario_id) !== String(scenario.id)) return;
                const latest = await api.get(`/simulation/scenarios/${scenario.id}/states/${payload.timestep}`);
                await this.appendStep(latest, false);
            });
        } catch (error) {
            this.timelineStatus.textContent = `Failed to load scenario: ${error.message}`;
        }
    }

    async appendStep(step, focus = true) {
        const exists = this.history.some((item) => item.timestep === step.timestep);
        if (!exists) {
            this.history.push(step);
            this.history.sort((a, b) => a.timestep - b.timestep);
            this.renderTimeline();
        } else {
            const index = this.history.findIndex((item) => item.timestep === step.timestep);
            this.history[index] = step;
        }
        if (focus) {
            this.focusTimelineStep(this.history.length - 1);
        } else {
            this.focusTimelineStep(this.history.findIndex((item) => item.timestep === step.timestep));
        }
    }

    renderTimeline() {
        if (!this.timelineTrack) return;
        clearChildren(this.timelineTrack);
        this.history.forEach((step, index) => {
            const node = this.timelineTemplate.content.firstElementChild.cloneNode(true);
            node.dataset.index = String(index);
            node.addEventListener('click', () => this.focusTimelineStep(index));
            node.querySelector('.timestep-label').textContent = `Timestep ${step.timestep}`;
            node.querySelector('.timestep-time').textContent = new Date(step.created_at).toLocaleString();
            const prev = this.history[index - 1];
            const currentGDP = this.computeAggregate(step.state, 'gdp');
            const previousGDP = prev ? this.computeAggregate(prev.state, 'gdp') : currentGDP;
            const currentInflation = this.computeAggregate(step.state, 'inflation');
            const previousInflation = prev ? this.computeAggregate(prev.state, 'inflation') : currentInflation;
            node.querySelector('.metric-gdp').textContent = this.diffText(currentGDP, previousGDP);
            node.querySelector('.metric-inflation').textContent = this.diffText(currentInflation, previousInflation, true);
            node.querySelector('.metric-triggers').textContent = String(step.audit?.triggers_fired?.length || 0);
            this.timelineTrack.appendChild(node);
        });
    }

    computeAggregate(state, field) {
        const values = Object.values(state.countries || {}).map((country) => country.macro?.[field]);
        const filtered = values.filter((value) => typeof value === 'number');
        if (filtered.length === 0) return 0;
        return filtered.reduce((sum, value) => sum + value, 0) / filtered.length;
    }

    diffText(current, previous, isPercent = false) {
        const diff = current - previous;
        const formatted = isPercent ? `${diff >= 0 ? '+' : ''}${(diff * 100).toFixed(2)}pp` : `${diff >= 0 ? '+' : ''}${diff.toFixed(2)}`;
        return formatted;
    }

    focusTimelineStep(index) {
        if (index < 0 || index >= this.history.length) return;
        this.currentStepIndex = index;
        const step = this.history[index];
        this.timelineStatus.textContent = `Focused on timestep ${step.timestep}`;
        if (this.timelineTrack) {
            this.timelineTrack.querySelectorAll('.timeline-card').forEach((card) => card.classList.remove('active'));
            const activeCard = this.timelineTrack.querySelector(`[data-index="${index}"]`);
            if (activeCard) {
                activeCard.classList.add('active');
                activeCard.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
            }
        }
        this.stateInspector.render(step.state);
        this.renderMacroDashboard(step);
        this.renderNetworks(step.state);
        this.renderPolicy(step.state);
        this.renderEvents(step.state);
        this.renderAudit(step.audit);
        document.dispatchEvent(new CustomEvent('scenario:step', {
            detail: {
                step,
                scenario: this.currentScenario
            }
        }));
    }

    renderMacroDashboard(step) {
        const container = this.lensPanels.macro;
        if (!container) return;
        clearChildren(container);
        const grid = createElement('div', { classList: 'macro-grid' });
        const countries = Object.entries(step.state.countries || {});
        countries.forEach(([code, country]) => {
            const card = createElement('article', { classList: 'country-card' });
            const header = createElement('header');
            header.appendChild(createElement('h3', { text: `${country.name || code}` }));
            header.appendChild(createElement('span', { classList: 'small', text: `GDP: ${formatNumber(country.macro?.gdp, { maximumFractionDigits: 1 })}` }));
            card.appendChild(header);

            const kpis = createElement('div', { classList: 'country-kpis' });
            kpis.appendChild(this.kpiRow('Inflation', formatPercent(country.macro?.inflation ?? 0)));
            kpis.appendChild(this.kpiRow('Unemployment', formatPercent(country.macro?.unemployment ?? 0)));
            kpis.appendChild(this.kpiRow('Debt/GDP', formatPercent(country.macro?.debt_gdp ?? 0)));
            card.appendChild(kpis);

            const sparkline = this.buildSparkline(code, 'inflation');
            if (sparkline) {
                card.appendChild(sparkline);
            }
            grid.appendChild(card);
        });
        container.appendChild(grid);
    }

    kpiRow(label, value) {
        const row = createElement('div', { classList: 'kpi-row' });
        row.appendChild(createElement('span', { text: label }));
        row.appendChild(createElement('span', { text: value }));
        return row;
    }

    buildSparkline(countryCode, field) {
        const historyValues = this.history.map((step) => step.state.countries?.[countryCode]?.macro?.[field]).filter((value) => typeof value === 'number');
        if (historyValues.length < 2) return null;
        const min = Math.min(...historyValues);
        const max = Math.max(...historyValues);
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', '0 0 100 40');
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const points = historyValues.map((value, index) => {
            const x = (index / (historyValues.length - 1)) * 100;
            const range = max - min || 1;
            const y = 40 - ((value - min) / range) * 40;
            return `${x},${y}`;
        }).join(' ');
        path.setAttribute('d', `M ${points}`);
        path.setAttribute('fill', 'none');
        const gradientId = `spark-${countryCode}-${field}-${Math.floor(Math.random() * 10000)}`;
        path.setAttribute('stroke', `url(#${gradientId})`);
        path.setAttribute('stroke-width', '2');
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.setAttribute('id', gradientId);
        gradient.setAttribute('x1', '0%');
        gradient.setAttribute('x2', '100%');
        gradient.innerHTML = '<stop offset="0%" stop-color="rgba(59,156,255,0.8)" /><stop offset="100%" stop-color="rgba(109,214,255,0.9)" />';
        defs.appendChild(gradient);
        svg.appendChild(defs);
        svg.appendChild(path);
        const wrapper = createElement('div', { classList: 'sparkline' });
        wrapper.appendChild(svg);
        return wrapper;
    }

    renderNetworks(state) {
        const container = this.lensPanels.networks;
        if (!container) return;
        clearChildren(container);
        const matrices = [
            { key: 'trade_matrix', label: 'Trade Flows' },
            { key: 'interbank_matrix', label: 'Interbank Exposures' },
            { key: 'alliance_graph', label: 'Alliances' },
            { key: 'sanctions', label: 'Sanctions' }
        ];
        matrices.forEach(({ key, label }) => {
            const matrix = state[key] || {};
            const title = createElement('h3', { text: label });
            const canvas = createElement('div', { classList: 'network-canvas' });
            this.drawNetwork(matrix, canvas);
            container.appendChild(title);
            container.appendChild(canvas);
        });
    }

    drawNetwork(matrix, canvas) {
        const entries = Object.entries(matrix);
        const nodes = new Set();
        entries.forEach(([from, targets]) => {
            nodes.add(from);
            Object.keys(targets).forEach((to) => nodes.add(to));
        });
        const nodeList = Array.from(nodes);
        const radius = Math.min(canvas.clientWidth, 360) / 2 - 30;
        const centerX = canvas.clientWidth / 2;
        const centerY = canvas.clientHeight / 2;
        const tooltip = createElement('div', { classList: 'network-tooltip hidden' });
        canvas.appendChild(tooltip);
        nodeList.forEach((node, index) => {
            const angle = (index / nodeList.length) * Math.PI * 2;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            const element = createElement('div', { classList: 'network-node', dataset: { node } });
            element.style.left = `${x - 9}px`;
            element.style.top = `${y - 9}px`;
            element.addEventListener('mouseenter', () => {
                tooltip.textContent = node;
                tooltip.style.left = `${x + 12}px`;
                tooltip.style.top = `${y - 12}px`;
                tooltip.classList.remove('hidden');
            });
            element.addEventListener('mouseleave', () => tooltip.classList.add('hidden'));
            canvas.appendChild(element);
        });
        entries.forEach(([from, targets]) => {
            const fromIndex = nodeList.indexOf(from);
            Object.entries(targets).forEach(([to, weight]) => {
                const toIndex = nodeList.indexOf(to);
                if (fromIndex === -1 || toIndex === -1 || !weight) return;
                const fromNode = canvas.querySelector(`.network-node[data-node="${from}"]`);
                const toNode = canvas.querySelector(`.network-node[data-node="${to}"]`);
                if (!fromNode || !toNode) return;
                const x1 = fromNode.offsetLeft + 9;
                const y1 = fromNode.offsetTop + 9;
                const x2 = toNode.offsetLeft + 9;
                const y2 = toNode.offsetTop + 9;
                const length = Math.hypot(x2 - x1, y2 - y1);
                const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);
                const edge = createElement('div', { classList: 'network-edge' });
                edge.style.width = `${length}px`;
                edge.style.left = `${x1}px`;
                edge.style.top = `${y1}px`;
                edge.style.transform = `rotate(${angle}deg)`;
                edge.style.opacity = String(Math.min(1, Math.abs(weight)));
                canvas.appendChild(edge);
            });
        });
    }

    renderPolicy(state) {
        const container = this.lensPanels.policy;
        if (!container) return;
        clearChildren(container);
        const table = createElement('table', { classList: 'policy-table' });
        const thead = document.createElement('thead');
        const headRow = document.createElement('tr');
        ['Regime', 'Parameter', 'Value'].forEach((label) => {
            const th = document.createElement('th');
            th.textContent = label;
            headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);
        const tbody = document.createElement('tbody');
        Object.entries(state.rules?.regimes || {}).forEach(([regime, params]) => {
            Object.entries(params).forEach(([key, value]) => {
                const row = document.createElement('tr');
                row.appendChild(createElement('td', { text: regime }));
                row.appendChild(createElement('td', { text: key }));
                row.appendChild(createElement('td', { text: typeof value === 'number' ? value.toString() : JSON.stringify(value) }));
                tbody.appendChild(row);
            });
        });
        table.appendChild(tbody);
        container.appendChild(table);
    }

    renderEvents(state) {
        const container = this.lensPanels.events;
        if (!container) return;
        clearChildren(container);
        const columns = createElement('div', { classList: 'event-columns' });
        const pendingColumn = createElement('div', { classList: 'event-column' });
        pendingColumn.appendChild(createElement('h3', { text: 'Pending Events' }));
        const processedColumn = createElement('div', { classList: 'event-column' });
        processedColumn.appendChild(createElement('h3', { text: 'Processed Events' }));
        (state.events?.pending || []).forEach((event) => {
            pendingColumn.appendChild(this.eventCard(event));
        });
        (state.events?.processed || []).forEach((event) => {
            processedColumn.appendChild(this.eventCard(event));
        });
        columns.appendChild(pendingColumn);
        columns.appendChild(processedColumn);
        container.appendChild(columns);
    }

    eventCard(event) {
        const card = createElement('article', { classList: 'event-card' });
        card.appendChild(createElement('h4', { text: event.kind || 'event' }));
        card.appendChild(createElement('pre', { text: JSON.stringify(event.payload || {}, null, 2) }));
        return card;
    }

    renderAudit(audit) {
        if (!this.auditLog) return;
        clearChildren(this.auditLog);
        if (!audit) {
            this.auditSummary.textContent = 'No audit data available for this timestep.';
            return;
        }
        this.auditSummary.textContent = `${audit.reducer_sequence?.length || 0} reducers • ${audit.field_changes?.length || 0} field changes • ${audit.triggers_fired?.length || 0} triggers`;
        const changes = audit.field_changes || [];
        if (changes.length === 0 && audit.errors?.length === 0) {
            const placeholder = createElement('p', { classList: 'small', text: 'No field changes recorded. This may be the initial state.' });
            this.auditLog.appendChild(placeholder);
            return;
        }
        changes.forEach((change) => {
            const node = this.auditTemplate.content.firstElementChild.cloneNode(true);
            node.querySelector('.audit-field').textContent = change.field_path;
            node.querySelector('.audit-reducer').textContent = change.reducer_name;
            const valueElement = node.querySelector('.audit-value');
            const detail = change.new_value !== undefined ? JSON.stringify(change.new_value) : '∅';
            valueElement.textContent = detail;
            node.addEventListener('click', () => this.focusField(change.field_path));
            this.auditLog.appendChild(node);
        });
        if (audit.errors && audit.errors.length) {
            const errorBlock = createElement('div', { classList: 'audit-row' });
            errorBlock.appendChild(createElement('div', { text: 'Errors' }));
            errorBlock.appendChild(createElement('div', { text: '' }));
            errorBlock.appendChild(createElement('div', { text: audit.errors.join('; ') }));
            this.auditLog.appendChild(errorBlock);
        }
    }

    focusField(fieldPath) {
        if (!this.stateInspector.container) return;
        const segments = fieldPath.split('.');
        let current = this.stateInspector.container;
        segments.forEach((segment) => {
            const details = Array.from(current.querySelectorAll(':scope > details')).find((item) => item.firstElementChild?.textContent === segment);
            if (details) {
                details.open = true;
                current = details;
            }
        });
        current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

export const scenarioWorkspace = new ScenarioWorkspace();
scenarioWorkspace.initialize();
