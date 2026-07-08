from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.retriever import retrieve
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

DIFFICULTY_PARAMS = {
    "Easy": {
        "who_can_answer": "Any student who just read Q&A once",
        "thinking_time": "10-20 seconds",
        "answerable_percentage": "100% of students",
        "bloom_level": "Remember and Understand",
        "instructions": """
        - Ask direct definition or fact-based questions
        - Use simple language, no complex terminology
        - Make 3 options obviously wrong, 1 clearly correct
        - No tricks or traps
        - Focus on key terms and basic concepts
        """
    },
    "Medium": {
        "who_can_answer": "Average student who understood the concepts",
        "thinking_time": "30-60 seconds",
        "answerable_percentage": "50-60% of students",
        "bloom_level": "Apply and Analyze",
        "instructions": """
        - Ask questions requiring understanding not just memorization
        - Use scenario-based or application questions
        - Make all 4 options plausible but only 1 correct
        - Include compare and contrast questions
        """
    },
    "Hard": {
        "who_can_answer": "Only top rankers after deep thinking",
        "thinking_time": "2-5 minutes",
        "answerable_percentage": "10-20% of students",
        "bloom_level": "Evaluate and Create",
        "instructions": """
        - First 8 questions: Very complex multi-step reasoning
          * Tricky distractors that seem correct at first glance
          * Edge cases and exceptions
          * Require connecting multiple concepts
        - Last 2 questions: Extremely hard [CHALLENGE] level
          * Almost no student can answer
          * Beyond-syllabus deep thinking required
          * Label these with [CHALLENGE]
        """
    }
}

class MCQState(TypedDict):
    syllabus_text: str
    topics: List[str]
    difficulty: str
    num_questions: int
    mcqs_raw: str
    mcqs_parsed: List[dict]
    error: str

def topic_extractor_agent(state: MCQState) -> MCQState:
    print("[Agent 1] Extracting topics...")
    prompt = ChatPromptTemplate.from_template("""
You are a syllabus analysis expert.
Extract all key topics from the syllabus below.
Return ONLY a numbered list of topics.

Syllabus:
{syllabus}

Topics:""")
    response = (prompt | llm).invoke({"syllabus": state["syllabus_text"]})
    topics = [
        line.strip()
        for line in response.content.split("\n")
        if line.strip() and line.strip()[0].isdigit()
    ]
    print(f"   [OK] Found {len(topics)} topics")
    return {**state, "topics": topics}

def mcq_generator_agent(state: MCQState) -> MCQState:
    print(f"[Agent 2] Generating {state['difficulty']} MCQs...")
    params = DIFFICULTY_PARAMS[state["difficulty"]]
    topics_text = "\n".join(state["topics"][:10])

    chunks = []
    for topic in state["topics"][:5]:
        retrieved = retrieve(topic, top_k=2)
        chunks.extend(retrieved)
    context = "\n".join([c["text"] for c in chunks[:8]])

    prompt = ChatPromptTemplate.from_template("""
You are an expert university exam question creator.
Generate exactly {num_questions} MCQs at {difficulty} difficulty.

Who can answer: {who_can_answer}
Thinking time: {thinking_time}
Bloom's level: {bloom_level}
Instructions: {instructions}

Topics: {topics}
Context: {context}

IMPORTANT: Return ONLY a valid JSON array. No extra text before or after.
Each question must follow this exact structure:
[
  {{
    "question": "Full question text here?",
    "options": {{
      "A": "First option text",
      "B": "Second option text",
      "C": "Third option text",
      "D": "Fourth option text"
    }},
    "answer": "A",
    "explanation": "Why this answer is correct",
    "thinking_time": "{thinking_time}",
    "is_challenge": false
  }}
]

For Hard difficulty last 2 questions set "is_challenge": true.
Return ONLY the JSON array now:""")

    response = (prompt | llm).invoke({
        "num_questions": state["num_questions"],
        "difficulty": state["difficulty"],
        "who_can_answer": params["who_can_answer"],
        "thinking_time": params["thinking_time"],
        "bloom_level": params["bloom_level"],
        "instructions": params["instructions"],
        "topics": topics_text,
        "context": context
    })

    print("   [OK] MCQs generated")
    return {**state, "mcqs_raw": response.content}

def mcq_parser_agent(state: MCQState) -> MCQState:
    print("[Agent 3] Parsing MCQs...")
    raw = state["mcqs_raw"]

    # Extract JSON from response
    json_match = re.search(r'\[.*\]', raw, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        try:
            parsed = json.loads(json_str)
            print(f"   [OK] Parsed {len(parsed)} questions")
            return {**state, "mcqs_parsed": parsed}
        except:
            pass

    print("   [WARN] Parsing failed, returning raw")
    return {**state, "mcqs_parsed": []}

def quality_checker_agent(state: MCQState) -> MCQState:
    print("[Agent 4] Quality checking...")
    if not state["mcqs_parsed"]:
        # Try to fix by re-prompting
        prompt = ChatPromptTemplate.from_template("""
Fix this JSON and return ONLY a valid JSON array of MCQ objects.
Each object must have: question, options (A/B/C/D), answer, explanation, thinking_time, is_challenge.

Raw input:
{raw}

Return ONLY valid JSON array:""")
        response = (prompt | llm).invoke({"raw": state["mcqs_raw"]})
        json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return {**state, "mcqs_parsed": parsed}
            except:
                pass

    print("   [OK] Quality check done")
    return state

def build_mcq_graph():
    graph = StateGraph(MCQState)
    graph.add_node("topic_extractor", topic_extractor_agent)
    graph.add_node("mcq_generator", mcq_generator_agent)
    graph.add_node("mcq_parser", mcq_parser_agent)
    graph.add_node("quality_checker", quality_checker_agent)

    graph.set_entry_point("topic_extractor")
    graph.add_edge("topic_extractor", "mcq_generator")
    graph.add_edge("mcq_generator", "mcq_parser")
    graph.add_edge("mcq_parser", "quality_checker")
    graph.add_edge("quality_checker", END)

    return graph.compile()

def generate_mcqs_with_agents(syllabus_text: str, difficulty: str, num_questions: int):
    graph = build_mcq_graph()
    result = graph.invoke(MCQState(
        syllabus_text=syllabus_text,
        topics=[],
        difficulty=difficulty,
        num_questions=num_questions,
        mcqs_raw="",
        mcqs_parsed=[],
        error=""
    ))
    return result["mcqs_parsed"]