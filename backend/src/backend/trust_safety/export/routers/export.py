from fastapi import APIRouter, Depends, Response, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.trust_safety.export.dependencies.export import get_data_export_manager
from src.backend.trust_safety.export.managers.export import DataExportManager
from src.backend.core.responses import error_responses

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
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
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
