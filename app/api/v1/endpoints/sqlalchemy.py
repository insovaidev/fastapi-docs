from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, Integer, func, select, text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
    sessionmaker,
)
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


router = APIRouter(prefix="/sqlalchemy", tags=["SQLAlchemy Mastery"])


class LearningBase(DeclarativeBase):
    pass


class DemoUser(LearningBase):
    __tablename__ = "demo_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    level: Mapped[str] = mapped_column(default="junior")
    points: Mapped[int] = mapped_column(default=0)

    posts: Mapped[list["DemoPost"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )


class DemoPost(LearningBase):
    __tablename__ = "demo_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str]
    body: Mapped[str]
    published: Mapped[bool] = mapped_column(default=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("demo_users.id"))

    author: Mapped[DemoUser] = relationship(back_populates="posts")


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
LearningBase.metadata.create_all(engine)


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    level: str = Field(default="junior", min_length=2, max_length=20)
    points: int = Field(default=0, ge=0, le=1000)


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    level: str
    points: int

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    body: str = Field(..., min_length=10, max_length=500)
    published: bool = False


class PostRead(BaseModel):
    id: int
    title: str
    body: str
    published: bool
    author_id: int

    model_config = ConfigDict(from_attributes=True)


class UserWithPostsRead(UserRead):
    posts: list[PostRead] = Field(default_factory=list)


class PointsTransfer(BaseModel):
    from_user_id: int = Field(..., gt=0)
    to_user_id: int = Field(..., gt=0)
    points: int = Field(..., gt=0, le=100)


def get_session():
    ensure_seed_data()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_seed_data() -> None:
    with SessionLocal() as db:
        has_users = db.scalar(select(func.count()).select_from(DemoUser))
        if has_users:
            return

        users = [
            DemoUser(name="Ada", email="ada@example.com", level="senior", points=120),
            DemoUser(name="Linus", email="linus@example.com", level="staff", points=180),
            DemoUser(name="Grace", email="grace@example.com", level="mid", points=90),
        ]
        db.add_all(users)
        db.flush()

        db.add_all(
            [
                DemoPost(
                    title="ORM Basics",
                    body="Learn how models map Python objects to relational tables.",
                    published=True,
                    author_id=users[0].id,
                ),
                DemoPost(
                    title="Raw SQL Escape Hatch",
                    body="Sometimes text queries are the right tool for reporting or migration work.",
                    published=False,
                    author_id=users[0].id,
                ),
                DemoPost(
                    title="Mixing ORM and SQL",
                    body="You can combine raw SQL and ORM as long as the boundaries stay clear.",
                    published=True,
                    author_id=users[1].id,
                ),
            ]
        )
        db.commit()


def get_user_or_404(db: Session, user_id: int) -> DemoUser:
    user = db.get(DemoUser, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Demo user not found")
    return user


@router.get("/", summary="Guide to the SQLAlchemy learning playground")
def get_sqlalchemy_guide():
    # Request setup: GET /sqlalchemy/
    # Learn this: start with a map of topics so you can explore ORM, raw SQL, and hybrid patterns step by step.
    return {
        "message": "This module uses a separate in-memory SQLite database just for learning SQLAlchemy.",
        "topics": [
            "ORM models and sessions",
            "relationships",
            "filtering and pagination",
            "eager loading",
            "raw SQL with text()",
            "mixing raw SQL with ORM",
            "transactions and rollbacks",
            "aggregations and group by",
        ],
        "try_in_docs": [
            "/sqlalchemy/reset",
            "/sqlalchemy/orm/users",
            "/sqlalchemy/orm/users/1",
            "/sqlalchemy/orm/users/1/posts",
            "/sqlalchemy/raw/users",
            "/sqlalchemy/raw/stats",
            "/sqlalchemy/hybrid/users/1/promote",
            "/sqlalchemy/hybrid/search?keyword=ORM",
            "/sqlalchemy/transactions/transfer-points",
            "/sqlalchemy/aggregates/top-authors",
        ],
    }


@router.post("/reset", summary="Reset the in-memory learning database")
def reset_memory_database():
    # Request setup: POST /sqlalchemy/reset
    # Learn this: in-memory databases are great for demos because you can rebuild state quickly and safely.
    LearningBase.metadata.drop_all(engine)
    LearningBase.metadata.create_all(engine)
    ensure_seed_data()
    return {"message": "In-memory SQLAlchemy database has been reset with seed data."}


@router.get("/orm/users", response_model=list[UserRead], summary="List users with ORM queries")
def list_users(
    db: Annotated[Session, Depends(get_session)],
    level: Annotated[str | None, Query(min_length=2, max_length=20)] = None,
    min_points: Annotated[int, Query(ge=0)] = 0,
):
    # Request setup: GET /sqlalchemy/orm/users?level=senior&min_points=50
    # Learn this: ORM queries are ideal for typed filters, composable conditions, and model-based results.
    stmt = select(DemoUser).where(DemoUser.points >= min_points).order_by(DemoUser.id)
    if level:
        stmt = stmt.where(DemoUser.level == level)
    return db.scalars(stmt).all()


@router.post(
    "/orm/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user with ORM insert",
)
def create_user(payload: UserCreate, db: Annotated[Session, Depends(get_session)]):
    # Request setup: POST /sqlalchemy/orm/users with JSON {"name":"Taylor","email":"taylor@example.com","level":"junior","points":25}
    # Learn this: ORM insert flow usually means create model instance, add it to the session, commit, then refresh.
    existing = db.scalar(select(DemoUser).where(DemoUser.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already exists in the demo database")

    user = DemoUser(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/orm/users/{user_id}", response_model=UserRead, summary="Read one ORM entity by primary key")
def read_user(user_id: int, db: Annotated[Session, Depends(get_session)]):
    # Request setup: GET /sqlalchemy/orm/users/1
    # Learn this: Session.get() is the cleanest ORM lookup when you already know the primary key.
    return get_user_or_404(db, user_id)


@router.post(
    "/orm/users/{user_id}/posts",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a related record through the ORM",
)
def create_post_for_user(
    user_id: int,
    payload: PostCreate,
    db: Annotated[Session, Depends(get_session)],
):
    # Request setup: POST /sqlalchemy/orm/users/1/posts with JSON {"title":"Joins","body":"Practice one-to-many relationships in SQLAlchemy.","published":true}
    # Learn this: relationships stay readable when you create child rows with foreign keys through mapped models.
    user = get_user_or_404(db, user_id)
    post = DemoPost(**payload.model_dump(), author_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get(
    "/orm/users/{user_id}/with-posts",
    response_model=UserWithPostsRead,
    summary="Load one user with related posts",
)
def read_user_with_posts(user_id: int, db: Annotated[Session, Depends(get_session)]):
    # Request setup: GET /sqlalchemy/orm/users/1/with-posts
    # Learn this: selectinload() solves the common N+1 relationship problem when you know related rows will be needed.
    stmt = (
        select(DemoUser)
        .options(selectinload(DemoUser.posts))
        .where(DemoUser.id == user_id)
    )
    user = db.scalar(stmt)
    if user is None:
        raise HTTPException(status_code=404, detail="Demo user not found")
    return user


@router.get("/raw/users", summary="Read rows using raw SQL")
def list_users_with_raw_sql(db: Annotated[Session, Depends(get_session)]):
    # Request setup: GET /sqlalchemy/raw/users
    # Learn this: raw SQL is useful when you want exact control over the query text or need database-specific features.
    rows = db.execute(
        text(
            """
            SELECT id, name, email, level, points
            FROM demo_users
            ORDER BY points DESC, id ASC
            """
        )
    ).mappings()
    return {"items": [dict(row) for row in rows]}


@router.get("/raw/stats", summary="Use raw SQL for reporting queries")
def get_raw_stats(db: Annotated[Session, Depends(get_session)]):
    # Request setup: GET /sqlalchemy/raw/stats
    # Learn this: reporting queries often become easier to express and review when written directly in SQL.
    row = db.execute(
        text(
            """
            SELECT
                COUNT(*) AS total_users,
                COALESCE(SUM(points), 0) AS total_points,
                COALESCE(AVG(points), 0) AS average_points
            FROM demo_users
            """
        )
    ).mappings().one()
    return dict(row)


@router.patch("/hybrid/users/{user_id}/promote", summary="Mix raw SQL updates with ORM reads")
def promote_user_hybrid(
    user_id: int,
    db: Annotated[Session, Depends(get_session)],
    level: Annotated[str, Query(min_length=2, max_length=20)] = "senior",
):
    # Request setup: PATCH /sqlalchemy/hybrid/users/1/promote?level=staff
    # Learn this: sometimes you use raw SQL for a precise update, then switch back to ORM for model-friendly responses.
    result = db.execute(
        text("UPDATE demo_users SET level = :level, points = points + 10 WHERE id = :user_id"),
        {"level": level, "user_id": user_id},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Demo user not found")
    db.commit()

    user = get_user_or_404(db, user_id)
    return {
        "message": "User promoted with a raw SQL update and loaded back with the ORM.",
        "user": UserRead.model_validate(user),
    }


@router.get("/hybrid/search", summary="Combine raw SQL discovery with ORM hydration")
def hybrid_search(
    keyword: Annotated[str, Query(min_length=2, max_length=30)],
    db: Annotated[Session, Depends(get_session)],
):
    # Request setup: GET /sqlalchemy/hybrid/search?keyword=ORM
    # Learn this: one practical hybrid pattern is using raw SQL to find ids, then ORM loading for relationships and serialization.
    rows = db.execute(
        text(
            """
            SELECT DISTINCT author_id
            FROM demo_posts
            WHERE lower(title) LIKE lower(:keyword)
               OR lower(body) LIKE lower(:keyword)
            """
        ),
        {"keyword": f"%{keyword}%"},
    ).mappings()
    author_ids = [row["author_id"] for row in rows]

    if not author_ids:
        return {"keyword": keyword, "items": []}

    stmt = (
        select(DemoUser)
        .options(selectinload(DemoUser.posts))
        .where(DemoUser.id.in_(author_ids))
        .order_by(DemoUser.id)
    )
    users = db.scalars(stmt).all()
    return {
        "keyword": keyword,
        "matched_author_ids": author_ids,
        "items": [UserWithPostsRead.model_validate(user) for user in users],
    }


@router.post("/transactions/transfer-points", summary="Run multiple ORM changes in one transaction")
def transfer_points(payload: PointsTransfer, db: Annotated[Session, Depends(get_session)]):
    # Request setup: POST /sqlalchemy/transactions/transfer-points with JSON {"from_user_id":1,"to_user_id":2,"points":15}
    # Learn this: transactions keep related updates atomic so either all changes commit or none of them do.
    sender = get_user_or_404(db, payload.from_user_id)
    receiver = get_user_or_404(db, payload.to_user_id)

    if sender.id == receiver.id:
        raise HTTPException(status_code=400, detail="Cannot transfer points to the same user")
    if sender.points < payload.points:
        raise HTTPException(status_code=400, detail="Sender does not have enough points")

    try:
        sender.points -= payload.points
        receiver.points += payload.points
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(sender)
    db.refresh(receiver)
    return {
        "message": "Points transferred successfully",
        "from_user": UserRead.model_validate(sender),
        "to_user": UserRead.model_validate(receiver),
    }


@router.get("/aggregates/top-authors", summary="Aggregate with ORM functions and group by")
def get_top_authors(db: Annotated[Session, Depends(get_session)]):
    # Request setup: GET /sqlalchemy/aggregates/top-authors
    # Learn this: SQLAlchemy ORM can still express reporting queries with joins, count(), group_by(), and labeled columns.
    stmt = (
        select(
            DemoUser.id,
            DemoUser.name,
            func.count(DemoPost.id).label("post_count"),
            func.sum(func.cast(DemoPost.published, Integer)).label("published_count"),
        )
        .outerjoin(DemoPost, DemoPost.author_id == DemoUser.id)
        .group_by(DemoUser.id, DemoUser.name)
        .order_by(text("post_count DESC"), DemoUser.id.asc())
    )
    rows = db.execute(stmt).mappings().all()
    return {"items": [dict(row) for row in rows]}
