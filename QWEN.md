## Qwen Added Memories
- NeuralFlow project status (continued session):

**Completed:**
1. Redesigned all docs pages with cyberpunk/terminal aesthetic (style.css, index.html, guide/*.html, user-guide/index.html)
2. Created docs CI workflow (.github/workflows/docs.yml) - validates HTML, links, credits
3. Created local preview script (scripts/preview-docs.sh)
4. Built Tauri desktop app successfully on Linux

**Build artifacts exist at:**
- Binary: apps/desktop/src-tauri/target/release/neuralflow (20MB)
- .deb: apps/desktop/src-tauri/target/release/bundle/deb/NeuralFlow_0.1.0_amd64.deb (6.5MB)
- .rpm: apps/desktop/src-tauri/target/release/bundle/rpm/NeuralFlow-0.1.0-1.x86_64.rpm (6.5MB)

**Fixes applied to get build working:**
- keyring crate: delete_credential() → delete_password() (v2 API)
- keyring features: replaced apple-native/windows-native/linux-native with linux-secret-service-rt-async-io-crypto-rust
- Generated app icons (icons/ dir was empty)
- Installed Rust + system deps (webkit2gtk-4.1-dev, etc.)

**Pending/Not done:**
- AppImage bundling failed (linuxdeploy issue)
- No macOS/Windows builds (need those platforms)
- Python sidecar not yet bundled into the app
- CI build workflow exists at .github/workflows/build.yml (triggers on v* tags)

**Author credits:** Stanley Sujith Nelavala + repo https://github.com/ssnelavala-masstcs/neuralflow everywhere
- User is running NeuralFlow locally on Linux. Running setup-dev.sh failed with "ERROR: uv not found". User needs uv installed first via `pip install uv`.
