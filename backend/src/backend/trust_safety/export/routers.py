from fastapi import APIRouter, Depends, Response
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.trust_safety.export.dependencies import get_data_export_manager
from src.backend.trust_safety.export.managers import DataExportManager

router = APIRouter(
    prefix="/export",
    tags=["export"]
)

@cbv(router)
class DataExportRouter:
    """CBV router for the self-service GDPR data export."""

    manager: DataExportManager = Depends(get_data_export_manager)
    user: User = Depends(get_current_user)

    @router.get(
        "/me",
        summary="exporting current user's data",
    )
    async def export_my_data(self):
        """Downloads a ZIP archive (JSON plus CSV) of the current user's library, reviews, progress, and club posts."""
        archive = await self.manager.build_export_archive(self.user)
        return Response(
            content=archive,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=user-{self.user.id}-data-export.zip",
            },
        )
