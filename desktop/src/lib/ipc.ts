import { invoke } from '@tauri-apps/api/core';

export const startLocalBackend = async () => {
  return await invoke('start_local_backend');
};

export const getVaultKey = async () => {
  return await invoke('get_vault_key');
};
