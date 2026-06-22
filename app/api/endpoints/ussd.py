# app/api/endpoints/ussd.py
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
from app.core.limiter import limiter
from app.api.schemas import USSDRequest
from app.services.ussd.ussd_service import handle_ussd

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ussd", response_class=PlainTextResponse)
@limiter.limit("30/minute")
async def ussd_callback(request: Request, req: USSDRequest):
    """
    USSD callback endpoint.
    Pydantic schema validates: sessionId, phoneNumber (E.164 format), text length.
    Requires authentication NOT enforced here as USSD comes from telco provider.
    """
    try:
        logger.info(f"USSD request: phone={req.phoneNumber}, session={req.sessionId}")
        
        response_text = handle_ussd(
            req.sessionId,
            req.phoneNumber,
            req.text
        )
        
        logger.info(f"USSD response sent to {req.phoneNumber}")
        return response_text
    except Exception as e:
        logger.error(f"USSD processing failed: {str(e)}", exc_info=True)
        return "Error processing your request. Please try again."