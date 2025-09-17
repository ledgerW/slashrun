import { api } from '../api.js';
import { createElement, clearChildren } from '../utils/dom.js';
import { getTriggerDrafts, saveTriggerDraft, deleteTriggerDraft } from '../utils/storage.js';
import { validateNonEmpty, validateDSL } from '../utils/validation.js';

class TriggerDesigner {
    constructor() {
        this.form = document.getElementById('trigger-form');
        this.actionsContainer = document.getElementById('trigger-actions');
        this.evalOutput = document.getElementById('trigger-eval-output');
        this.loadExamplesButton = document.getElementById('load-trigger-examples');
        this.saveDraftButton = document.getElementById('save-trigger-draft');
        this.actionModal = document.getElementById('action-modal');
        this.actionModalBody = document.getElementById('action-modal-body');
        this.actionModalTitle = document.getElementById('action-modal-title');
        this.actionForm = document.getElementById('action-form');
        this.actionCancel = document.getElementById('action-cancel');
        this.actionClose = this.actionModal?.querySelector('.modal-close');
        this.currentActions = {
            patches: [],
            overrides: [],
            network_rewrites: [],
            events: []
        };
        this.pendingActionType = null;
        this.currentScenario = null;
        this.currentStep = null;
        this.examples = {};
    }

    initialize() {
        if (!this.form) return;
        this.form.querySelectorAll('.action-controls button').forEach((button) => {
            button.addEventListener('click', () => this.openActionModal(button.dataset.action));
        });
        this.loadExamplesButton?.addEventListener('click', () => this.loadExamples());
        this.saveDraftButton?.addEventListener('click', () => this.handleSaveDraft());
        this.actionCancel?.addEventListener('click', (event) => {
            event.preventDefault();
            this.closeActionModal();
        });
        this.actionClose?.addEventListener('click', () => this.closeActionModal());
        this.actionModal?.addEventListener('close', () => {
            this.actionForm?.reset();
            this.pendingActionType = null;
        });
        this.actionForm?.addEventListener('submit', (event) => this.handleActionSubmit(event));

        document.addEventListener('scenario:selected', (event) => {
            this.currentScenario = event.detail?.scenario;
            this.updateEvaluation();
        });
        document.addEventListener('scenario:step', (event) => {
            this.currentStep = event.detail?.step;
            this.currentScenario = event.detail?.scenario || this.currentScenario;
            this.updateEvaluation();
        });

        this.renderActions();
        this.renderDraftBadges();
    }

    renderActions() {
        if (!this.actionsContainer) return;
        clearChildren(this.actionsContainer);
        const sections = [
            ['patches', 'Policy Patches'],
            ['overrides', 'Reducer Overrides'],
            ['network_rewrites', 'Network Rewrites'],
            ['events', 'Event Injections']
        ];
        sections.forEach(([key, label]) => {
            const items = this.currentActions[key];
            if (!items || items.length === 0) return;
            const group = createElement('div', { classList: 'draft-card' });
            group.appendChild(createElement('h4', { text: label }));
            items.forEach((item, index) => {
                const chip = createElement('div', { classList: 'action-chip' });
                chip.appendChild(createElement('span', { text: this.describeAction(key, item) }));
                const remove = createElement('button', { classList: 'btn btn-secondary', text: 'Remove', attributes: { type: 'button' } });
                remove.addEventListener('click', () => {
                    this.currentActions[key].splice(index, 1);
                    this.renderActions();
                });
                chip.appendChild(remove);
                group.appendChild(chip);
            });
            this.actionsContainer.appendChild(group);
        });
    }

    describeAction(type, action) {
        switch (type) {
            case 'patches':
                return `${action.path} ${action.op} ${action.value}`;
            case 'overrides':
                return `${action.target} → ${action.impl_name}`;
            case 'network_rewrites':
                return `${action.layer}: ${action.edits.map((edit) => `${edit[0]}→${edit[1]}(${edit[2]})`).join(', ')}`;
            case 'events':
                return `${action.kind} event`;
            default:
                return 'Action';
        }
    }

    openActionModal(type) {
        if (!this.actionModal || !this.actionModalBody) return;
        this.pendingActionType = type;
        clearChildren(this.actionModalBody);
        switch (type) {
            case 'patch':
                this.actionModalTitle.textContent = 'Add Policy Patch';
                this.renderPatchForm();
                break;
            case 'override':
                this.actionModalTitle.textContent = 'Add Reducer Override';
                this.renderOverrideForm();
                break;
            case 'network':
                this.actionModalTitle.textContent = 'Add Network Rewrite';
                this.renderNetworkForm();
                break;
            case 'event':
                this.actionModalTitle.textContent = 'Inject Event';
                this.renderEventForm();
                break;
            default:
                return;
        }
        this.actionModal.showModal();
    }

    closeActionModal() {
        this.actionModal?.close();
    }

    renderPatchForm() {
        const path = createElement('input', { attributes: { name: 'path', required: 'true', placeholder: 'rules.regimes.trade.tariff_multiplier' } });
        const op = document.createElement('select');
        op.name = 'op';
        ['set', 'add', 'mul'].forEach((value) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value.toUpperCase();
            op.appendChild(option);
        });
        const value = createElement('input', { attributes: { name: 'value', required: 'true', placeholder: '0.1' } });
        this.actionModalBody.appendChild(this.labeledField('Target Path', path));
        this.actionModalBody.appendChild(this.labeledField('Operation', op));
        this.actionModalBody.appendChild(this.labeledField('Value', value));
    }

    renderOverrideForm() {
        const target = createElement('input', { attributes: { name: 'target', required: 'true', placeholder: 'monetary_policy' } });
        const impl = createElement('input', { attributes: { name: 'impl_name', required: 'true', placeholder: 'taylor_rule_v1' } });
        this.actionModalBody.appendChild(this.labeledField('Reducer Target', target));
        this.actionModalBody.appendChild(this.labeledField('Implementation Name', impl));
    }

    renderNetworkForm() {
        const layer = document.createElement('select');
        layer.name = 'layer';
        ['trade', 'alliances', 'sanctions', 'interbank', 'energy'].forEach((value) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            layer.appendChild(option);
        });
        const from = createElement('input', { attributes: { name: 'from', required: 'true', placeholder: 'USA' } });
        const to = createElement('input', { attributes: { name: 'to', required: 'true', placeholder: 'CHN' } });
        const weight = createElement('input', { attributes: { name: 'weight', required: 'true', placeholder: '0.8' } });
        this.actionModalBody.appendChild(this.labeledField('Layer', layer));
        this.actionModalBody.appendChild(this.labeledField('From (ISO3)', from));
        this.actionModalBody.appendChild(this.labeledField('To (ISO3)', to));
        this.actionModalBody.appendChild(this.labeledField('Weight', weight));
    }

    renderEventForm() {
        const kind = document.createElement('select');
        kind.name = 'kind';
        ['conflict', 'disaster', 'strike', 'embargo', 'mobilization'].forEach((value) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            kind.appendChild(option);
        });
        const payload = document.createElement('textarea');
        payload.name = 'payload';
        payload.rows = 4;
        payload.placeholder = '{"country": "USA", "intensity": 0.4}';
        this.actionModalBody.appendChild(this.labeledField('Event Kind', kind));
        this.actionModalBody.appendChild(this.labeledField('Payload (JSON)', payload));
    }

    labeledField(label, input) {
        const wrapper = createElement('label');
        wrapper.textContent = label;
        wrapper.appendChild(input);
        return wrapper;
    }

    handleActionSubmit(event) {
        event.preventDefault();
        const formData = new FormData(this.actionForm);
        switch (this.pendingActionType) {
            case 'patch':
                this.currentActions.patches.push({
                    path: formData.get('path'),
                    op: formData.get('op'),
                    value: this.parseValue(formData.get('value'))
                });
                break;
            case 'override':
                this.currentActions.overrides.push({
                    target: formData.get('target'),
                    impl_name: formData.get('impl_name')
                });
                break;
            case 'network':
                this.currentActions.network_rewrites.push({
                    layer: formData.get('layer'),
                    edits: [[formData.get('from'), formData.get('to'), this.parseValue(formData.get('weight'))]]
                });
                break;
            case 'event':
                this.currentActions.events.push({
                    kind: formData.get('kind'),
                    payload: this.parseJSON(formData.get('payload'))
                });
                break;
            default:
                break;
        }
        this.renderActions();
        this.closeActionModal();
    }

    parseValue(raw) {
        if (raw === null || raw === undefined) return null;
        const value = Number(raw);
        return Number.isNaN(value) ? raw : value;
    }

    parseJSON(raw) {
        if (!raw) return {};
        try {
            return JSON.parse(raw);
        } catch {
            return { note: raw };
        }
    }

    async loadExamples() {
        try {
            this.examples = await api.get('/simulation/triggers/examples');
            this.renderExamples();
        } catch (error) {
            this.evalOutput.textContent = `Failed to load examples: ${error.message}`;
        }
    }

    renderExamples() {
        const list = document.getElementById('trigger-example-list');
        if (!list) return;
        clearChildren(list);
        Object.entries(this.examples).forEach(([key, trigger]) => {
            const button = createElement('button', { classList: 'btn btn-secondary', text: `Use ${trigger.name || key}` });
            button.addEventListener('click', () => this.applyExample(trigger));
            list.appendChild(button);
        });
    }

    applyExample(trigger) {
        if (!trigger) return;
        this.form.querySelector('#trigger-name').value = trigger.name || '';
        this.form.querySelector('#trigger-description').value = trigger.description || '';
        this.form.querySelector('#trigger-condition').value = trigger.condition?.when || '';
        const onceCheckbox = this.form.querySelector('#trigger-once');
        if (onceCheckbox) {
            onceCheckbox.checked = trigger.condition?.once ?? true;
        }
        const expiry = this.form.querySelector('#trigger-expiry');
        if (expiry) {
            expiry.value = trigger.expires_after_turns ?? '';
        }
        this.currentActions = {
            patches: trigger.action?.patches || [],
            overrides: trigger.action?.overrides || [],
            network_rewrites: trigger.action?.network_rewrites || [],
            events: trigger.action?.events || []
        };
        this.renderActions();
        this.updateEvaluation();
    }

    handleSaveDraft() {
        const name = this.form.querySelector('#trigger-name').value.trim();
        const description = this.form.querySelector('#trigger-description').value.trim();
        const condition = this.form.querySelector('#trigger-condition').value.trim();
        const once = this.form.querySelector('#trigger-once').checked;
        const expiryRaw = this.form.querySelector('#trigger-expiry').value;
        if (!validateNonEmpty(name)) {
            alert('Trigger name is required.');
            return;
        }
        if (!validateDSL(condition)) {
            alert('Condition contains unsupported characters.');
            return;
        }
        const draft = {
            name,
            description,
            condition: { when: condition, once },
            action: this.currentActions,
            expires_after_turns: expiryRaw ? Number(expiryRaw) : null
        };
        saveTriggerDraft(draft);
        this.renderDraftBadges();
        alert('Trigger draft saved locally. It will be attached when creating new scenarios.');
    }

    renderDraftBadges() {
        const drafts = getTriggerDrafts();
        const list = document.getElementById('trigger-draft-list');
        if (!list) return;
        clearChildren(list);
        drafts.forEach((draft) => {
            const card = createElement('article', { classList: 'draft-card' });
            card.appendChild(createElement('h4', { text: draft.name }));
            card.appendChild(createElement('p', { classList: 'small', text: draft.description || '' }));
            const remove = createElement('button', { classList: 'btn btn-secondary', text: 'Delete Draft', attributes: { type: 'button' } });
            remove.addEventListener('click', () => {
                deleteTriggerDraft(draft.name);
                this.renderDraftBadges();
            });
            card.appendChild(remove);
            list.appendChild(card);
        });
        if (drafts.length === 0) {
            list.appendChild(createElement('p', { classList: 'small', text: 'No local drafts stored.' }));
        }
    }

    updateEvaluation() {
        if (!this.evalOutput) return;
        const condition = this.form.querySelector('#trigger-condition')?.value.trim();
        if (!condition) {
            this.evalOutput.textContent = 'Enter a condition to evaluate.';
            return;
        }
        if (!this.currentStep || !this.currentStep.state) {
            this.evalOutput.textContent = 'Select a scenario and timestep to evaluate the condition.';
            return;
        }
        if (!validateDSL(condition)) {
            this.evalOutput.textContent = 'Condition contains unsupported characters.';
            return;
        }
        try {
            const result = this.evaluateCondition(condition, this.currentStep);
            this.evalOutput.textContent = result ? 'Condition is TRUE for current timestep.' : 'Condition is FALSE for current timestep.';
        } catch (error) {
            this.evalOutput.textContent = `Evaluation error: ${error.message}`;
        }
    }

    evaluateCondition(expression, step) {
        const state = step.state;
        const helper = {
            t: step.timestep,
            state,
            country: (code) => state.countries?.[code] || {},
            avg: (path) => this.averageMetric(state, path)
        };
        const safeExpression = expression.replace(/country\('([A-Za-z0-9_\-]+)'\)/g, (_, code) => `country('${code.toUpperCase()}')`);
        const fn = new Function('t', 'state', 'country', 'avg', `return (${safeExpression});`);
        return Boolean(fn(helper.t, helper.state, helper.country, helper.avg));
    }

    averageMetric(state, path) {
        const segments = path.split('.');
        const values = Object.values(state.countries || {}).map((country) => {
            let current = country;
            for (const segment of segments) {
                current = current?.[segment];
            }
            return typeof current === 'number' ? current : null;
        }).filter((value) => value !== null);
        if (values.length === 0) return 0;
        return values.reduce((sum, value) => sum + value, 0) / values.length;
    }
}

export const triggerDesigner = new TriggerDesigner();
triggerDesigner.initialize();
