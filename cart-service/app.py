from fastapi import FastAPI, APIRouter, Response, status
from pydantic import BaseModel
import redis, os

userRouter = APIRouter(prefix="/cart", tags=["Cart"])

class Item(BaseModel):
    id: int
    name: str
    priceCents: int


def get_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True,
    )


@userRouter.get("/{user_id}")
async def getUserItems(user_id: int):
    with get_redis() as r:
        items = r.lrange(f"user:{user_id}:items", 0, -1)

    return {
        "user_id": user_id,
        "items": [Item.model_validate_json(item).model_dump() for item in items],
    }

@userRouter.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def addUserItems(user_id: int, item: Item):
    with get_redis() as r:
        r.rpush(f"user:{user_id}:items", item.model_dump_json())

    return {"message": f"Item {item.id} added to user {user_id}'s cart."}

@userRouter.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteUserItem(user_id: int, item_id: int):
    with get_redis() as r:
        items = r.lrange(f"user:{user_id}:items", 0, -1)
        for item in items:
            item_data = Item.model_validate_json(item)
            if item_data.id == item_id:
                r.lrem(f"user:{user_id}:items", 1, item)
                return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

app = FastAPI()
app.include_router(userRouter)
