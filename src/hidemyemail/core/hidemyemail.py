"""Hide My Email business logic and service layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Iterator

from hidemyemail.core.exceptions import AliasNotFoundError, AliasOperationError

if TYPE_CHECKING:
    from hidemyemail.core.icloud_client import ICloudClient


@dataclass
class EmailAlias:
    """Represents a Hide My Email alias."""

    anonymous_id: str
    email: str
    label: str
    note: str
    created_at: datetime
    is_active: bool
    forward_to: str
    domain: str

    @classmethod
    def from_api(cls, data: dict) -> EmailAlias:
        """Create from API response data."""
        timestamp = data.get("createTimestamp", 0)
        # Handle timestamp in milliseconds
        if timestamp > 1e12:
            timestamp = timestamp / 1000

        return cls(
            anonymous_id=data.get("anonymousId", ""),
            email=data.get("hme", ""),
            label=data.get("label", ""),
            note=data.get("note", ""),
            created_at=datetime.fromtimestamp(timestamp) if timestamp else datetime.now(),
            is_active=data.get("isActive", True),
            forward_to=data.get("forwardToEmail", ""),
            domain=data.get("domain", ""),
        )


class HideMyEmailService:
    """High-level Hide My Email operations."""

    def __init__(self, client: ICloudClient) -> None:
        self.client = client

    def list_all(self) -> Iterator[EmailAlias]:
        """List all email aliases."""
        for alias_data in self.client.hidemyemail:
            yield EmailAlias.from_api(alias_data)

    def search(self, query: str) -> Iterator[EmailAlias]:
        """
        Search aliases by label, email, or note.

        Args:
            query: Search term (case-insensitive)

        Yields:
            Matching EmailAlias objects
        """
        query_lower = query.lower()
        for alias in self.list_all():
            if (
                query_lower in alias.label.lower()
                or query_lower in alias.email.lower()
                or query_lower in alias.note.lower()
            ):
                yield alias

    def get_by_email_or_id(self, identifier: str) -> EmailAlias | None:
        """
        Find an alias by email address or anonymous ID.

        Args:
            identifier: Email address or anonymous ID

        Returns:
            The alias if found, None otherwise
        """
        for alias in self.list_all():
            if alias.email == identifier or alias.anonymous_id == identifier:
                return alias
        return None

    def create(self, label: str, note: str = "") -> EmailAlias:
        """
        Generate and reserve a new email alias.

        Args:
            label: Label for the alias (e.g., "Netflix")
            note: Optional note

        Returns:
            The created EmailAlias

        Raises:
            AliasOperationError: If creation fails
        """
        try:
            # Generate a new random email
            generated = self.client.hidemyemail.generate()
            email = generated.get("hme", "")

            if not email:
                raise AliasOperationError("Failed to generate email address")

            # Reserve it with metadata
            result = self.client.hidemyemail.reserve(
                email=email,
                label=label,
                note=note,
            )

            if not result:
                raise AliasOperationError("Failed to reserve email alias")

            return EmailAlias.from_api(result)
        except Exception as e:
            if isinstance(e, AliasOperationError):
                raise
            raise AliasOperationError(f"Failed to create alias: {e}") from e

    def update(self, anonymous_id: str, label: str, note: str) -> bool:
        """
        Update alias metadata.

        Args:
            anonymous_id: The alias identifier
            label: New label
            note: New note

        Returns:
            True if successful
        """
        try:
            result = self.client.hidemyemail.update_metadata(
                anonymous_id=anonymous_id,
                label=label,
                note=note,
            )
            return bool(result)
        except Exception:
            return False

    def deactivate(self, anonymous_id: str) -> bool:
        """
        Deactivate an alias (stop forwarding).

        Args:
            anonymous_id: The alias identifier

        Returns:
            True if successful
        """
        try:
            result = self.client.hidemyemail.deactivate(anonymous_id)
            return bool(result)
        except Exception:
            return False

    def reactivate(self, anonymous_id: str) -> bool:
        """
        Reactivate a deactivated alias.

        Args:
            anonymous_id: The alias identifier

        Returns:
            True if successful
        """
        try:
            result = self.client.hidemyemail.reactivate(anonymous_id)
            return bool(result)
        except Exception:
            return False

    def delete(self, anonymous_id: str) -> bool:
        """
        Permanently delete an alias.

        Args:
            anonymous_id: The alias identifier

        Returns:
            True if successful
        """
        try:
            result = self.client.hidemyemail.delete(anonymous_id)
            return bool(result)
        except Exception:
            return False
