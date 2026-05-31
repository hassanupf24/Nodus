import time
from typing import Any, Dict
from agents.base_agent import BaseAgent
from agents.schemas import AgentResponse
from llm_runtime.service import get_llm_service
from llm_runtime.schemas import ChatRequest, ChatMessage, Role
from shared.logging_config import get_logger

logger = get_logger(__name__)

class SummarizerAgent(BaseAgent):
    """Agent that creates structured summaries of files, logs, or dialogues."""

    def __init__(self) -> None:
        super().__init__(
            name="summarizer",
            description="Generates concise, structured markdown summaries of files and dialogues."
        )

    async def run(
        self, 
        query: str, 
        conversation_id: str | None = None, 
        config: Dict[str, Any] | None = None
    ) -> AgentResponse:
        start_time = time.time()
        steps = ["Analyzing input text", "Structuring document headers"]

        system_prompt = (
            "You are the Nodus Summarization Agent. Your goal is to synthesize the provided text "
            "into a clean, structured markdown document. Use the following format:\n"
            "# Summary Title\n"
            "## Core Subject\n"
            "[Brief 1-2 sentence description of main topic]\n"
            "## Key Takeaways\n"
            "- [Point 1]\n"
            "- [Point 2]\n"
            "## Extracted Key Concepts\n"
            "- [Concept/Term]: [Brief context]\n"
            "Avoid wordiness and keep it highly factual."
        )

        user_content = f"Text to summarize:\n{query}"
        
        try:
            llm = get_llm_service()
            req = ChatRequest(
                model=(config or {}).get("model", "llama3.2:3b"),
                messages=[ChatMessage(role=Role.USER, content=user_content)],
                system=system_prompt,
                stream=False
            )
            steps.append("Sending text chunks to local LLM")
            resp = await llm.chat(req)
            summary = resp.message.content
            status = "completed"
        except Exception as e:
            logger.error("agent.summarizer.llm_failed", error=str(e))
            steps.append(f"Local LLM call failed: {e}. Executing fallback parser.")
            
            # Simple fallback summarization (first three sentences + word counts)
            sentences = [s.strip() for s in query.split(".") if s.strip()]
            preview = ". ".join(sentences[:3]) + "." if sentences else "No content preview available."
            words_count = len(query.split())
            
            summary = (
                f"# Summary (Fallback Model)\n\n"
                f"## Core Subject\n"
                f"Inference server offline. Synthesized first lines: *{preview}*\n\n"
                f"## Document Metrics\n"
                f"- **Total Words:** {words_count}\n"
                f"- **Estimated Reading Time:** {max(1, words_count // 200)} min(s)\n"
                f"- **Sentence Count:** {len(sentences)}\n"
            )
            status = "degraded"

        elapsed_ms = (time.time() - start_time) * 1000
        return AgentResponse(
            agent_name=self.name,
            status=status,
            response=summary,
            steps=steps,
            metadata={
                "elapsed_ms": elapsed_ms,
                "input_length": len(query)
            }
        )
