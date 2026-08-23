from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from src.backend.core.models import Base
from src.backend.identity.auth.models import User, Session
from src.backend.identity.profile.models import Profile
from src.backend.identity.blocked_users.models import BlockedUser
from src.backend.identity.follow.models import Follow
from src.backend.catalog.books.models import Work, Edition, Genre
from src.backend.catalog.librarian.models import LibrarianSubmission
from src.backend.library.reading_goals.models import ReadingGoal
from src.backend.library.shelf.models import Shelf, ShelfItem
from src.backend.library.progress.models import ProgressLog, ReadingPeriod
from src.backend.library.reviews.models import Review
from src.backend.clubs.clubs.models import Club, ClubGenre
from src.backend.clubs.club_membership.models import ClubMembership
from src.backend.clubs.reading_session.models import ReadingSession
from src.backend.clubs.thread.models import Thread
from src.backend.clubs.voting.models import VotingPoll, PollVote, PollCandidate
from src.backend.clubs.events.models import ClubEvent, EventRSVP
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.trust_safety.consent.models import ConsentRecords, LegalDocument
from src.backend.notifications.models import Notification, NotificationPreference
from src.backend.administration.announcements.models import Announcement
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
