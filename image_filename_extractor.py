import os

class ImageFilenameExtractor:
    """
    A custom ComfyUI node that extracts the filename from an image input
    and optionally strips "-swapped.png" from the filename.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "extract_filename"
    CATEGORY = "djb-utils"
    
    def extract_filename(self, image):
        """
        Extract filename from image tensor and strip "-swapped.png" if present
        """
        filename = ""
        
        # Try to get filename from image metadata
        if hasattr(image, 'filename') and image.filename:
            filename = image.filename
        elif hasattr(image, 'image') and hasattr(image.image, 'filename'):
            filename = image.image.filename
        elif len(image.shape) > 0 and hasattr(image, 'pil_image'):
            # For PIL images
            if hasattr(image.pil_image, 'filename'):
                filename = image.pil_image.filename
        
        # If we still don't have a filename, try to get it from the tensor metadata
        if not filename and hasattr(image, 'names') and image.names:
            filename = image.names[0] if isinstance(image.names, list) else str(image.names)
        
        # Extract just the filename without path
        if filename:
            filename = os.path.basename(filename)
            
            # Strip "-swapped.png" if it exists in the filename
            if filename.endswith("-swapped.png"):
                filename = filename[:-len("-swapped.png")]
                # Add back the original extension if there was one
                # (in case the original was something like "image-swapped.png" from "image.jpg")
                if not filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                    filename += ".png"  # Default to .png if no extension
            elif "-swapped.png" in filename:
                # Handle case where "-swapped.png" appears in middle of filename
                filename = filename.replace("-swapped.png", "")
        
        return (filename,)

# Alternative implementation that works with ComfyUI's image loading system
class ImageFilenameExtractorV2:
    """
    Alternative implementation that tries to access filename through ComfyUI's image loading metadata
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "extract_filename"
    CATEGORY = "utils"
    OUTPUT_NODE = False
    
    def extract_filename(self, image):
        filename = "unknown"
        
        # ComfyUI typically stores metadata in the batch dimension or as attributes
        try:
            # Method 1: Check if filename is stored in image metadata
            if hasattr(image, 'filename'):
                filename = str(image.filename)
            
            # Method 2: Check for filename in tensor metadata (common in ComfyUI)
            elif hasattr(image, 'names') and image.names is not None:
                if isinstance(image.names, (list, tuple)) and len(image.names) > 0:
                    filename = str(image.names[0])
                else:
                    filename = str(image.names)
            
            # Method 3: Try to get from tensor's underlying data structure
            elif hasattr(image, 'meta') and 'filename' in image.meta:
                filename = str(image.meta['filename'])
                
        except (AttributeError, IndexError, KeyError):
            # If all methods fail, return a default
            filename = "image_no_filename"
        
        # Clean up the filename
        if filename and filename != "unknown":
            # Extract basename (remove path)
            filename = os.path.basename(filename)
            
            # Remove "-swapped.png" if present
            if filename.endswith("-swapped.png"):
                # Remove -swapped.png and keep original extension or add .png
                base_name = filename[:-len("-swapped.png")]
                if '.' in base_name:
                    filename = base_name
                else:
                    filename = base_name + ".png"
            elif "-swapped.png" in filename:
                # Remove -swapped.png from anywhere in the filename
                filename = filename.replace("-swapped.png", "")
        
        return (filename,)

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "ImageFilenameExtractor": ImageFilenameExtractor,
    "ImageFilenameExtractorV2": ImageFilenameExtractorV2,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageFilenameExtractor": "Image Filename Extractor",
    "ImageFilenameExtractorV2": "Image Filename Extractor V2",
}

# For ComfyUI to recognize this as a custom node package
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
