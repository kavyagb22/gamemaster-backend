from fastapi import FastAPI, Depends, HTTPException, status
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from models.game import Game
from models.group import Group
from models.request import SigninRequest, SignupRequest, AddGameRequest, DeleteGameRequest, UpdateGameRequest, CreateGroupRequest, ConvertUserRequest, UpdateGroupRequest, DeleteGroupRequest, JoinGroupRequest
from helpers.security import hash_password, verify_password, get_current_user_username, create_access_token
from sqlalchemy.orm import selectinload
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
                'id': user.id,
                'usertype': user.usertype
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
        'token': token,
        "data": {
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'username': user.username,
            'createdAt': user.created_at,
            'id': user.id,
            'usertype': user.usertype
        }
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


@app.get('/games/get')
async def get_games(username: str = Depends(get_current_user_username),
                    db: AsyncSession = Depends(get_db)):
    try:
        query = select(Game).where(Game.owner_username == username)
        result = await db.execute(query)
        games = result.scalars().all()
        return {
            "status": status.HTTP_200_OK,
            "data": {
                'owner': username,
                'games': games
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/games/add')
async def add_game(payload: AddGameRequest,
                   db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User).where(User.username == payload.owner))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid owner found for usernames provided.")
        existing_game_query = await db.execute(
            select(Game).where(Game.name.ilike(payload.name.strip()),
                               Game.owner_username == user.username))
        if existing_game_query.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=
                f"A game named '{payload.name}' already exists in {payload.owner}'s library."
            )

        new_game = Game(name=payload.name,
                        min_players=payload.min_players,
                        max_players=payload.max_players,
                        optimal_players=payload.optimal_players,
                        last_played=payload.last_played,
                        gametype=payload.gametype,
                        personal_rating=payload.personal_rating,
                        group_rating=payload.group_rating,
                        comments=payload.comments,
                        playtime=payload.playtime,
                        complexity=payload.complexity,
                        owner=user)
        db.add(new_game)

        # update library too in group
        groups_query = await db.execute(
            select(Group).where(Group.host == user.username).options(
                selectinload(Group.library)))
        hosted_groups = groups_query.scalars().all()

        for group in hosted_groups:
            group.library.append(new_game)

        await db.commit()
        await db.refresh(new_game)
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Game added",
            "data": new_game
        }
    except HTTPException:

        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.post('/games/delete')
async def delete_game(game: DeleteGameRequest,
                      db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Game).where(Game.id == game.game_id))
        game = result.scalar_one_or_none()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Game not found")
        await db.delete(game)
        await db.commit()
        return {
            "message": "Game deleted successfully",
            'status': status.HTTP_200_OK
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.put('/games/update')
async def update_game(payload: UpdateGameRequest,
                      db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Game).where(Game.id == payload.game_id))
        game = result.scalar_one_or_none()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Game not found")
        update_data = payload.model_dump(exclude={"game_id"},
                                         exclude_unset=True)
        for key, value in update_data.items():
            setattr(game, key, value)

        await db.commit()
        await db.refresh(game)
        return {
            "status": status.HTTP_200_OK,
            "message": "Game updated",
            "data": game
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.post('/groups/create')
async def create_group(payload: CreateGroupRequest,
                       db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User).where(User.username == payload.host))
        host = result.scalar_one_or_none()
        if not host:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid user found for username provided.")
        existing_group_query = await db.execute(
            select(Group).where(Group.invite_code == payload.invite_code))
        if existing_group_query.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=
                f"A group with the same invite code '{payload.invite_code}' already exists."
            )
        existing_library = await db.execute(
            select(Game).where(Game.owner_username == host.username))
        host_games = existing_library.scalars().all()
        new_group = Group(name=payload.name,
                          desc=payload.desc,
                          invite_code=payload.invite_code,
                          preferred_location=payload.preferred_location,
                          schedule=payload.schedule,
                          gametype=payload.gametype,
                          last_played=payload.last_played,
                          host=host.username,
                          members=[host],
                          library=host_games)
        db.add(new_group)
        await db.commit()
        await db.refresh(new_group, attribute_names=['members', 'library'])
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Group created",
            "data": new_group
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.get('/groups/get')
async def get_groups(username: str = Depends(get_current_user_username),
                     db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Group).where(
                Group.members.any(User.username == username)).options(
                    selectinload(Group.members), selectinload(Group.library)))
        groups = result.scalars().all()
        return {"status": status.HTTP_200_OK, "data": {'groups': groups}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put('/groups/update')
async def update_group(payload: UpdateGroupRequest,
                       db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Group).where(Group.id == payload.group_id))
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Group not found")
        update_data = payload.model_dump(exclude={"group_id"},
                                         exclude_unset=True)
        for key, value in update_data.items():
            setattr(group, key, value)

        await db.commit()
        await db.refresh(group)
        return {
            "status": status.HTTP_200_OK,
            "message": "Group updated",
            "data": group
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.post('/groups/delete')
async def delete_group(group: DeleteGroupRequest,
                       db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Group).where(Group.id == group.group_id))
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Group not found")
        await db.delete(group)
        await db.commit()
        return {
            "message": "Group deleted successfully",
            'status': status.HTTP_200_OK
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.post('/groups/join')
async def join_group(payload: JoinGroupRequest,
                     db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User).where(User.username == payload.username))
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid user found for username provided.")
        group_result = await db.execute(
            select(Group).options(selectinload(Group.members)).where(
                Group.invite_code == payload.invite_code,
                Group.name == payload.group_name))
        group = group_result.scalar_one_or_none()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid group found for the code and name provided")
        if member in group.members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this group.")
        group.members.append(member)
        await db.commit()
        await db.refresh(group)
        return {"status": status.HTTP_201_CREATED, "message": "Group joined!"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.post('/user/convert-type')
async def convert_usertype(payload: ConvertUserRequest,
                           db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User).where(User.username == payload.username))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid user found for username provided.")
        if user.usertype == 'host':
            user.usertype = 'player'
        elif user.usertype == 'player':
            user.usertype = 'host'
        await db.commit()
        await db.refresh(user)
        return {
            "status": status.HTTP_200_OK,
            "message": "Usertype converted",
            "data": user
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
