from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from edgepulse.app.database.session import get_db
from edgepulse.app.models.alert import AlertResponse
from edgepulse.app.services.alert_exceptions import (
    AlertNotFoundError,
)
from edgepulse.app.services.alert_service import AlertService


router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
)


@router.get(
    "",
    response_model=list[AlertResponse],
)
def list_alerts(
    acknowledged: bool | None = Query(default=None),
    database: Session = Depends(get_db),
) -> list[AlertResponse]:
    alerts = AlertService.list_alerts(
        database=database,
        acknowledged=acknowledged,
    )

    return [
        AlertResponse.model_validate(alert)
        for alert in alerts
    ]


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
def get_alert(
    alert_id: str,
    database: Session = Depends(get_db),
) -> AlertResponse:
    try:
        alert = AlertService.get_alert(
            database=database,
            alert_id=alert_id,
        )

        return AlertResponse.model_validate(alert)

    except AlertNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
)
def acknowledge_alert(
    alert_id: str,
    database: Session = Depends(get_db),
) -> AlertResponse:
    try:
        alert = AlertService.acknowledge_alert(
            database=database,
            alert_id=alert_id,
        )

        return AlertResponse.model_validate(alert)

    except AlertNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error