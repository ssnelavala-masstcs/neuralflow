"""Single-agent execution loop: LiteLLM + tool dispatch."""
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

    async def run(
        self,
        node: NodeSpec,
        messages: list[dict],
        tools: list[dict],
    ) -> dict[str, Any]:
        import litellm

        data = node.data
        model: str = data.get("model", "openai/gpt-4o-mini")
        temperature: float = float(data.get("temperature", 0.7))
        max_tokens: int = int(data.get("maxTokens", 2048))
        system_prompt: str = data.get("systemPrompt", "")

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        call_index = 0
        total_cost = 0.0
        total_input_tokens = 0
        total_output_tokens = 0
        final_output = ""

        for _ in range(MAX_ITERATIONS):
            kwargs: dict[str, Any] = dict(
                model=model,
                messages=full_messages,
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

            end_ms = int(time.time() * 1000)
            latency = end_ms - start_ms

            # Reconstruct final response from stream
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

            # Persist llm_call record
            llm_call = LlmCall(
                id=str(uuid.uuid4()),
                node_run_id=self.node_run.id,
                run_id=self.run_id,
                provider=model.split("/")[0] if "/" in model else "unknown",
                model=model,
                call_index=call_index,
                messages=json.dumps(full_messages),
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

            # Handle tool calls
            tool_calls = getattr(choice.message, "tool_calls", None) or []
            if tool_calls and finish_reason == "tool_calls":
                full_messages.append(choice.message.model_dump())
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

                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(tool_output) if tool_output is not None else (tool_error or ""),
                    })
                call_index += 1
                continue  # next LLM iteration

            # Normal stop
            final_output = full_content or (
                choice.message.content if hasattr(choice.message, "content") else ""
            )
            break

        # Update node_run stats
        self.node_run.cost_usd = total_cost
        self.node_run.input_tokens = total_input_tokens
        self.node_run.output_tokens = total_output_tokens
        await self.db.flush()

        return {"output": final_output, "cost_usd": total_cost}

    async def _dispatch_tool(self, tool_name: str, tool_input: dict) -> tuple[Any, str | None]:
        """Route a tool call to the built-in registry."""
        from neuralflow.tools.registry import get_tool

        tool = get_tool(tool_name)
        if tool is None:
            return None, f"Tool '{tool_name}' not found"
        try:
            result = await tool.execute(tool_input)
            return result, None
        except Exception as exc:
            return None, str(exc)
