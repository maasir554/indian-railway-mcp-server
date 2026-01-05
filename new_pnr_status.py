import httpx
from new_pnr_schema import PNRResponse
import os
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

PNR_API_PATH = os.getenv("NEW_PNR_API_PATH")
PNR_API_KEY_NAME = os.getenv("NEW_PNR_API_KEY_NAME")

def fetch_pnr_status(pnr_no: str) -> PNRResponse | None:
    """
    Fetch PNR status from Live API.
    
    Args:
        pnr_no: The PNR number to check (must be 10 digits)
        
    Returns:
        PNRResponse object containing the PNR status data, or None if PNR is invalid
    """
    # Validate PNR length - must be exactly 10 digits
    if len(pnr_no) != 10 or not pnr_no.isdigit():
        return None
    
    assert PNR_API_PATH is not None
    assert PNR_API_KEY_NAME is not None
    url = PNR_API_PATH
    
    with httpx.Client() as client:
        initial_response = client.get(url)
        api_key = client.cookies.get(PNR_API_KEY_NAME)

        if not api_key:
            raise ValueError("Failed to retrieve XSRF-TOKEN from cookies", initial_response)
        
        decoded_token = unquote(api_key)
        headers = {
            f'X-{PNR_API_KEY_NAME}': decoded_token,
        }
        
        body = {"pnr": pnr_no}
        
        response = client.post(url, json=body, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if API returned an error (PNR not found)
        if data.get("status") is False:
            return None
        
        return PNRResponse(**data)
