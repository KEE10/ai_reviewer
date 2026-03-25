import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, DefaultDict, List, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

EventHandler = Callable[[T], Awaitable[None]]

PR_CREATED = "pr.created"
PR_REVIEWED = "pr.reviewed"


@dataclass(frozen=True)
class Event:
    """Base event type for event bus messages."""

    name: str
    payload: Any = None


class EventBus:
    """In-memory async event bus.

    Handlers are registered per-event name. Emitting an event fires all handlers
    concurrently and waits for them to complete.
    """

    def __init__(self) -> None:
        self._handlers: DefaultDict[str, List[EventHandler[Any]]] = defaultdict(list)

    async def subscribe(self, event_name: str, handler: EventHandler[Any]) -> None:
        """Register an async handler for an event name."""
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    async def unsubscribe(self, event_name: str, handler: EventHandler[Any]) -> None:
        """Unregister a handler from an event name."""
        handlers = self._handlers.get(event_name)
        if handlers and handler in handlers:
            handlers.remove(handler)
            if not handlers:
                self._handlers.pop(event_name, None)

    async def emit(self, event: Event) -> None:
        """Publish an event to all subscribed handlers."""
        handlers = list(self._handlers.get(event.name, []))

        if not handlers:
            return

        results = await asyncio.gather(
            *(handler(event.payload) for handler in handlers),
            return_exceptions=True,
        )

        for handler, result in zip(handlers, results):
            if isinstance(result, Exception):
                logger.exception(
                    "Event handler failed: %s (event=%s)",
                    handler,
                    event.name,
                    exc_info=result,
                )


bus = EventBus()


async def subscribe(event_name: str, handler: EventHandler[Any]) -> None:
    """Shortcut to subscribe to an event."""
    await bus.subscribe(event_name, handler)


async def unsubscribe(event_name: str, handler: EventHandler[Any]) -> None:
    """Shortcut to unsubscribe from an event."""
    await bus.unsubscribe(event_name, handler)


async def emit(event_name: str, payload: Any = None) -> None:
    """Shortcut to emit an event."""
    await bus.emit(Event(name=event_name, payload=payload))
