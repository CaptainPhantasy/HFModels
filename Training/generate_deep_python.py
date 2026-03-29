#!/usr/bin/env python3
"""
Deep Python patterns generator.
Produces advanced Python examples: async, dataclass, typing, decorators, generators, etc.
"""
import json


SYSTEM_PROMPTS = [
    "You are a Python expert. Write idiomatic, performant Python using modern patterns.",
    "You are a Python core developer. Write code that leverages the full power of Python.",
    "You are a Python architect. Design clean, maintainable, type-safe systems.",
]


def async_examples():
    """Generate async/await examples."""
    return [
        {
            "system": SYSTEM_PROMPTS[0],
            "user": "Implement an async context manager for database connection pooling.",
            "assistant": '''import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator
import asyncpg


class ConnectionPool:
    """Async PostgreSQL connection pool with context manager support."""
    
    def __init__(
        self,
        dsn: str,
        min_size: int = 5,
        max_size: int = 20,
        command_timeout: float = 60.0,
    ) -> None:
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._command_timeout = command_timeout
        self._pool: asyncpg.Pool | None = None
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the connection pool."""
        async with self._lock:
            if self._pool is None:
                self._pool = await asyncpg.create_pool(
                    self._dsn,
                    min_size=self._min_size,
                    max_size=self._max_size,
                    command_timeout=self._command_timeout,
                )
    
    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
        """Acquire a connection from the pool."""
        if self._pool is None:
            await self.initialize()
        async with self._pool.acquire() as conn:
            yield conn
    
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[asyncpg.Transaction]:
        """Execute within a transaction."""
        async with self.acquire() as conn:
            async with conn.transaction():
                yield conn
    
    async def close(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            if self._pool is not None:
                await self._pool.close()
                self._pool = None
    
    async def __aenter__(self) -> "ConnectionPool":
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


# Usage
async def main():
    pool = ConnectionPool("postgresql://user:pass@localhost/db")
    async with pool:
        async with pool.transaction() as conn:
            result = await conn.fetchrow(
                "SELECT id, name FROM users WHERE active = true"
            )
            print(result)


if __name__ == "__main__":
    asyncio.run(main())'''
        },
        {
            "system": SYSTEM_PROMPTS[0],
            "user": "Create an async iterator for processing streaming data with backpressure.",
            "assistant": '''import asyncio
from typing import AsyncIterator, TypeVar
from collections.abc import AsyncGenerator

T = TypeVar("T")


class AsyncBatcher(AsyncIterator[T]):
    """Async iterator that batches items for efficient processing."""
    
    def __init__(
        self,
        source: AsyncIterator[T],
        batch_size: int = 100,
        batch_timeout: float = 1.0,
    ) -> None:
        self._source = source
        self._batch_size = batch_size
        self._batch_timeout = batch_timeout
        self._buffer: list[T] = []
        self._queue: asyncio.Queue[list[T] | None] = asyncio.Queue(maxsize=10)
    
    async def _producer(self) -> None:
        """Pull from source and batch items."""
        try:
            while True:
                try:
                    # Wait for item with timeout
                    item = await asyncio.wait_for(
                        self._source.__anext__(),
                        timeout=self._batch_timeout,
                    )
                    self._buffer.append(item)
                    
                    if len(self._buffer) >= self._batch_size:
                        await self._queue.put(self._buffer)
                        self._buffer = []
                        
                except asyncio.TimeoutError:
                    if self._buffer:
                        await self._queue.put(self._buffer)
                        self._buffer = []
                        
        except StopAsyncIteration:
            if self._buffer:
                await self._queue.put(self._buffer)
        finally:
            await self._queue.put(None)  # Signal end
    
    async def __anext__(self) -> list[T]:
        """Return next batch."""
        value = await self._queue.get()
        if value is None:
            raise StopAsyncIteration
        return value
    
    async def collect(self) -> list[T]:
        """Collect all items into a list."""
        results = []
        async for batch in self:
            results.extend(batch)
        return results


async def stream_users() -> AsyncIterator[dict]:
    """Example: stream users from a database."""
    for i in range(1000):
        yield {"id": i, "name": f"User {i}"}
        await asyncio.sleep(0.01)


async def main():
    async def process_batch(users: list[dict]) -> None:
        # Process batch (e.g., bulk insert)
        print(f"Processing batch of {len(users)} users")
    
    # Stream and process in batches
    async for batch in AsyncBatcher(stream_users(), batch_size=50):
        await process_batch(batch)'''
        },
        {
            "system": SYSTEM_PROMPTS[0],
            "user": "Implement async task groups with cancellation and error handling.",
            "assistant": '''import asyncio
from typing import TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class TaskResult(Generic[T]):
    task_id: str
    success: bool
    result: T | None = None
    error: Exception | None = None


class TaskRunner:
    """Manages concurrent async tasks with cancellation support."""
    
    def __init__(self, max_concurrent: int = 10) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._tasks: set[asyncio.Task] = set()
        self._results: dict[str, TaskResult] = {}
    
    async def run(
        self,
        tasks: dict[str, callable],
    ) -> dict[str, TaskResult]:
        """Run tasks concurrently with controlled parallelism."""
        async with asyncio.TaskGroup() as tg:
            for task_id, coro_fn in tasks.items():
                task = tg.create_task(self._run_task(task_id, coro_fn))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)
        
        return self._results.copy()
    
    async def _run_task(
        self,
        task_id: str,
        coro_fn: callable,
    ) -> TaskResult[T]:
        """Run a single task with semaphore control."""
        async with self._semaphore:
            try:
                result = await coro_fn()
                self._results[task_id] = TaskResult(
                    task_id=task_id,
                    success=True,
                    result=result,
                )
                return self._results[task_id]
                
            except asyncio.CancelledError:
                self._results[task_id] = TaskResult(
                    task_id=task_id,
                    success=False,
                    error=asyncio.CancelledError(),
                )
                raise
                
            except Exception as e:
                self._results[task_id] = TaskResult(
                    task_id=task_id,
                    success=False,
                    error=e,
                )
                return self._results[task_id]
    
    async def cancel_all(self) -> None:
        """Cancel all pending tasks."""
        for task in self._tasks:
            task.cancel()


# Usage
async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(0.1)  # Simulate I/O
    return {"id": user_id, "name": f"User {user_id}"}


async def main():
    tasks = {
        f"user_{i}": lambda i=i: fetch_user(i)
        for i in range(100)
    }
    
    runner = TaskRunner(max_concurrent=20)
    results = await runner.run(tasks)
    
    successful = [r for r in results.values() if r.success]
    print(f"Completed: {len(successful)}/{len(results)}")'''
        },
    ]


def dataclass_examples():
    """Generate dataclass examples."""
    return [
        {
            "system": SYSTEM_PROMPTS[1],
            "user": "Implement a dataclass with validation, slots, and frozen immutability.",
            "assistant": '''from dataclasses import dataclass, field
from typing import ClassVar
import immutabledict


@dataclass(frozen=True, slots=True)
class ImmutableUser:
    """Immutable user entity with frozen dataclass."""
    
    id: int
    email: str
    name: str
    
    _email_pattern: ClassVar = ...
    
    def __post_init__(self) -> None:
        """Validate after initialization."""
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        if len(self.name) < 1:
            raise ValueError("Name cannot be empty")
    
    def with_name(self, name: str) -> "ImmutableUser":
        """Return new instance with updated name."""
        return ImmutableUser(
            id=self.id,
            email=self.email,
            name=name,
        )


@dataclass
class Config:
    """Mutable config with defaults and factory methods."""
    
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = field(default=100, ge=1, le=10000)
    timeout: float = field(default=30.0, gt=0)
    allowed_origins: frozenset[str] = field(default_factory=frozenset)
    
    def __post_init__(self) -> None:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_levels:
            raise ValueError(f"Invalid log_level: {self.log_level}")


# Use immutabledict for nested immutable data
ConfigDict = immutabledict.immutabledict[str, int | str | bool]'''
        },
        {
            "system": SYSTEM_PROMPTS[1],
            "user": "Create a dataclass-based entity system with relationships.",
            "assistant": '''from dataclasses import dataclass, field
from typing import NewType, ClassVar
from datetime import datetime


UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)
ProductId = NewType("ProductId", int)


@dataclass
class Address:
    street: str
    city: str
    country: str
    postal_code: str
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.country}"


@dataclass
class LineItem:
    product_id: ProductId
    quantity: int
    unit_price: float
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Order:
    """Aggregate root for order domain."""
    
    id: OrderId
    user_id: UserId
    items: list[LineItem] = field(default_factory=list)
    shipping_address: Address | None = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    
    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)
    
    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
    
    def add_item(self, item: LineItem) -> None:
        """Add item, merging quantities if product exists."""
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                return
        self.items.append(item)
    
    def remove_item(self, product_id: ProductId) -> None:
        self.items = [i for i in self.items if i.product_id != product_id]'''
        },
    ]


def typing_examples():
    """Generate typing module examples."""
    return [
        {
            "system": SYSTEM_PROMPTS[2],
            "user": "Implement Protocol-based dependency injection with structural subtyping.",
            "assistant": '''from typing import Protocol, runtime_checkable
from abc import abstractmethod


@runtime_checkable
class Storage(Protocol):
    """Protocol defining storage interface."""
    
    async def save(self, key: str, value: bytes) -> None: ...
    async def load(self, key: str) -> bytes | None: ...
    async def delete(self, key: str) -> None: ...


@runtime_checkable
class Cache(Protocol):
    """Protocol defining cache interface."""
    
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl: int = 300) -> None: ...
    async def invalidate(self, key: str) -> None: ...


class RedisStorage:
    """Redis implementation of Storage."""
    
    async def save(self, key: str, value: bytes) -> None:
        await self._redis.set(key, value)
    
    async def load(self, key: str) -> bytes | None:
        return await self._redis.get(key)
    
    async def delete(self, key: str) -> None:
        await self._redis.delete(key)


class Service:
    """Service using protocol-based dependencies."""
    
    def __init__(self, storage: Storage, cache: Cache) -> None:
        self._storage = storage
        self._cache = cache
    
    async def get_data(self, key: str) -> bytes | None:
        # Try cache first
        cached = await self._cache.get(key)
        if cached:
            return cached.encode()
        
        # Load from storage
        data = await self._storage.load(key)
        if data:
            await self._cache.set(key, data.decode())
        
        return data'''
        },
        {
            "system": SYSTEM_PROMPTS[2],
            "user": "Use TypedDict and TypeVarTuple for generic type transformations.",
            "assistant": '''from typing import TypedDict, TypeVar, Generic, Unpack
from dataclasses import dataclass


class UserDict(TypedDict):
    id: int
    name: str
    email: str


class UserWithRole(TypedDict):
    id: int
    name: str
    email: str
    role: str


class PartialUser(TypedDict, total=False):
    name: str
    email: str


# TypeVarTuple for variadic generics (Python 3.11+)
T = TypeVar("T")
Ts = TypeVarTuple("Ts")


def merge_dicts(*dicts: dict) -> dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


# Generic container
@dataclass
class Container(Generic[T]):
    value: T
    metadata: dict
    
    def map(self, func: callable[[T], T]) -> "Container[T]":
        return Container(func(self.value), self.metadata)
    
    def flat_map(
        self, func: callable[[T], "Container[T]"]
    ) -> "Container[T]":
        return func(self.value)


# Using overloads for type narrowing
from typing import overload


@overload
def process(value: int) -> int: ...
@overload
def process(value: str) -> str: ...
@overload
def process(value: list[int]) -> list[int]: ...


def process(value):
    return value'''
        },
        {
            "system": SYSTEM_PROMPTS[2],
            "user": "Implement a generic Repository pattern with abstract base classes.",
            "assistant": '''from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence, Optional
from dataclasses import dataclass


T = TypeVar("T")
ID = TypeVar("ID")


@dataclass(frozen=True)
class Page(Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int
    
    @property
    def pages(self) -> int:
        return (self.total + self.size - 1) // self.size
    
    @property
    def has_next(self) -> bool:
        return self.page < self.pages
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1


class Repository(ABC, Generic[T, ID]):
    """Abstract repository with CRUD operations."""
    
    @abstractmethod
    async def create(self, entity: T) -> T: ...
    
    @abstractmethod
    async def get(self, id: ID) -> Optional[T]: ...
    
    @abstractmethod
    async def update(self, entity: T) -> T: ...
    
    @abstractmethod
    async def delete(self, id: ID) -> None: ...
    
    @abstractmethod
    async def list(
        self,
        page: int = 1,
        size: int = 20,
        **filters,
    ) -> Page[T]: ...


class User:
    id: int
    name: str
    email: str


class UserRepository(Repository[User, int]):
    async def create(self, entity: User) -> User:
        ...
    
    async def get(self, id: int) -> Optional[User]:
        ...'''
        },
    ]


def decorator_examples():
    """Generate decorator examples."""
    return [
        {
            "system": SYSTEM_PROMPTS[1],
            "user": "Create a decorator for retry logic with exponential backoff.",
            "assistant": '''import asyncio
import functools
import logging
from typing import TypeVar, Callable, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Retry decorator with exponential backoff."""
    
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay,
                        )
                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__}: {e}"
                        )
                        import time
                        time.sleep(delay)
            
            raise last_exception
        
        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay,
                        )
                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__}: {e}"
                        )
                        await asyncio.sleep(delay)
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Usage
@retry(max_attempts=5, exceptions=(ConnectionError, TimeoutError))
async def fetch_data(url: str) -> dict:
    ...'''
        },
        {
            "system": SYSTEM_PROMPTS[1],
            "user": "Build a decorator for caching with TTL and async support.",
            "assistant": '''import asyncio
import functools
import hashlib
import time
from typing import TypeVar, Callable, ParamSpec, Generic
from dataclasses import dataclass
from collections import OrderedDict

P = ParamSpec("P")
T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: float
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class TTLCache(Generic[T]):
    """Thread-safe TTL cache with LRU eviction."""
    
    def __init__(self, max_size: int = 128, default_ttl: float = 300.0) -> None:
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    def _make_key(self, *args, **kwargs) -> str:
        key = f"{args!r}{kwargs!r}"
        return hashlib.md5(key.encode()).hexdigest()
    
    async def get_or_compute(
        self,
        key: str,
        compute: Callable[[], T],
        ttl: float | None = None,
    ) -> T:
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry and not entry.is_expired():
                self._cache.move_to_end(key)
                return entry.value
            
            value = await compute() if asyncio.iscoroutinefunction(compute) else compute()
            
            self._cache[key] = CacheEntry(
                value=value,
                expires_at=time.time() + (ttl or self._default_ttl),
            )
            
            if len(self._cache) > self._max_size:
                self._cache.popitem(last=False)
            
            return value


def cached(ttl: float = 300.0, max_size: int = 128):
    """Cached decorator with TTL support."""
    cache = TTLCache(max_size=max_size, default_ttl=ttl)
    
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = cache._make_key(*args, **kwargs)
            return await cache.get_or_compute(
                key,
                lambda: func(*args, **kwargs),
                ttl,
            )
        return wrapper
    return decorator'''
        },
    ]


def generator_examples():
    """Generate iterator and generator examples."""
    return [
        {
            "system": SYSTEM_PROMPTS[0],
            "user": "Implement a memory-efficient pipeline using generators.",
            "assistant": '''from typing import Iterator, Callable, TypeVar
from functools import partial

T = TypeVar("T")
U = TypeVar("U")


class Pipeline(Generic[T]):
    """Fluent generator pipeline for processing large datasets."""
    
    def __init__(self, source: Iterator[T]) -> None:
        self._source = source
        self._transforms: list[Callable] = []
    
    def __iter__(self) -> Iterator[T]:
        result = self._source
        for transform in self._transforms:
            result = transform(result)
        return iter(result)
    
    def filter(self, predicate: Callable[[T], bool]) -> "Pipeline[T]":
        """Add filter transformation."""
        def apply(source: Iterator[T]) -> Iterator[T]:
            return (x for x in source if predicate(x))
        self._transforms.append(apply)
        return self
    
    def map(self, fn: Callable[[T], U]) -> "Pipeline[U]":
        """Add map transformation."""
        def apply(source: Iterator[T]) -> Iterator[U]:
            return (fn(x) for x in source)
        self._transforms.append(apply)
        return self  # type: ignore
    
    def flat_map(self, fn: Callable[[T], Iterator[U]]) -> "Pipeline[U]":
        """Add flat_map transformation."""
        def apply(source: Iterator[T]) -> Iterator[U]:
            for item in source:
                yield from fn(item)
        self._transforms.append(apply)
        return self  # type: ignore
    
    def take(self, n: int) -> "Pipeline[T]":
        """Take first n items."""
        def apply(source: Iterator[T]) -> Iterator[T]:
            for i, item in enumerate(source):
                if i >= n:
                    break
                yield item
        self._transforms.append(apply)
        return self
    
    def batch(self, size: int) -> "Pipeline[list[T]]":
        """Batch items into lists."""
        def apply(source: Iterator[T]) -> Iterator[list[T]]:
            batch = []
            for item in source:
                batch.append(item)
                if len(batch) >= size:
                    yield batch
                    batch = []
            if batch:
                yield batch
        self._transforms.append(apply)
        return self  # type: ignore


# Usage
def read_lines(path: str) -> Iterator[str]:
    with open(path) as f:
        yield from f

result = (
    Pipeline(read_lines("data.txt"))
    .map(str.strip)
    .filter(bool)
    .map(str.lower)
    .batch(100)
)

for batch in result:
    process(batch)'''
        },
    ]


def context_manager_examples():
    """Generate context manager examples."""
    return [
        {
            "system": SYSTEM_PROMPTS[1],
            "user": "Create a context manager for resource management with cleanup.",
            "assistant": '''import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator
from dataclasses import dataclass


@dataclass
class DatabaseConnection:
    """Simulated database connection."""
    dsn: str
    
    async def execute(self, query: str) -> list[dict]:
        return [{"id": 1, "name": "test"}]
    
    async def close(self) -> None:
        print(f"Closing connection to {self.dsn}")


@dataclass
class Transaction:
    """Transaction context for database operations."""
    
    connection: DatabaseConnection
    committed: bool = False
    
    async def commit(self) -> None:
        self.committed = True
        print("Transaction committed")
    
    async def rollback(self) -> None:
        print("Transaction rolled back")


@asynccontextmanager
async def get_connection(dsn: str) -> AsyncIterator[DatabaseConnection]:
    """Get database connection with automatic cleanup."""
    conn = DatabaseConnection(dsn)
    try:
        yield conn
    finally:
        await conn.close()


@asynccontextmanager
async def transaction(dsn: str) -> AsyncIterator[Transaction]:
    """Transaction context manager with auto-commit/rollback."""
    async with get_connection(dsn) as conn:
        tx = Transaction(connection=conn)
        try:
            yield tx
            if not tx.committed:
                await tx.commit()
        except Exception:
            await tx.rollback()
            raise


# Usage
async def transfer_funds(from_id: int, to_id: int, amount: float):
    async with transaction("postgresql://localhost/db") as tx:
        await tx.connection.execute(
            f"UPDATE accounts SET balance = balance - {amount} WHERE id = {from_id}"
        )
        await tx.connection.execute(
            f"UPDATE accounts SET balance = balance + {amount} WHERE id = {to_id}"
        )'''
        },
    ]


def abc_examples():
    """Generate abstract base class examples."""
    return [
        {
            "system": SYSTEM_PROMPTS[2],
            "user": "Implement the Strategy pattern using ABC with type safety.",
            "assistant": '''from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from dataclasses import dataclass


T = TypeVar("T")


class SortStrategy(ABC, Generic[T]):
    """Abstract base for sorting strategies."""
    
    @abstractmethod
    def sort(self, data: list[T]) -> list[T]:
        """Sort data and return new list."""
        ...
    
    @abstractmethod
    def name(self) -> str:
        """Return strategy name."""
        ...


class QuickSort(T, Generic[T]):
    """Quick sort implementation."""
    
    def sort(self, data: list[T]) -> list[T]:
        if len(data) <= 1:
            return data.copy()
        
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        
        s = QuickSort()
        return s.sort(left) + middle + s.sort(right)
    
    def name(self) -> str:
        return "QuickSort"


class MergeSort(T, Generic[T]):
    """Merge sort implementation."""
    
    def sort(self, data: list[T]) -> list[T]:
        if len(data) <= 1:
            return data.copy()
        
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        
        return self._merge(left, right)
    
    def _merge(self, left: list[T], right: list[T]) -> list[T]:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    def name(self) -> str:
        return "MergeSort"


class Sorter(ABC, Generic[T]):
    """Context for sorting operations."""
    
    def __init__(self, strategy: SortStrategy[T]) -> None:
        self._strategy = strategy
    
    @property
    def strategy(self) -> SortStrategy[T]:
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: SortStrategy[T]) -> None:
        self._strategy = strategy
    
    def sort(self, data: list[T]) -> list[T]:
        return self._strategy.sort(data)'''
        },
    ]


def generate_deep_python(output_path: str) -> int:
    """Generate all deep Python examples and write to JSONL."""
    all_examples = []
    
    all_examples.extend(async_examples())
    all_examples.extend(dataclass_examples())
    all_examples.extend(typing_examples())
    all_examples.extend(decorator_examples())
    all_examples.extend(generator_examples())
    all_examples.extend(context_manager_examples())
    all_examples.extend(abc_examples())
    
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            record = {
                "messages": [
                    {"role": "system", "content": ex["system"]},
                    {"role": "user", "content": ex["user"]},
                    {"role": "assistant", "content": ex["assistant"]}
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    
    return count


if __name__ == "__main__":
    import sys
    output = sys.argv[1] if len(sys.argv) > 1 else "deep_python_training.jsonl"
    count = generate_deep_python(output)
    print(f"Generated {count} deep Python examples")
