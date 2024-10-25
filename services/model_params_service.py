from supabase_utils import supabase_client
from models.model_params import ModelParams
import logging

def get_active_model_param() -> ModelParams:
    try:
        response = supabase_client.from_("model_params").select("*").eq("active", True).single().execute()
    
        if not response.data:
            raise Exception("Error fetching active model param: No data returned")
        
        if len(response.data) == 0:
            raise Exception("No active model param found")
        
        # Cast the data to ModelParams
        return ModelParams(**response.data)
    except Exception as e:
        logging.error(f"Error in get_active_model_param: {str(e)}")
        raise