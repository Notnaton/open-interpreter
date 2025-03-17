"""
Asynchronous helpers for the Open Interpreter GUI.

This module provides utilities for handling asynchronous operations
in the GUI application, primarily for managing response streaming.
"""
import asyncio
import threading
from typing import Any, Callable, Awaitable, Generator, AsyncGenerator, TypeVar, Optional
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')

class AsyncHelper:
    """Helper class for managing asynchronous operations in the GUI"""
    
    @staticmethod
    def run_in_thread(func: Callable[..., Any], *args: Any, **kwargs: Any) -> threading.Thread:
        """
        Run a function in a separate thread.
        
        Args:
            func: The function to run
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The started thread object
        """
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True  # Thread will exit when main thread exits
        thread.start()
        return thread
    
    @staticmethod
    async def run_async_in_thread(func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        """
        Run an async function in a separate thread with its own event loop.
        
        Args:
            func: The async function to run
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the async function
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await asyncio.get_event_loop().run_in_executor(
                executor,
                AsyncHelper._run_in_new_loop,
                func, args, kwargs
            )
    
    @staticmethod
    def _run_in_new_loop(func: Callable[..., Awaitable[T]], args: tuple, kwargs: dict) -> T:
        """
        Create a new event loop in the current thread and run the function.
        
        Args:
            func: The async function to run
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the async function
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    
    @staticmethod
    async def ensure_async_generator(
        response_generator: Any
    ) -> AsyncGenerator[Any, None]:
        """
        Ensure that the given response generator is an async generator.
        
        Args:
            response_generator: The generator to convert (could be sync generator, 
                                async generator, awaitable, or single value)
            
        Returns:
            An async generator that yields items from the original generator
        """
        # If it's already an async generator, just return it
        if hasattr(response_generator, '__aiter__'):
            async for item in response_generator:
                yield item
            return
            
        # If it's an awaitable (coroutine or future), await it first
        if asyncio.iscoroutine(response_generator) or asyncio.isfuture(response_generator):
            result = await response_generator
            # If the result is an async generator, yield from it
            if hasattr(result, '__aiter__'):
                async for item in result:
                    yield item
                return
            # Otherwise, yield the single result
            yield result
            return
            
        # If it's a sync generator, yield each item
        if hasattr(response_generator, '__iter__') and not isinstance(response_generator, (str, bytes, dict)):
            for item in response_generator:
                yield item
            return
            
        # If it's a single item, yield it once
        yield response_generator 