"""
ComfyUI DJB Utils - Custom nodes for ComfyUI
"""

from .image_filename_extractor import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Import any other node files you have
# from .other_node_file import NODE_CLASS_MAPPINGS as OTHER_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as OTHER_DISPLAY_MAPPINGS

# Combine all node mappings
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# If you have multiple files, combine them like this:
# NODE_CLASS_MAPPINGS.update(OTHER_MAPPINGS)
# NODE_DISPLAY_NAME_MAPPINGS.update(OTHER_DISPLAY_MAPPINGS)
