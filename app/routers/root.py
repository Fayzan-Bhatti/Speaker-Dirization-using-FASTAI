from fastapi import APIRouter

router = APIRouter()

@router.get("/root")
async def root():
    return {"Root is Calling"}
