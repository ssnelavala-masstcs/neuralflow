"""Single-agent execution loop: LiteLLM for standard providers, direct httpx for OpenRouter/custom."""
from __future__ import annotations

import json
import time
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.execution.event_emitter import EventEmitter
from neuralflow.execution.workflow_analyzer import NodeSpec
from neuralflow.models.run import LlmCall, NodeRun, ToolCallRecord


MAX_ITERATIONS = 20  # guard against infinite tool-call loops

# Providers that have an OpenAI-compatible API and should be called directly via httpx
# when a base URL is available (or when using OpenRouter's known URL).
_OPENAI_COMPAT_PREFIXES = {"openrouter", "lm_studio", "custom"}


class AgentRunner:
    def __init__(
        self,
        db: AsyncSession,
        run_id: str,
        node_run: NodeRun,
        emitter: EventEmitter,
        api_key: str | None = None,
        api_base: str | None = None,
    ):
        self.db = db
        self.run_id = run_id
        self.node_run = node_run
        self.emitter = emitter
        self.api_key = api_key
        self.api_base = api_base

    # ──────────────────────────────────────────────────────────────────────
    # Public entry point
    # ──────────────────────────────────────────────────────────────────────

    async def run(
        self,
        node: NodeSpec,
        messages: list[dict],
        tools: list[dict],
    ) -> dict[str, Any]:
        data = node.data
        model: str = data.get("model", "openai/gpt-4o-mini")
        temperature: float = float(data.get("temperature", 0.7))
        max_tokens: int = int(data.get("maxTokens", 2048))
        system_prompt: str = data.get("systemPrompt", "")

        full_messages: list[dict] = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        # Route: OpenRouter / custom base-URL → direct httpx
        # Everything else → LiteLLM
        provider_prefix = model.split("/")[0] if "/" in model else ""
        use_direct = (
            provider_prefix in _OPENAI_COMPAT_PREFIXES
            or bool(self.api_base)
        )

        if use_direct:
            return await self._run_direct(node, model, full_messages, tools, temperature, max_tokens)
        else:
            return await self._run_litellm(node, model, full_messages, tools, temperature, max_tokens)

    # ──────────────────────────────────────────────────────────────────────
    # Direct httpx path (OpenAI-compatible, used for OpenRouter etc.)
    # ──────────────────────────────────────────────────────────────────────

    async def _run_direct(
        self,
        node: NodeSpec,
        model: str,
        messages: list[dict],
        tools: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        import httpx

        # Determine base URL
        if model.startswith("openrouter/"):
            base_url = self.api_base or "https://openrouter.ai/api/v1"
            # Strip the "openrouter/" routing prefix — OpenRouter expects "openai/gpt-4o" etc.
            api_model = model[len("openrouter/"):]
        else:
            base_url = (self.api_base or "").rstrip("/")
            api_model = model

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        # OpenRouter strongly recommends these headers
        if "openrouter.ai" in base_url:
            headers["HTTP-Referer"] = "https://neuralflow.app"
            headers["X-Title"] = "NeuralFlow"

        body: dict[str, Any] = {
            "model": api_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"

        call_index = 0
        total_cost = 0.0
        total_input_tokens = 0
        total_output_tokens = 0
        final_output = ""
        current_messages = list(messages)

        for _ in range(MAX_ITERATIONS):
            body["messages"] = current_messages
            start_ms = int(time.time() * 1000)
            full_content = ""
            finish_reason = "stop"
            tool_calls_raw: list[dict] = []

            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=body,
                ) as resp:
                    if resp.status_code != 200:
                        err = await resp.aread()
                        raise RuntimeError(f"HTTP {resp.status_code}: {err.decode()}")

                    # Accumulate streaming tool-call fragments
                    tc_index_map: dict[int, dict] = {}

                    async for raw_line in resp.aiter_lines():
                        if not raw_line.startswith("data: "):
                            continue
                        payload = raw_line[6:]
                        if payload.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(payload)
                        except json.JSONDecodeError:
                            continue

                        choice = chunk.get("choices", [{}])[0]
                        delta = choice.get("delta", {})
                        finish_reason = choice.get("finish_reason") or finish_reason

                        # Text content
                        if delta.get("content"):
                            full_content += delta["content"]
                            await self.emitter.llm_chunk(node.id, delta["content"])

                        # Tool-call fragments (streamed as deltas)
                        for tc_delta in delta.get("tool_calls", []):
                            idx = tc_delta.get("index", 0)
                            if idx not in tc_index_map:
                                tc_index_map[idx] = {
                                    "id": tc_delta.get("id", ""),
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""},
                                }
                            entry = tc_index_map[idx]
                            fn = tc_delta.get("function", {})
                            if fn.get("name"):
                                entry["function"]["name"] += fn["name"]
                            if fn.get("arguments"):
                                entry["function"]["arguments"] += fn["arguments"]
                            if tc_delta.get("id"):
                                entry["id"] = tc_delta["id"]

                    tool_calls_raw = list(tc_index_map.values())

            latency = int(time.time() * 1000) - start_ms

            # Persist llm_call (no token counts from OpenRouter streaming — set to 0)
            llm_call = LlmCall(
                id=str(uuid.uuid4()),
                node_run_id=self.node_run.id,
                run_id=self.run_id,
                provider=api_model.split("/")[0] if "/" in api_model else "openrouter",
                model=api_model,
                call_index=call_index,
                messages=json.dumps(current_messages),
                response=json.dumps({"content": full_content}),
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                latency_ms=latency,
                finish_reason=finish_reason,
            )
            self.db.add(llm_call)
            await self.db.flush()

            # Handle tool calls
            if tool_calls_raw and finish_reason == "tool_calls":
                current_messages.append({
                    "role": "assistant",
                    "content": full_content or None,
                    "tool_calls": tool_calls_raw,
                })
                for tc in tool_calls_raw:
                    fn = tc.get("function", {})
                    tool_name = fn.get("name", "")
                    try:
                        tool_input = json.loads(fn.get("arguments", "{}"))
                    except Exception:
                        tool_input = {}

                    await self.emitter.tool_call(node.id, tool_name, tool_input)
                    tool_output, tool_error = await self._dispatch_tool(tool_name, tool_input)

                    tc_record = ToolCallRecord(
                        id=str(uuid.uuid4()),
                        llm_call_id=llm_call.id,
                        node_run_id=self.node_run.id,
                        run_id=self.run_id,
                        tool_name=tool_name,
                        tool_source="builtin",
                        input_data=json.dumps(tool_input),
                        output_data=json.dumps(tool_output) if tool_output is not None else None,
                        error=tool_error,
                    )
                    self.db.add(tc_record)
                    await self.emitter.tool_result(node.id, tool_name, tool_output)

                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id", ""),
                        "content": json.dumps(tool_output) if tool_output is not None else (tool_error or ""),
                    })
                call_index += 1
                continue

            final_output = full_content
            break

        self.node_run.cost_usd = total_cost
        self.node_run.input_tokens = total_input_tokens
        self.node_run.output_tokens = total_output_tokens
        await self.db.flush()

        return {"output": final_output, "cost_usd": total_cost}

    # ──────────────────────────────────────────────────────────────────────
    # LiteLLM path (OpenAI, Anthropic, Groq, Mistral, etc.)
    # ──────────────────────────────────────────────────────────────────────

    async def _run_litellm(
        self,
        node: NodeSpec,
        model: str,
        messages: list[dict],
        tools: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        import litellm

        call_index = 0
        total_cost = 0.0
        total_input_tokens = 0
        total_output_tokens = 0
        final_output = ""
        current_messages = list(messages)

        for _ in range(MAX_ITERATIONS):
            kwargs: dict[str, Any] = dict(
                model=model,
                messages=current_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.api_base:
                kwargs["api_base"] = self.api_base
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            start_ms = int(time.time() * 1000)
            chunks: list[Any] = []
            full_content = ""

            async for chunk in await litellm.acompletion(**kwargs):
                chunks.append(chunk)
                delta = chunk.choices[0].delta
                if delta.content:
                    full_content += delta.content
                    await self.emitter.llm_chunk(node.id, delta.content)

            latency = int(time.time() * 1000) - start_ms

            response = litellm.stream_chunk_builder(chunks)
            usage = getattr(response, "usage", None)
            input_tok = getattr(usage, "prompt_tokens", 0) or 0
            output_tok = getattr(usage, "completion_tokens", 0) or 0

            try:
                cost = litellm.completion_cost(completion_response=response)
            except Exception:
                cost = 0.0

            total_cost += cost
            total_input_tokens += input_tok
            total_output_tokens += output_tok

            llm_call = LlmCall(
                id=str(uuid.uuid4()),
                node_run_id=self.node_run.id,
                run_id=self.run_id,
                provider=model.split("/")[0] if "/" in model else "unknown",
                model=model,
                call_index=call_index,
                messages=json.dumps(current_messages),
                response=json.dumps(response.model_dump() if hasattr(response, "model_dump") else {}),
                input_tokens=input_tok,
                output_tokens=output_tok,
                cost_usd=cost,
                latency_ms=latency,
                finish_reason=response.choices[0].finish_reason if response.choices else None,
            )
            self.db.add(llm_call)
            await self.db.flush()

            choice = response.choices[0]
            finish_reason = choice.finish_reason
            tool_calls = getattr(choice.message, "tool_calls", None) or []

            if tool_calls and finish_reason == "tool_calls":
                current_messages.append(choice.message.model_dump())
                for tc in tool_calls:
                    fn = tc.function
                    tool_name = fn.name
                    try:
                        tool_input = json.loads(fn.arguments)
                    except Exception:
                        tool_input = {}

                    await self.emitter.tool_call(node.id, tool_name, tool_input)
                    tool_output, tool_error = await self._dispatch_tool(tool_name, tool_input)

                    tc_record = ToolCallRecord(
                        id=str(uuid.uuid4()),
                        llm_call_id=llm_call.id,
                        node_run_id=self.node_run.id,
                        run_id=self.run_id,
                        tool_name=tool_name,
                        tool_source="builtin",
                        input_data=json.dumps(tool_input),
                        output_data=json.dumps(tool_output) if tool_output is not None else None,
                        error=tool_error,
                    )
                    self.db.add(tc_record)
                    await self.emitter.tool_result(node.id, tool_name, tool_output)

                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(tool_output) if tool_output is not None else (tool_error or ""),
                    })
                call_index += 1
                continue

            final_output = full_content or (
                choice.message.content if hasattr(choice.message, "content") else ""
            )
            break

        self.node_run.cost_usd = total_cost
        self.node_run.input_tokens = total_input_tokens
        self.node_run.output_tokens = total_output_tokens
        await self.db.flush()

        return {"output": final_output, "cost_usd": total_cost}

    # ──────────────────────────────────────────────────────────────────────
    # Tool dispatch
    # ──────────────────────────────────────────────────────────────────────

    async def _dispatch_tool(self, tool_name: str, tool_input: dict) -> tuple[Any, str | None]:
        from neuralflow.tools.registry import get_tool

        tool = get_tool(tool_name)
        if tool is None:
            return None, f"Tool '{tool_name}' not found"
        try:
            result = await tool.execute(tool_input)
            return result, None
        except Exception as exc:
            return None, str(exc)
