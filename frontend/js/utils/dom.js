export function createElement(tag, options = {}) {
    const element = document.createElement(tag);
    if (options.classList) {
        element.className = options.classList;
    }
    if (options.text !== undefined) {
        element.textContent = options.text;
    }
    if (options.attributes) {
        Object.entries(options.attributes).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                element.setAttribute(key, String(value));
            }
        });
    }
    if (options.dataset) {
        Object.entries(options.dataset).forEach(([key, value]) => {
            element.dataset[key] = value;
        });
    }
    return element;
}

export function clearChildren(node) {
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
}

export function appendChildren(parent, children) {
    children.forEach((child) => {
        if (child) {
            parent.appendChild(child);
        }
    });
    return parent;
}

export function formatNumber(value, options = {}) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '—';
    }
    const formatter = new Intl.NumberFormat('en-US', options);
    return formatter.format(value);
}

export function formatPercent(value, fractionDigits = 2) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '—';
    }
    return `${(value * 100).toFixed(fractionDigits)}%`;
}

export function animateCount(element, value, duration = 320) {
    if (!element) return;
    const start = performance.now();
    const initial = Number(element.dataset.currentValue || '0');
    const target = Number(value);
    const step = (timestamp) => {
        const progress = Math.min((timestamp - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = initial + (target - initial) * eased;
        element.textContent = formatNumber(current, { maximumFractionDigits: 1 });
        element.dataset.currentValue = String(target);
        if (progress < 1) {
            requestAnimationFrame(step);
        }
    };
    requestAnimationFrame(step);
}

export function toggleHidden(node, hide) {
    node.classList.toggle('hidden', hide);
}

export function setStatusLight(element, status) {
    if (!element) return;
    element.classList.toggle('online', status === 'online');
}

export function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

export function buildDetailsTree(data, level = 0) {
    if (data === null || data === undefined) {
        return createElement('div', { classList: 'state-value', text: 'null' });
    }

    if (typeof data !== 'object') {
        return createElement('div', { classList: 'state-value', text: String(data) });
    }

    const container = createElement('div', { classList: 'state-node' });

    Object.entries(data).forEach(([key, value]) => {
        const details = document.createElement('details');
        details.open = level < 1;
        const summary = document.createElement('summary');
        summary.textContent = key;
        details.appendChild(summary);

        if (typeof value === 'object' && value !== null) {
            details.appendChild(buildDetailsTree(value, level + 1));
        } else {
            const leaf = createElement('div', { classList: 'state-value', text: String(value) });
            details.appendChild(leaf);
        }
        container.appendChild(details);
    });

    return container;
}
