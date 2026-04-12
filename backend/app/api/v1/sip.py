"""
SIP Calculator API.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.sip import (
    SipCompareRequest,
    SipCompareResponse,
    SipRequest,
    SipResponse,
)
from app.services.sip_calculator import (
    calculate_sip_projections,
    compare_sip_scenarios,
)

router = APIRouter(prefix="/sip", tags=["SIP Calculator"])


@router.post("/calculate", response_model=SipResponse)
async def calculate_sip(req: SipRequest):
    """Calculate SIP future value projection."""
    try:
        result = calculate_sip_projections(
            monthly_amount=req.monthly_amount,
            expected_annual_return=req.expected_annual_return,
            time_horizon_years=req.time_horizon_years,
            annual_step_up_pct=req.annual_step_up_pct,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return SipResponse(**result)


@router.post("/compare", response_model=SipCompareResponse)
async def compare_sip(req: SipCompareRequest):
    """Compare SIP outcomes across different return scenarios."""
    try:
        results = compare_sip_scenarios(
            monthly_amount=req.monthly_amount,
            time_horizon_years=req.time_horizon_years,
            return_scenarios=req.return_scenarios,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return SipCompareResponse(scenarios=[SipResponse(**r) for r in results])
