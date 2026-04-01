from fastapi import APIRouter

from neuralflow.tools.registry import list_tools

router = APIRouter(prefix="/api/tools")


@router.get("")
async def get_builtin_tools():
    return list_tools()
