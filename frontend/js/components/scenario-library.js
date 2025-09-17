import { api } from '../api.js';
import { scenarioWorkspace } from './scenario-workspace.js';
import { createElement, clearChildren } from '../utils/dom.js';
import { getTriggerDrafts } from '../utils/storage.js';
import { validateNonEmpty } from '../utils/validation.js';

class ScenarioLibrary {
    constructor() {
        this.grid = document.getElementById('scenario-grid');
        this.metrics = document.getElementById('scenario-metrics');
        this.searchInput = document.getElementById('scenario-search');
        this.createButton = document.getElementById('create-scenario-btn');
        this.modal = document.getElementById('scenario-modal');
        this.modalForm = document.getElementById('scenario-form');
        this.modalClose = this.modal?.querySelector('.modal-close');
        this.modalCancel = document.getElementById('scenario-cancel');
        this.templateSelect = document.getElementById('scenario-template');
        this.triggerList = document.getElementById('trigger-draft-list');
        this.scenarioName = document.getElementById('scenario-name');
        this.scenarioDescription = document.getElementById('scenario-description');
        this.scenarios = [];
        this.filteredScenarios = [];
    }

    initialize() {
        if (!this.grid) return;
        this.fetchScenarios();
        this.searchInput?.addEventListener('input', () => this.applyFilter());
        this.createButton?.addEventListener('click', () => this.openModal());
        this.modalClose?.addEventListener('click', () => this.closeModal());
        this.modalCancel?.addEventListener('click', (event) => {
            event.preventDefault();
            this.closeModal();
        });
        this.modal?.addEventListener('close', () => this.modalForm?.reset());
        this.modalForm?.addEventListener('submit', (event) => this.handleCreate(event));
    }

    async fetchScenarios() {
        try {
            const scenarios = await api.get('/simulation/scenarios');
            this.scenarios = scenarios;
            this.filteredScenarios = scenarios;
            this.render();
        } catch (error) {
            this.grid.textContent = `Failed to load scenarios: ${error.message}`;
        }
    }

    render() {
        if (!this.grid) return;
        clearChildren(this.grid);
        this.filteredScenarios.forEach((scenario) => {
            const card = createElement('article', { classList: 'scenario-card' });
            card.appendChild(createElement('h3', { text: scenario.name }));
            card.appendChild(createElement('p', { classList: 'small', text: scenario.description || 'No description provided.' }));
            const meta = createElement('div', { classList: 'scenario-meta' });
            meta.appendChild(createElement('span', { text: `Timesteps: ${scenario.current_timestep}` }));
            meta.appendChild(createElement('span', { text: `Triggers: ${scenario.triggers_count}` }));
            card.appendChild(meta);
            const sparkline = createElement('div', { classList: 'scenario-sparkline' });
            const path = createElement('canvas', { classList: 'sparkline-path' });
            this.drawSparkline(path, scenario.current_state);
            sparkline.appendChild(path);
            card.appendChild(sparkline);
            card.addEventListener('click', () => scenarioWorkspace.loadScenario(scenario));
            this.grid.appendChild(card);
        });
        this.renderMetrics();
    }

    renderMetrics() {
        if (!this.metrics) return;
        clearChildren(this.metrics);
        const total = createElement('div', { classList: 'metric-card' });
        total.appendChild(createElement('h3', { text: 'Total Scenarios' }));
        total.appendChild(createElement('span', { text: String(this.scenarios.length) }));
        const triggers = createElement('div', { classList: 'metric-card' });
        triggers.appendChild(createElement('h3', { text: 'Total Triggers' }));
        const triggerCount = this.scenarios.reduce((sum, scenario) => sum + (scenario.triggers_count || 0), 0);
        triggers.appendChild(createElement('span', { text: String(triggerCount) }));
        const updated = createElement('div', { classList: 'metric-card' });
        updated.appendChild(createElement('h3', { text: 'Last Updated' }));
        const latest = this.scenarios[0];
        updated.appendChild(createElement('span', { text: latest ? new Date(latest.updated_at).toLocaleString() : '—' }));
        this.metrics.appendChild(total);
        this.metrics.appendChild(triggers);
        this.metrics.appendChild(updated);
    }

    drawSparkline(canvas, state) {
        if (!canvas || !canvas.getContext) return;
        const context = canvas.getContext('2d');
        canvas.width = canvas.clientWidth || 220;
        canvas.height = canvas.clientHeight || 48;
        context.clearRect(0, 0, canvas.width, canvas.height);
        if (!state || !state.countries) return;
        const values = Object.values(state.countries).map((country) => country.macro?.gdp).filter((value) => typeof value === 'number');
        if (values.length === 0) return;
        const min = Math.min(...values);
        const max = Math.max(...values);
        context.strokeStyle = 'rgba(59,156,255,0.9)';
        context.lineWidth = 2;
        context.beginPath();
        values.forEach((value, index) => {
            const x = (index / (values.length - 1 || 1)) * canvas.width;
            const range = max - min || 1;
            const y = canvas.height - ((value - min) / range) * canvas.height;
            if (index === 0) {
                context.moveTo(x, y);
            } else {
                context.lineTo(x, y);
            }
        });
        context.stroke();
    }

    applyFilter() {
        const query = this.searchInput?.value.toLowerCase() || '';
        if (!query) {
            this.filteredScenarios = this.scenarios;
        } else {
            this.filteredScenarios = this.scenarios.filter((scenario) => {
                return scenario.name.toLowerCase().includes(query) || (scenario.description || '').toLowerCase().includes(query);
            });
        }
        this.render();
    }

    openModal() {
        if (!this.modal) return;
        this.populateTriggerDrafts();
        this.modal.showModal();
    }

    closeModal() {
        this.modal?.close();
    }

    populateTriggerDrafts() {
        if (!this.triggerList) return;
        clearChildren(this.triggerList);
        const drafts = getTriggerDrafts();
        if (drafts.length === 0) {
            this.triggerList.appendChild(createElement('p', { classList: 'small', text: 'No local drafts stored.' }));
            return;
        }
        drafts.forEach((draft) => {
            const card = createElement('article', { classList: 'draft-card' });
            card.appendChild(createElement('h4', { text: draft.name }));
            card.appendChild(createElement('p', { classList: 'small', text: draft.description || '' }));
            card.appendChild(createElement('pre', { text: draft.condition?.when || 'No condition set' }));
            this.triggerList.appendChild(card);
        });
    }

    async handleCreate(event) {
        event.preventDefault();
        if (!validateNonEmpty(this.scenarioName?.value)) {
            this.scenarioName?.focus();
            return;
        }
        const templateType = this.templateSelect?.value || 'mvs';
        try {
            const templateEndpoint = templateType === 'fis' ? '/simulation/templates/fis' : '/simulation/templates/mvs';
            const template = await api.post(templateEndpoint, {});
            const initialState = template.state;
            const payload = {
                name: this.scenarioName.value.trim(),
                description: this.scenarioDescription.value.trim(),
                initial_state: initialState,
                triggers: getTriggerDrafts()
            };
            await api.post('/simulation/scenarios', payload);
            this.closeModal();
            await this.fetchScenarios();
        } catch (error) {
            alert(`Failed to create scenario: ${error.message}`);
        }
    }
}

export const scenarioLibrary = new ScenarioLibrary();
scenarioLibrary.initialize();
