mod commands;

use commands::keychain::{keychain_delete, keychain_get, keychain_set};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .invoke_handler(tauri::generate_handler![keychain_set, keychain_get, keychain_delete])
        .run(tauri::generate_context!())
        .expect("error while running NeuralFlow");
}
