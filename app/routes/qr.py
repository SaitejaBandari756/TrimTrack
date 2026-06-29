import io
import base64
import qrcode
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_session
from app.services.cache_service import cache_service
from app.services.url_service import url_service
from app.utils.url_helpers import get_public_base_url

router = APIRouter()


@router.get("/qr/{short_code}", tags=["QR Code"])
async def get_qr_code(short_code: str, session: AsyncSession = Depends(get_session)):
    url, error = await url_service.get_url(session, short_code)
    if error:
        return JSONResponse(status_code=error["code"], content=error)

    cached_qr = await cache_service.get_qr(short_code)
    if cached_qr:
        img_bytes = base64.b64decode(cached_qr)
        return StreamingResponse(
            io.BytesIO(img_bytes),
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    public_base_url = get_public_base_url()
    short_url = f"{public_base_url}/{short_code}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(short_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    await cache_service.set_qr(short_code, qr_b64)

    buf.seek(0)
    return StreamingResponse(
        buf, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"}
    )
