import { buildDetailsTree, clearChildren } from '../utils/dom.js';

export class StateInspector {
    constructor(container) {
        this.container = container;
        this.currentState = null;
    }

    render(state) {
        if (!this.container) return;
        this.currentState = state;
        clearChildren(this.container);
        if (!state) {
            this.container.textContent = 'No state loaded. Select a scenario from the library.';
            return;
        }
        const tree = buildDetailsTree(state);
        this.container.appendChild(tree);
    }

    expandAll() {
        if (!this.container) return;
        this.container.querySelectorAll('details').forEach((details) => {
            details.open = true;
        });
    }

    collapseAll() {
        if (!this.container) return;
        this.container.querySelectorAll('details').forEach((details) => {
            details.open = false;
        });
    }
}
