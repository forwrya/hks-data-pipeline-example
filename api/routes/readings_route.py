from fastapi import APIRouter

async def read_root():
    return "Hello World"

router = APIRouter()
router.add_api_route("/", read_root, methods=["GET"])