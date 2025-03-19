import logging
import time
from typing import List, Dict, Any, Optional
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class AIModelService:
    """Service for interacting with different AI models."""
    
    def __init__(self):
        """Initialize the AI model service."""
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("AI Model Service initialized")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError))
    )
    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        model_type: str = "default",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get a completion from an AI model.
        
        Args:
            messages: List of message dictionaries with role and content.
            model_type: Type of model to use (default, medical_advice, policy_expert, patient_history).
            model_name: Specific model name to override the default for the model_type.
            **kwargs: Additional parameters to pass to the model.
            
        Returns:
            Dict containing response content and metadata.
        """
        start_time = time.time()
        
        # Select the model name based on the model type
        if not model_name:
            if model_type == "medical_advice":
                model_name = settings.MEDICAL_ADVICE_MODEL
            elif model_type == "policy_expert":
                model_name = settings.POLICY_EXPERT_MODEL
            elif model_type == "patient_history":
                model_name = settings.PATIENT_HISTORY_MODEL
            else:
                model_name = settings.DEFAULT_CHAT_MODEL
        
        # Get the model settings based on the model type
        model_settings = settings.MODEL_SETTINGS.get(model_type, settings.MODEL_SETTINGS["default"]).copy()
        
        # Override with any provided kwargs
        model_settings.update(kwargs)
        
        try:
            # Call the OpenAI API
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=messages,
                **model_settings
            )
            
            # Process the response
            processing_time = time.time() - start_time
            tokens_used = response.usage.total_tokens if hasattr(response, "usage") else None
            
            result = {
                "content": response.choices[0].message.content,
                "model": model_name,
                "processing_time": processing_time,
                "tokens_used": tokens_used,
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(
                f"AI completion successful: model={model_name}, "
                f"tokens={tokens_used}, time={processing_time:.2f}s"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting AI completion: {str(e)}")
            raise

    async def get_medical_advice(
        self, 
        user_query: str, 
        chat_history: List[Dict[str, str]] = None,
        patient_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get medical advice from a specialized medical model.
        
        Args:
            user_query: The user's medical question.
            chat_history: Optional previous conversation history.
            patient_info: Optional patient information to contextualize the advice.
            
        Returns:
            Dict containing the medical advice and metadata.
        """
        messages = []
        
        # Add system message with instructions for the medical advice model
        system_message = {
            "role": "system",
            "content": (
                "You are a healthcare AI assistant trained to provide evidence-based health information. "
                "Always clarify that you're not a licensed medical professional and cannot provide medical diagnosis. "
                "Provide information based on medical literature and best practices. "
                "When uncertain, acknowledge limitations and suggest consulting healthcare providers."
            )
        }
        messages.append(system_message)
        
        # Add patient context if available
        if patient_info:
            patient_context = {
                "role": "system",
                "content": f"Patient information: {patient_info}"
            }
            messages.append(patient_context)
        
        # Add chat history if available
        if chat_history:
            messages.extend(chat_history)
        
        # Add the current user query
        messages.append({"role": "user", "content": user_query})
        
        # Get response from the medical advice model
        return await self.get_completion(messages, model_type="medical_advice")
    
    async def get_policy_information(
        self, 
        user_query: str,
        chat_history: List[Dict[str, str]] = None,
        policy_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get health policy information from a specialized policy model.
        
        Args:
            user_query: The user's policy-related question.
            chat_history: Optional previous conversation history.
            policy_data: Optional structured policy data retrieved from database.
            
        Returns:
            Dict containing the policy information and metadata.
        """
        messages = []
        
        # Add system message with instructions for the policy expert model
        system_message = {
            "role": "system",
            "content": (
                "You are a healthcare policy expert AI assistant. "
                "Provide accurate information about health policies, regulations, and guidelines. "
                "Always cite sources when possible and clarify when policies may vary by jurisdiction. "
                "When uncertain, acknowledge limitations and suggest where to find official information."
            )
        }
        messages.append(system_message)
        
        # Add policy data context if available
        if policy_data:
            policy_context = {
                "role": "system",
                "content": f"Policy information: {policy_data}"
            }
            messages.append(policy_context)
        
        # Add chat history if available
        if chat_history:
            messages.extend(chat_history)
        
        # Add the current user query
        messages.append({"role": "user", "content": user_query})
        
        # Get response from the policy expert model
        return await self.get_completion(messages, model_type="policy_expert")
    
    async def process_patient_history(
        self,
        user_query: str,
        patient_history: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process and summarize patient history in response to a query.
        
        Args:
            user_query: The user's question about their medical history.
            patient_history: Patient history records from the database.
            chat_history: Optional previous conversation history.
            
        Returns:
            Dict containing the processed patient history response and metadata.
        """
        messages = []
        
        # Add system message with instructions for the patient history model
        system_message = {
            "role": "system",
            "content": (
                "You are a healthcare AI assistant specialized in managing and explaining patient medical history. "
                "Summarize and explain medical records clearly and accurately. "
                "Maintain strict confidentiality and privacy of patient information. "
                "Do not make diagnostic conclusions from the history alone."
            )
        }
        messages.append(system_message)
        
        # Add patient history context
        history_context = {
            "role": "system",
            "content": f"Patient history: {patient_history}"
        }
        messages.append(history_context)
        
        # Add chat history if available
        if chat_history:
            messages.extend(chat_history)
        
        # Add the current user query
        messages.append({"role": "user", "content": user_query})
        
        # Get response from the patient history model
        return await self.get_completion(messages, model_type="patient_history")

# Create a global instance of the AI model service
ai_model_service = AIModelService() 