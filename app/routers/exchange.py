from typing import List, Dict, Tuple

from fastapi import APIRouter, HTTPException, Query, Depends

from ..auth import get_api_key
from ..deps import get_rates
from ..models import FxResponse

router = APIRouter(tags=["exchange"], dependencies=[Depends(get_api_key)])


def _get_rate(rates: Dict[Tuple[str, str], float], base: str, target: str) -> float:
    base = base.upper()
    target = target.upper()
    if base == target:
        return 1.0
    if (base, target) in rates:
        return rates[(base, target)]
    if ("USD", base) in rates and ("USD", target) in rates:
        return rates[("USD", target)] / rates[("USD", base)]
    raise KeyError(f"Unsupported currency pair {base}->{target}")


@router.get("/exchange", response_model=FxResponse)
def convert(
        from_: str = Query(..., alias="from", min_length=3, max_length=3, description="Three-letter currency code"),
        to: str = Query(..., min_length=3, max_length=3, description="Three-letter currency code"),
        amount: float = Query(..., ge=0),
        rates: Dict[Tuple[str, str], float] = Depends(get_rates),
):
    if not rates:
        raise HTTPException(status_code=500,
                            detail="Exchange rates dataset not loaded. Put CSV in app/data/ and restart.")
    try:
        rate = _get_rate(rates, from_, to)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    converted = round(amount * rate, 6)
    via: List[str] = ["USD"] if (from_.upper() != "USD" and to.upper() != "USD") else [from_.upper(), to.upper()]
    return FxResponse(converted=converted, rate_used=rate, via=via)
