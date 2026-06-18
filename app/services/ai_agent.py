import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

# Import configurations and schemas
from app.core.config import GOOGLE_API_KEY, MODEL_ID, TEMPERATURE, MAX_TOKENS
from app.models.schemas import ExtractedMedicalInfo

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    medical_context: str

class MedicalAIAgent:
    def __init__(self):
        # Initialize the Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_ID,
            temperature=TEMPERATURE,
            google_api_key=GOOGLE_API_KEY,
            max_output_tokens=MAX_TOKENS
        )
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("doctor_assistant", self._assistant_node)
        workflow.add_edge(START, "doctor_assistant")
        workflow.add_edge("doctor_assistant", END)
        return workflow.compile()

    def _assistant_node(self, state: AgentState):
        messages = state.get("messages", [])
        context = state.get("medical_context", "")
        
        system_prompt = f"""You are an advanced Medical AI Assistant designed exclusively as a clinical decision support system for healthcare professionals.
        
        Use the following Patient Medical Report Context to assist the doctor. 
        Analyze the current clinical findings together with historical data to provide evidence-based insights.
        
        PATIENT MEDICAL REPORT CONTEXT:
        {context}
        
        Always maintain a professional, clinical tone. Do not invent or hallucinate patient data.
        """
        
        full_messages = [SystemMessage(content=system_prompt)] + list(messages)
        response = self.llm.invoke(full_messages)
        
        return {"messages": [response]}

    def extract_structured_info(self, raw_text: str) -> ExtractedMedicalInfo:
        # Bind the Pydantic schema to Gemini to force structured JSON output
        structured_llm = self.llm.with_structured_output(ExtractedMedicalInfo)
        
        prompt = f"""Extract the key medical information from the following clinical document. 
        If a category is not mentioned, leave the list empty.
        
        DOCUMENT TEXT:
        {raw_text}
        """
        
        result = structured_llm.invoke([HumanMessage(content=prompt)])
        return result

    def chat(self, user_message: str, medical_context: str, chat_history: list = None) -> str:
        if chat_history is None:
            chat_history = []
            
        inputs = {
            "messages": [HumanMessage(content=user_message)],
            "medical_context": medical_context
        }
        
        result = self.graph.invoke(inputs)
        return result["messages"][-1].content

# Initialize a global instance
ai_agent_instance = MedicalAIAgent()