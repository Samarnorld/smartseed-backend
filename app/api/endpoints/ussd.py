# app/api/endpoints/ussd.py
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from app.services.ussd.ussd_service import handle_ussd

router = APIRouter()

@router.post("/ussd", response_class=PlainTextResponse)
async def ussd_callback(request: Request):
    form = await request.form()
    session_id = form.get("sessionId")
    phone_number = form.get("phoneNumber")
    text = form.get("text", "")

    response_text = handle_ussd(session_id, phone_number, text)

    return response_text