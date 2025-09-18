import { auth } from './auth.js';
import { createElement, clearChildren } from './utils/dom.js';

const PREFERENCE_KEY = 'slashrun_preferences';

function loadPreferences() {
    try {
        const raw = localStorage.getItem(PREFERENCE_KEY);
        return raw ? JSON.parse(raw) : { animations: true, autoplay: false };
    } catch {
        return { animations: true, autoplay: false };
    }
}

function savePreferences(prefs) {
    localStorage.setItem(PREFERENCE_KEY, JSON.stringify(prefs));
}

function initializeDashboard() {
    if (!auth.requireAuth()) return;
    const user = auth.getUser();
    const userDisplay = document.getElementById('user-display');
    if (userDisplay && user) {
        userDisplay.textContent = `${user.username} • ${user.email}`;
    }
    const logoutButton = document.getElementById('logout-btn');
    logoutButton?.addEventListener('click', () => auth.logout());

    const navLinks = document.querySelectorAll('.nav-link');
    const panels = document.querySelectorAll('[data-panel]');
    navLinks.forEach((link) => {
        link.addEventListener('click', () => {
            navLinks.forEach((item) => item.classList.remove('active'));
            link.classList.add('active');
            const target = link.dataset.panel;
            panels.forEach((panel) => {
                panel.classList.toggle('hidden', panel.id !== target);
            });
        });
    });

    const preferences = loadPreferences();
    const animationToggle = document.getElementById('setting-animations');
    const autoplayToggle = document.getElementById('setting-autoplay');
    if (animationToggle) {
        animationToggle.checked = preferences.animations;
        animationToggle.addEventListener('change', () => {
            preferences.animations = animationToggle.checked;
            document.body.dataset.animations = animationToggle.checked ? 'on' : 'off';
            savePreferences(preferences);
        });
        document.body.dataset.animations = animationToggle.checked ? 'on' : 'off';
    }
    if (autoplayToggle) {
        autoplayToggle.checked = preferences.autoplay;
        autoplayToggle.addEventListener('change', () => {
            preferences.autoplay = autoplayToggle.checked;
            savePreferences(preferences);
        });
    }

    document.addEventListener('scenario:selected', () => {
        const prefs = loadPreferences();
        if (prefs.autoplay) {
            const playButton = document.getElementById('timeline-play');
            if (playButton && playButton.textContent === 'Play') {
                playButton.click();
            }
        }
    });

    populateDataCatalog();
}

function populateDataCatalog() {
    const catalog = document.getElementById('data-catalog-content');
    if (!catalog) return;
    clearChildren(catalog);
    const entries = [
        {
            title: 'Macro: GDP, Inflation, Output Gap',
            description: 'Derived from \u03a3 of country macro states. Reducers reference Taylor rules and Phillips curve elasticities to adjust policy_rate and inflation expectations.',
            insight: 'Audit the monetary_policy reducer to trace contributions from neutral_rate, inflation_target, and output_gap for each country.'
        },
        {
            title: 'Trade Networks',
            description: 'Weighted adjacency matrices stored in trade_matrix. Reducers apply tariff_multiplier and ntm_shock from rules.regimes.trade to simulate trade disruptions.',
            insight: 'Use the network lens to highlight edges above the 0.7 intensity threshold to identify fragile trade corridors.'
        },
        {
            title: 'Financial Sector Stress',
            description: 'Interbank exposures and sovereign yields feed leverage targets and liquidity reducers. Track credit_spread and bank_tier1_ratio for stability diagnostics.',
            insight: 'Trigger templates include liquidity injections when average credit spreads exceed 250bps.'
        },
        {
            title: 'Security & Sentiment',
            description: 'Security.milex_gdp and Sentiment.policy_pressure inform mobilization and propaganda reducers. Event injections can pivot these metrics dramatically.',
            insight: 'Combine mobilization events with sentiment propaganda_gain patches to model hybrid warfare scenarios.'
        }
    ];
    entries.forEach((entry) => {
        const card = createElement('article', { classList: 'catalog-card' });
        card.appendChild(createElement('h3', { text: entry.title }));
        card.appendChild(createElement('p', { text: entry.description }));
        card.appendChild(createElement('p', { classList: 'small', text: entry.insight }));
        catalog.appendChild(card);
    });
}

if (document.body.classList.contains('console-body')) {
    initializeDashboard();
} else if (document.body.classList.contains('landing-body')) {
    const primaryBtn = document.querySelector('.btn-primary');
    primaryBtn?.addEventListener('mouseover', () => {
        document.body.dataset.animations = 'pulse';
    });
}
