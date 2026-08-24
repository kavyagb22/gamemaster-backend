from fastapi import FastAPI, Depends, HTTPException, status
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from models.request import SigninRequest, SignupRequest
from helpers.security import hash_password, verify_password, get_current_user_username, create_access_token

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gamemaster API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def test():
    return {"Gamemaster backend operational"}


@app.get('/test-db')
async def test_user_table(db: AsyncSession = Depends(get_db)):
    try:
        query = select(User)
        result = await db.execute(query)
        print('results: ', result)
        users = result.scalars().all()
        return {"status": "success", "data": users}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/auth/user')
async def get_user(username: str = Depends(get_current_user_username),
                   db: AsyncSession = Depends(get_db)):
    try:
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User '{username}' not found")
        return {
            "status": status.HTTP_200_OK,
            "data": {
                'firstname': user.firstname,
                'lastname': user.lastname,
                'email': user.email,
                'username': user.username,
                'createdAt': user.created_at,
                'id': user.id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/auth/signin')
async def signin_user(payload: SigninRequest,
                      db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == payload.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")

    token = create_access_token(payload.username)
    return {
        "status": status.HTTP_200_OK,
        "message": "Logged in",
        'token': token
    }


@app.post('/auth/signup')
async def signup_user(payload: SignupRequest,
                      db: AsyncSession = Depends(get_db)):
    try:
        existing_user = select(User).where(User.username == payload.username)
        result = await db.execute(existing_user)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Username already exists!")
        hashed_password = hash_password(payload.password)
        new_user = User(firstname=payload.firstname,
                        lastname=payload.lastname,
                        email=payload.email,
                        password_hash=hashed_password,
                        username=payload.username)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        token = create_access_token(new_user.username)
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User created",
            'token': token,
            "data": new_user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
