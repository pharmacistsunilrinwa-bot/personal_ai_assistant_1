import google.generativeai as genai
from config import Config
import logging
from typing import Dict, Any, List, Optional

class PatternRecognitionService:
    DEFAULT_SYSTEM_INSTRUCTION = (
        "You are an expert Pattern Recognition and Logical Reasoning Engine. "
        "Your core objective is to analyze complex puzzles, identify subtle patterns "
        "(numerical, linguistic, behavioral, or logical), and solve problems using rigorous "
        "first-principles deduction.\n\n"
        "Guidelines for your response:\n"
        "1. Step-by-Step Chain of Thought (CoT): Always break down the inputs into smaller logical chunks. "
        "Explicitly list your observations, assumptions, and hypotheses before reaching a final conclusion.\n"
        "2. Pattern Recognition: If a sequence (numbers, shapes, words) is provided, identify the underlying rule/formula, "
        "explain the transition states, and predict future items in the sequence.\n"
        "3. Structured Analysis: Format your output with clear headers:\n"
        "   - **Observations**: What facts are directly stated or visible?\n"
        "   - **Hypothesis/Pattern Rule**: What is the suspected logic, pattern, or mathematical formula?\n"
        "   - **Deductive Steps**: Step-by-step verification of the hypothesis.\n"
        "   - **Logical Conclusion**: The final, definitive answer or prediction."
    )

    def __init__(self):
        self._setup_client()

    def _setup_client(self, system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION):
        """Initializes the Gemini client and applies System Instructions."""
        api_key = Config.get_gemini_api_key()
        genai.configure(api_key=api_key)
        self.system_instruction = system_instruction
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            system_instruction=system_instruction
        )

    async def solve_logic_problem(self, prompt: str, custom_instruction: Optional[str] = None) -> str:
        """Solves a logic problem or detects patterns using the system instruction.
        
        Supports optional custom_instruction to override or append to default reasoning parameters.
        """
        # If a custom instruction is specified, re-setup the model temporarily with it
        if custom_instruction:
            self._setup_client(system_instruction=custom_instruction)
        else:
            if self.system_instruction != self.DEFAULT_SYSTEM_INSTRUCTION:
                self._setup_client(self.DEFAULT_SYSTEM_INSTRUCTION)

        for _ in range(len(Config.GEMINI_API_KEYS)):
            try:
                response = await self.model.generate_content_async(prompt)
                return response.text
            except Exception as e:
                logging.error(f"Error in PatternRecognitionService: {e}")
                if "429" in str(e) or "quota" in str(e).lower():
                    logging.info("Rotating API key due to rate limit/quota in logic engine...")
                    Config.rotate_key()
                    # Re-initialize with the updated current API key
                    self._setup_client(self.system_instruction)
                else:
                    raise e
        raise Exception("All API keys exhausted or failed in Pattern Recognition engine.")

    async def detect_sequence_pattern(self, elements: List[Any]) -> Dict[str, Any]:
        """Provides a specific utility endpoint to analyze a sequence and predict the next elements."""
        prompt = (
            f"Analyze the following sequence and determine the pattern: {elements}.\n"
            f"What are the next 3 elements? Explain the pattern rule clearly."
        )
        response_text = await self.solve_logic_problem(prompt)
        return {
            "sequence": elements,
            "analysis_and_prediction": response_text
        }
