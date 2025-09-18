export function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

export function validateNonEmpty(value) {
    return Boolean(value && value.trim().length > 0);
}

export function validateDSL(expression) {
    if (!expression) return false;
    const prohibited = /[\{\};\$]/;
    return !prohibited.test(expression);
}

export function validateNumeric(value) {
    return value !== '' && !Number.isNaN(Number(value));
}
