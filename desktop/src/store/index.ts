import { create } from 'zustand';

interface AppState {
  memoryLoaded: boolean;
  setMemoryLoaded: (loaded: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  memoryLoaded: false,
  setMemoryLoaded: (loaded) => set({ memoryLoaded: loaded }),
}));
