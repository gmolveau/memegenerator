"""User service — upsert users and groups from OIDC data."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Group, User


def _get_or_create_group(db: Session, name: str) -> Group:
    group = db.scalar(select(Group).where(Group.name == name))
    if group is None:
        group = Group(name=name)
        db.add(group)
    return group


def assign_role(db: Session, identifier: str, role_name: str) -> User | None:
    """Assign a role to a user looked up by sub or name. Returns None if not found."""
    from src.models import Role  # avoid circular at module level

    user = db.scalar(
        select(User).where((User.sub == identifier) | (User.name == identifier))
    )
    if user is None:
        return None

    role = db.scalar(select(Role).where(Role.name == role_name))
    if role is None:
        return None

    user.role = role
    db.commit()
    return user


def get_effective_role(user: User) -> str | None:
    """Return the user's role name, falling back to their groups' roles."""
    if user.role:
        return user.role.name
    for group in user.groups:
        if group.role:
            return group.role.name
    return None


def upsert_user(
    db: Session,
    sub: str,
    name: str,
    email: str,
    group_names: list[str],
) -> User:
    groups = [_get_or_create_group(db, g) for g in group_names]

    user = db.scalar(select(User).where(User.sub == sub))
    if user is None:
        user = User(sub=sub, name=name, email=email, groups=groups)
        db.add(user)
    else:
        user.name = name
        user.email = email
        user.groups = groups

    db.commit()
    return user
