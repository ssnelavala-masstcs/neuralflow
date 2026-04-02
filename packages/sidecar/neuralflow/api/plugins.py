from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from neuralflow.plugins.loader import (
    discover_plugins,
    load_all_plugins,
    get_loaded_plugins,
    get_plugin,
    PluginManifest,
)

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


class PluginOut(BaseModel):
    name: str
    version: str
    description: str
    author: str
    node_types: list[str]
    tool_names: list[str]
    package: str
    loaded: bool
    error: str | None


def _to_out(m: PluginManifest) -> PluginOut:
    return PluginOut(
        name=m.name,
        version=m.version,
        description=m.description,
        author=m.author,
        node_types=m.node_types,
        tool_names=m.tool_names,
        package=m.package,
        loaded=m.loaded,
        error=m.error,
    )


@router.get("", response_model=list[PluginOut])
def list_plugins() -> list[PluginOut]:
    return [_to_out(m) for m in get_loaded_plugins()]


@router.get("/{name}", response_model=PluginOut)
def get_plugin_by_name(name: str) -> PluginOut:
    manifest = get_plugin(name)
    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")
    return _to_out(manifest)


@router.post("/reload", response_model=list[PluginOut])
def reload_plugins() -> list[PluginOut]:
    manifests = load_all_plugins()
    return [_to_out(m) for m in manifests]
