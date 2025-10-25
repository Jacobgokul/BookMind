from fastapi import APIRouter, UploadFile, status
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/genric",
    tags=["Genric"]
)


@router.post("/upload_file")
async def upload_file_api(
    file: UploadFile
):
    print(file.content_type)
    if file.content_type == "text/plain":
        return file.file.read()
    elif file.content_type == "application/pdf":
        return JSONResponse(
            content="Developement inprogress",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    else:
        return JSONResponse(
            status_code= status.HTTP_412_PRECONDITION_FAILED,
            content="Sorry! Upload only text files."
        )