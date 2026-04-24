alembic -x table=posts revision --autogenerate -m "posts only"
alembic -x table=users,posts revision --autogenerate -m "users and posts"
alembic revision --autogenerate -m "full schema update"

# Step by Create & run migration
alembic revision -m "add posts table"
alembic upgrade head

# Step 1: Create the Post model
from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.db import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

# Step 2: Add relationship to User model
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    posts = relationship("Post", back_populates="user")

# Step 3: Export the model
from app.models.post import Post
from app.models.user import User

__all__ = ["User", "Post"]

# Typical safe check before migration:
alembic current
alembic history
alembic upgrade head


# Step 4: Generate migration only for posts
alembic -x table=posts revision --autogenerate -m "create posts table"


# Step 5: Review the generated migration

alembic upgrade head


Yes. In a real production app, Alembic is mainly about making database changes safely, predictably, and reviewably.

Production Safety

For this project, a safe pattern looks like this:

Add the model/code change.
Generate a migration.
Review the migration file manually.
Deploy code + migration in a controlled order.
Run alembic upgrade head in the target environment.
For adding fields safely, teams usually avoid “big risky changes” in one step.

Example: adding status to posts.

Safer rollout:

Add status as nullable=True.
Deploy and migrate.
Backfill old rows.
Update app code to start writing status.
Later, make status nullable=False if needed.
That is safer than adding a required non-null column immediately, because old rows already exist.

For destructive changes, use the “expand and contract” style:

First add new columns/tables.
Let the app write to both old and new if needed.
Backfill data.
Switch reads to the new structure.
Remove old columns only in a later migration.
How Teams Benefit From Alembic

Alembic helps a large team because it makes schema changes part of normal source control, just like Python code.

Benefits:

Everyone can see exactly what changed in the database.
New developers can recreate the schema by running migrations.
Environments stay consistent: local, staging, production.
Rollbacks and upgrade history are tracked by revision IDs.
Code review can catch dangerous DB changes before deploy.
Yes, you should commit alembic/ to git.

Usually commit:

alembic/env.py
alembic/script.py.mako
alembic/versions/*.py
alembic.ini if it belongs to the repo
Do not commit:

__pycache__
generated temp files
In a team, a good rule is:

every schema change PR should include both model changes and the Alembic migration file
one logical feature/change should usually have one migration
review the migration file, not just the model diff
Should We Create Migration For Sample Data?

Sometimes yes, but not always.

Good use of data migrations:

required lookup data
default roles
system permissions
required config rows
reference records the app depends on
Not ideal for Alembic:

demo data
fake users
development-only sample posts
For development sample data, a seed script is usually better than Alembic.

Rule of thumb:

schema changes: Alembic
required production data: Alembic can be okay
fake/sample/dev data: use a seed script
Example In Your Project

If you add a posts table:

Create app/models/post.py
Add relationship in User
Generate migration:
alembic -x table=posts revision --autogenerate -m "create posts table"
Review the generated file
Apply:
alembic upgrade head
If later you want to add a field like status to posts:

Update model
status = Column(String(20), nullable=True)
Generate migration:
alembic -x table=posts revision --autogenerate -m "add status to posts"
Review that it adds only the status column
Apply:
alembic upgrade head
If you want to backfill values, you can edit the migration file and add SQL or Alembic ops inside upgrade().

Example:

op.add_column("posts", sa.Column("status", sa.String(length=20), nullable=True))
op.execute("UPDATE posts SET status = 'draft' WHERE status IS NULL")
Later, in another migration, you can make it non-null if appropriate.

Recommended Team Workflow

For a large team:

Pull latest code.
Run alembic upgrade head.
Make model changes.
Generate a migration.
Review the migration carefully.
Commit model + migration together.
Run tests.
Merge.
If two branches both create migrations, you may get multiple heads. That is normal. Then the team creates a merge migration.

Short Answer

Yes, commit alembic/ and migration files.
Use Alembic for schema changes and required production data.
Use seed scripts for fake/sample data.
For production safety, prefer small forward-only migrations and avoid risky one-step destructive changes.
If you want, I can next show you a concrete sequence in this repo:

migration 1: create posts
migration 2: add sample seed data
migration 3: add a new field to posts safely