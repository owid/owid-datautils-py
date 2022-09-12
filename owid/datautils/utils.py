"""Functions related to the dataframe HighLevelDiff class."""

from typing import Callable, Generator, Iterable, List, Any, Optional


def get_list_description_with_max_length(items: List[Any], max_items: int = 20) -> str:
    """Return a string representation for a list, potentially shortened in the middle."""
    if len(items) > max_items:
        return (
            f"[{len(items)} items] "
            + f'{", ".join(str(item) for item in items[:int(max_items/2)])} ... "'
            + f'{", ".join(str(item) for item in items[-int(max_items/2):])}'
        )
    else:
        return ", ".join(str(item) for item in items)


def yield_list_lines(
    description: str, items: Iterable[Any]
) -> Generator[str, None, None]:
    """Yield a list of lines for a list of items.

    If the sublist is a single item then no newline is inserted. If the sublist has more than one item
    then the description is printed as a header and the items are printed on separate lines with a sligh indent.
    """
    sublines = [item for item in items]
    if len(sublines) > 1:
        yield f"{description}:"
        for subline in sublines:
            if subline != "":
                yield f"  {subline}"
    elif len(sublines) == 1:
        yield f"{description}: {sublines[0]}"


def get_compact_list_description(
    items_iterable: Iterable[Any],
    tuple_headers: Optional[List[str]] = None,
    max_items: int = 20,
) -> Generator[str, None, None]:
    """Get a compact desription of a list.

    If the list is numeric and monotonic then it gets compacted into a range like 2000-2015. If
    the list contains tuples then the tuples are deconstructed into their components and the
    components are compacted individually. Long lists (above max_items items) are
    shortened in the middle.
    """
    items = set(items_iterable)
    if not items:
        yield "[]"
    elif all(isinstance(item, int) for item in items):
        sorted_items = sorted(items)
        if len(items) == 1:
            yield str(sorted_items[0])
        if len(items) == 2:
            yield f"{sorted_items[0]}, {sorted_items[1]}"
        if len(items) > 2:
            if len(items) == sorted_items[-1] - sorted_items[0]:
                yield f"{sorted_items[0]}-{sorted_items[-1]}"
            else:
                yield get_list_description_with_max_length(sorted_items, max_items)
    elif all(isinstance(item, tuple) for item in items):
        transposed = zip(*items)
        lines = [
            line for item in transposed for line in get_compact_list_description(item)
        ]
        if tuple_headers and len(tuple_headers) == len(lines):
            yield from (
                f"{header}: {line}" for header, line in zip(tuple_headers, lines)
            )
        else:
            yield from lines
    else:
        sorted_items = sorted(items)
        yield get_list_description_with_max_length(sorted_items, max_items)


def yield_formatted_if_not_empty(
    item: Any,
    format_function: Callable[[Any], Generator[str, None, None]],
    fallback_message: str = "",
) -> Generator[str, None, None]:
    """Yield an item formatted with the given function if it is not empty.

    This is a useful helper to avoid duplicating property/function access in if blocks and
    then again in the block body.
    """
    if item is not None and any(item):
        yield from format_function(item)
    elif fallback_message != "":
        yield fallback_message
