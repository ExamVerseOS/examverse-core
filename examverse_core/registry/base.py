"""Generic thread-safe registry for ExamVerseOS named components.

The :class:`Registry` is a generic key → instance store used as the
foundation for specialised registries (providers, validators, commands, etc.).

Example:
    >>> reg: Registry[str, MyHandler] = Registry(name="handlers")
    >>> reg.register("send_email", EmailHandler())
    >>> handler = reg.get("send_email")
"""

from __future__ import annotations

import threading
from typing import Generic, Hashable, Iterator, TypeVar

KT = TypeVar("KT", bound=Hashable)
VT = TypeVar("VT")


class DuplicateKeyError(KeyError):
    """Raised when a key is registered twice without ``overwrite=True``.

    Args:
        key: The duplicate key.
        registry_name: The name of the registry where the collision occurred.
    """

    def __init__(self, key: object, registry_name: str) -> None:
        super().__init__(f"Key {key!r} is already registered in registry {registry_name!r}.")
        self.key = key
        self.registry_name = registry_name


class Registry(Generic[KT, VT]):
    """Generic thread-safe key→value registry.

    Args:
        name: Human-readable name for error messages and debugging.
    """

    def __init__(self, name: str = "registry") -> None:
        """Initialise an empty registry.

        Args:
            name: The registry's display name.
        """
        self._name = name
        self._store: dict[KT, VT] = {}
        self._lock = threading.RLock()

    def register(self, key: KT, value: VT, *, overwrite: bool = False) -> None:
        """Register a key→value pair.

        Args:
            key: The registration key.
            value: The value to store.
            overwrite: When ``False`` (default), raises :class:`DuplicateKeyError`
                if the key is already registered.

        Raises:
            DuplicateKeyError: If ``key`` is already registered and
                ``overwrite=False``.
        """
        with self._lock:
            if not overwrite and key in self._store:
                raise DuplicateKeyError(key, self._name)
            self._store[key] = value

    def get(self, key: KT) -> VT | None:
        """Retrieve a value by key.

        Args:
            key: The registration key to look up.

        Returns:
            The registered value, or ``None`` if not found.
        """
        return self._store.get(key)

    def require(self, key: KT) -> VT:
        """Retrieve a value by key, raising if not found.

        Args:
            key: The registration key to look up.

        Returns:
            The registered value.

        Raises:
            KeyError: If the key is not registered.
        """
        value = self._store.get(key)
        if value is None:
            raise KeyError(
                f"Key {key!r} is not registered in registry {self._name!r}."
            )
        return value

    def unregister(self, key: KT) -> bool:
        """Remove a registration.

        Args:
            key: The key to remove.

        Returns:
            ``True`` if the key was found and removed, ``False`` otherwise.
        """
        with self._lock:
            return self._store.pop(key, None) is not None

    def keys(self) -> list[KT]:
        """Return all registered keys.

        Returns:
            Sorted-by-repr list of registered keys.
        """
        return list(self._store)

    def values(self) -> list[VT]:
        """Return all registered values.

        Returns:
            List of registered values in insertion order.
        """
        return list(self._store.values())

    def __len__(self) -> int:
        """Return the number of registered entries.

        Returns:
            Integer count.
        """
        return len(self._store)

    def __contains__(self, key: object) -> bool:
        """Check whether a key is registered.

        Args:
            key: The key to check.

        Returns:
            ``True`` if registered.
        """
        return key in self._store

    def __iter__(self) -> Iterator[KT]:
        """Iterate over registered keys.

        Yields:
            Each registered key.
        """
        yield from self._store

    def clear(self) -> None:
        """Remove all registrations."""
        with self._lock:
            self._store.clear()

    def __repr__(self) -> str:
        """Return a developer-friendly representation.

        Returns:
            String with registry name and entry count.
        """
        return f"<Registry name={self._name!r} entries={len(self._store)}>"
