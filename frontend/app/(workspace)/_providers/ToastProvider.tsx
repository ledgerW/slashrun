'use client';

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type CSSProperties,
  type ReactNode,
} from 'react';
import { createPortal } from 'react-dom';

interface ToastOptions {
  id: number;
  title: string;
  description?: string;
  variant?: 'default' | 'success' | 'error';
  duration?: number;
}

interface ToastInput {
  title: string;
  description?: string;
  variant?: 'default' | 'success' | 'error';
  duration?: number;
}

interface ToastContextValue {
  pushToast: (toast: ToastInput) => void;
  dismissToast: (id: number) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastOptions[]>([]);

  const removeToast = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const pushToast = useCallback(
    (toast: ToastInput) => {
      const id = Number(`${Date.now()}${Math.floor(Math.random() * 1000)}`);
      const toastWithDefaults: ToastOptions = {
        id,
        title: toast.title,
        description: toast.description,
        variant: toast.variant ?? 'default',
        duration: toast.duration ?? 5000,
      };

      setToasts((current) => [...current, toastWithDefaults]);

      if (toastWithDefaults.duration && toastWithDefaults.duration > 0) {
        window.setTimeout(() => {
          removeToast(id);
        }, toastWithDefaults.duration);
      }
    },
    [removeToast],
  );

  const dismissToast = useCallback(
    (id: number) => {
      removeToast(id);
    },
    [removeToast],
  );

  const contextValue = useMemo(
    () => ({
      pushToast,
      dismissToast,
    }),
    [pushToast, dismissToast],
  );

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      {typeof document !== 'undefined'
        ? createPortal(
            <ToastViewport toasts={toasts} dismissToast={dismissToast} />,
            document.body,
          )
        : null}
    </ToastContext.Provider>
  );
}

function ToastViewport({
  toasts,
  dismissToast,
}: {
  toasts: ToastOptions[];
  dismissToast: (id: number) => void;
}) {
  if (typeof document === 'undefined') {
    return null;
  }

  return (
    <div
      aria-live="assertive"
      aria-atomic="true"
      style={{
        position: 'fixed',
        insetBlockEnd: '24px',
        insetInlineEnd: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        zIndex: 50,
      }}
    >
      {toasts.map((toast) => (
        <article
          key={toast.id}
          role="status"
          style={getToastStyle(toast.variant)}
          tabIndex={0}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <strong style={{ fontSize: '14px' }}>{toast.title}</strong>
              {toast.description ? (
                <p style={{ margin: 0, fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                  {toast.description}
                </p>
              ) : null}
            </div>
            <button
              type="button"
              onClick={() => dismissToast(toast.id)}
              style={{
                border: 'none',
                background: 'transparent',
                color: 'inherit',
                cursor: 'pointer',
                fontSize: '16px',
              }}
              aria-label="Dismiss notification"
            >
              ×
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}

function getToastStyle(variant: ToastOptions['variant']) {
  const baseStyle: CSSProperties = {
    minWidth: '260px',
    maxWidth: '320px',
    padding: '14px 16px',
    borderRadius: 'var(--radius-md)',
    background: 'rgba(13, 20, 34, 0.95)',
    color: 'var(--color-text-primary)',
    border: '1px solid rgba(78, 160, 255, 0.35)',
    boxShadow: '0 8px 20px rgba(0, 0, 0, 0.35)',
  };

  switch (variant) {
    case 'success':
      return {
        ...baseStyle,
        borderColor: 'rgba(76, 207, 144, 0.45)',
      };
    case 'error':
      return {
        ...baseStyle,
        borderColor: 'rgba(255, 92, 92, 0.45)',
      };
    default:
      return baseStyle;
  }
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  return context;
}
