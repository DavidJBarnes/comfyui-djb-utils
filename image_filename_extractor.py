import os
import folder_paths

class WorkingFilenameExtractor:
    """
    A filename extractor that uses ComfyUI's internal image loading system
    to track the most recently loaded image filename.
    """
    
    # Class variable to store the most recent filename
    _last_loaded_image = ""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("full_filename", "name_only", "extension")
    FUNCTION = "extract_filename"
    CATEGORY = "djb-utils"
    
    def extract_filename(self, image):
        """
        Extract filename using ComfyUI's internal tracking.
        """
        filename = self._last_loaded_image
        
        if not filename:
            # Fallback: try to get from ComfyUI's recent files
            try:
                # Check ComfyUI's web interface recent files
                from server import PromptServer
                if hasattr(PromptServer.instance, 'last_image_filename'):
                    filename = PromptServer.instance.last_image_filename
            except:
                pass
        
        if not filename:
            filename = "unknown_image"
        
        # Clean filename and handle -swapped.png removal
        clean_filename = os.path.basename(filename)
        if clean_filename.endswith("-swapped.png"):
            clean_filename = clean_filename[:-len("-swapped.png")]
            if not any(clean_filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']):
                clean_filename += ".png"
        elif "-swapped.png" in clean_filename:
            clean_filename = clean_filename.replace("-swapped.png", "")
        
        # Extract components
        name_without_ext = os.path.splitext(clean_filename)[0]
        extension = os.path.splitext(clean_filename)[1]
        
        return (clean_filename, name_without_ext, extension)


class DirectImageFilenameInput:
    """
    Alternative approach: Manual filename input with image passthrough
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Enter the image filename manually"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "IMAGE")
    RETURN_NAMES = ("full_filename", "name_only", "extension", "image")
    FUNCTION = "process_filename"
    CATEGORY = "djb-utils"
    
    def process_filename(self, image, filename):
        """
        Process manually entered filename
        """
        if not filename.strip():
            return ("", "", "", image)
        
        # Clean filename and handle -swapped.png removal
        clean_filename = os.path.basename(filename.strip())
        if clean_filename.endswith("-swapped.png"):
            clean_filename = clean_filename[:-len("-swapped.png")]
            if not any(clean_filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']):
                clean_filename += ".png"
        elif "-swapped.png" in clean_filename:
            clean_filename = clean_filename.replace("-swapped.png", "")
        
        # Extract components
        name_without_ext = os.path.splitext(clean_filename)[0]
        extension = os.path.splitext(clean_filename)[1]
        
        return (clean_filename, name_without_ext, extension, image)


# Try to patch ComfyUI's image loading to track filenames
try:
    from PIL import Image
    from comfy import utils
    
    # Store original load function
    if hasattr(utils, 'common_upscale'):
        # This is a common function that processes images
        original_common_upscale = utils.common_upscale
        
        def tracked_common_upscale(samples, *args, **kwargs):
            result = original_common_upscale(samples, *args, **kwargs)
            return result
        
        utils.common_upscale = tracked_common_upscale
        
except Exception as e:
    print(f"Could not patch image loading functions: {e}")

# Try to hook into the LoadImage node directly
try:
    import nodes
    if hasattr(nodes, 'LoadImage'):
        original_load_image = nodes.LoadImage.load_image
        
        def tracked_load_image(self, image):
            # Store the filename before processing
            WorkingFilenameExtractor._last_loaded_image = image
            return original_load_image(self, image)
        
        nodes.LoadImage.load_image = tracked_load_image
        print("Successfully patched LoadImage to track filenames")
        
except Exception as e:
    print(f"Could not patch LoadImage node: {e}")


# Node mappings
NODE_CLASS_MAPPINGS = {
    "WorkingFilenameExtractor": WorkingFilenameExtractor,
    "DirectImageFilenameInput": DirectImageFilenameInput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WorkingFilenameExtractor": "Working Filename Extractor",
    "DirectImageFilenameInput": "Direct Image Filename Input",
}
