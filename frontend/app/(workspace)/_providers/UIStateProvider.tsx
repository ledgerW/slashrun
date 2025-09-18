'use client';

import { createContext, useContext, useRef, type ReactNode } from 'react';
import { useStoreWithEqualityFn } from 'zustand/traditional';
import { shallow } from 'zustand/shallow';
import { createStore } from 'zustand/vanilla';

interface UIState {
  isSidebarCollapsed: boolean;
  toggleSidebar: () => void;
  isTimelineCollapsed: boolean;
  toggleTimeline: () => void;
}

type UIStateStore = ReturnType<typeof createUIStateStore>;

const UIStateContext = createContext<UIStateStore | null>(null);

function createUIStateStore() {
  return createStore<UIState>((set) => ({
    isSidebarCollapsed: false,
    toggleSidebar: () =>
      set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),
    isTimelineCollapsed: false,
    toggleTimeline: () =>
      set((state) => ({ isTimelineCollapsed: !state.isTimelineCollapsed })),
  }));
}

export function UIStateProvider({ children }: { children: ReactNode }) {
  const storeRef = useRef<UIStateStore | null>(null);
  if (!storeRef.current) {
    storeRef.current = createUIStateStore();
  }

  return (
    <UIStateContext.Provider value={storeRef.current}>{children}</UIStateContext.Provider>
  );
}

export function useUIState<T>(selector: (state: UIState) => T): T {
  const store = useContext(UIStateContext);
  if (!store) {
    throw new Error('useUIState must be used within a UIStateProvider');
  }

  return useStoreWithEqualityFn(store, selector, shallow);
}
