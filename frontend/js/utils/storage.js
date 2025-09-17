const STORAGE_KEY = 'slashrun_trigger_drafts';

export function saveTriggerDraft(draft) {
    const drafts = getTriggerDrafts();
    const existingIndex = drafts.findIndex((item) => item.name === draft.name);
    if (existingIndex >= 0) {
        drafts[existingIndex] = draft;
    } else {
        drafts.push(draft);
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
}

export function getTriggerDrafts() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
        return [];
    }
    try {
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

export function deleteTriggerDraft(name) {
    const drafts = getTriggerDrafts().filter((draft) => draft.name !== name);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
}

export function clearTriggerDrafts() {
    localStorage.removeItem(STORAGE_KEY);
}
