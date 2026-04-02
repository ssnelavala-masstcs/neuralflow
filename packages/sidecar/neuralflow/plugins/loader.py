"""Plugin loader: discovers installed NeuralFlow plugins via entry_points."""
from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)

ENTRY_POINT_GROUP = "neuralflow_plugins"


@dataclass
class PluginManifest:
    name: str           # e.g. "my-plugin"
    version: str        # e.g. "0.1.0"
    description: str
    author: str
    node_types: list[str]    # node type names this plugin adds
    tool_names: list[str]    # tool names this plugin registers
    package: str             # Python package name
    loaded: bool = False
    error: str | None = None


_loaded_plugins: dict[str, PluginManifest] = {}


def discover_plugins() -> list[PluginManifest]:
    """Scan installed packages for neuralflow_plugins entry points."""
    from importlib.metadata import entry_points

    manifests: list[PluginManifest] = []
    eps = entry_points(group=ENTRY_POINT_GROUP)

    for ep in eps:
        try:
            plugin_module = ep.load()
            manifest_data = getattr(plugin_module, "MANIFEST", {})
            manifest = PluginManifest(
                name=manifest_data.get("name", ep.name),
                version=manifest_data.get("version", "unknown"),
                description=manifest_data.get("description", ""),
                author=manifest_data.get("author", ""),
                node_types=manifest_data.get("node_types", []),
                tool_names=manifest_data.get("tool_names", []),
                package=ep.value.split(":")[0],
            )
            manifests.append(manifest)
        except Exception as exc:
            log.warning("Failed to load plugin entry point %s: %s", ep.name, exc)
            manifests.append(PluginManifest(
                name=ep.name, version="error", description="", author="",
                node_types=[], tool_names=[], package="", error=str(exc)
            ))

    return manifests


def load_all_plugins() -> list[PluginManifest]:
    """Load all discovered plugins, registering their tools."""
    manifests = discover_plugins()
    for manifest in manifests:
        try:
            pkg = importlib.import_module(manifest.package)
            if hasattr(pkg, "register"):
                pkg.register()
            manifest.loaded = True
            _loaded_plugins[manifest.name] = manifest
            log.info(
                "Loaded plugin: %s v%s (%d tools, %d node types)",
                manifest.name, manifest.version,
                len(manifest.tool_names), len(manifest.node_types),
            )
        except Exception as exc:
            manifest.error = str(exc)
            log.warning("Failed to load plugin %s: %s", manifest.name, exc)

    return manifests


def get_loaded_plugins() -> list[PluginManifest]:
    return list(_loaded_plugins.values())


def get_plugin(name: str) -> PluginManifest | None:
    return _loaded_plugins.get(name)
