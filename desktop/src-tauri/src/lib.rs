// Nodus Core Tauri Commands
#[tauri::command]
fn start_local_backend() -> Result<String, String> {
    // Stub: Spawns the local FastAPI backend using `uv run` or bundled binary
    Ok("Backend started successfully".into())
}

#[tauri::command]
fn get_vault_key() -> Result<String, String> {
    // Stub: Interacts with OS Keychain to get/set Nodus encryption key
    Ok("secure-key-stub".into())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![start_local_backend, get_vault_key])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
