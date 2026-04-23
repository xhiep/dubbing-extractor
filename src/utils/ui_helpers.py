"""UI Helper Functions.

Pure utility functions for UI geometry calculations with no state dependencies.
"""


def expand_band_from_center(
    top_y: int | None,
    bottom_y: int | None,
    frame_height: int,
    padding_px: int
) -> tuple[int | None, int | None]:
    """Expand subtitle band from center by padding pixels.

    Args:
        top_y: Top Y coordinate of band (None if not set)
        bottom_y: Bottom Y coordinate of band (None if not set)
        frame_height: Total frame height in pixels
        padding_px: Padding to add around band

    Returns:
        Tuple of (new_top, new_bottom) or (None, None) if invalid input
    """
    if top_y is None or bottom_y is None or frame_height <= 0:
        return None, None
    center_y = (int(top_y) + int(bottom_y)) / 2.0
    base_height = max(2, int(bottom_y) - int(top_y) + 1)
    half_height = base_height / 2.0 + max(0, int(padding_px or 0))
    new_top = max(0, int(round(center_y - half_height)))
    new_bottom = min(frame_height - 1, int(round(center_y + half_height)))
    if new_bottom <= new_top:
        new_bottom = min(frame_height - 1, new_top + 1)
    return new_top, new_bottom


def shift_band(
    top_y: int | None,
    bottom_y: int | None,
    frame_height: int,
    offset_px: int
) -> tuple[int | None, int | None]:
    """Shift subtitle band vertically by offset pixels.

    Args:
        top_y: Top Y coordinate of band (None if not set)
        bottom_y: Bottom Y coordinate of band (None if not set)
        frame_height: Total frame height in pixels
        offset_px: Vertical offset in pixels (positive = down, negative = up)

    Returns:
        Tuple of (new_top, new_bottom) or (None, None) if invalid input
    """
    if top_y is None or bottom_y is None or frame_height <= 0:
        return None, None
    shift = max(-frame_height, min(frame_height, int(offset_px or 0)))
    height = max(2, int(bottom_y) - int(top_y) + 1)
    new_top = int(top_y) - shift
    new_bottom = new_top + height - 1
    if new_top < 0:
        new_top = 0
        new_bottom = min(frame_height - 1, new_top + height - 1)
    if new_bottom > frame_height - 1:
        new_bottom = frame_height - 1
        new_top = max(0, new_bottom - height + 1)
    return new_top, new_bottom
