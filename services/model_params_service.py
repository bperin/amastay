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


def get_all_model_params() -> list[ModelParams]:
    """
    Retrieves all model parameter configurations from the database

    Returns:
        list[ModelParams]: List of all model parameter configurations
    """
    try:
        response = supabase_client.from_("model_params").select("*").execute()

        if not response.data:
            return []

        return [ModelParams(**param) for param in response.data]

    except Exception as e:
        logging.error(f"Error in get_all_model_params: {str(e)}")
        raise
