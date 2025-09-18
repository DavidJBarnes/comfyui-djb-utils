import os
import folder_paths

class ReliableFilenameExtractor:
    """
    A more reliable ComfyUI node that gets the filename by accessing ComfyUI's
    internal image loading system directly, rather than trying to extract it
    from image metadata.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_name": ("STRING", {
                    "default": "",
                    "tooltip": "The image filename (connect from LoadImage's 'image' parameter)"
                }),
            },
            "optional": {
                "image": ("IMAGE",),  # Optional for validation/passthrough
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "IMAGE")
    RETURN_NAMES = ("full_filename", "name_only", "extension", "image_passthrough")
    FUNCTION = "extract_filename"
    CATEGORY = "djb-utils"
    
    def extract_filename(self, image_name, image=None):
        """
        Extract filename components from the image_name parameter.
        This is more reliable than trying to get it from image metadata.
        """
        if not image_name or image_name.strip() == "":
            return ("", "", "", image)
        
        # Clean the filename - remove any path components
        clean_filename = os.path.basename(image_name.strip())
        
        # Handle your "-swapped.png" case
        if clean_filename.endswith("-swapped.png"):
            clean_filename = clean_filename[:-len("-swapped.png")]
            # Add back appropriate extension if needed
            if not any(clean_filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']):
                clean_filename += ".png"
        elif "-swapped.png" in clean_filename:
            clean_filename = clean_filename.replace("-swapped.png", "")
        
        # Extract components
        name_without_ext = os.path.splitext(clean_filename)[0]
        extension = os.path.splitext(clean_filename)[1]
        
        return (clean_filename, name_without_ext, extension, image)


class FilenameFromLoadImageDirect:
    """
    Alternative approach that tries to get the currently selected image
    from ComfyUI's LoadImage system directly.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # Get available images from ComfyUI's input folder
        input_dir = folder_paths.get_input_directory()
        files = []
        if os.path.exists(input_dir):
            files = [f for f in os.listdir(input_dir) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'))]
        
        return {
            "required": {
                "image_file": (files, {"default": files[0] if files else ""}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("full_filename", "name_only", "extension")
    FUNCTION = "get_filename"
    CATEGORY = "djb-utils"
    
    def get_filename(self, image_file):
        """
        Get filename from the selected image file.
        """
        if not image_file:
            return ("", "", "")
        
        # Handle "-swapped.png" removal
        clean_filename = image_file
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


# Improved version of your existing approach with better debugging
class ImprovedImageFilenameExtractor:
    """
    Improved version of your existing extractor with better debugging
    and more metadata access methods.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("filename", "debug_info")
    FUNCTION = "extract_filename"
    CATEGORY = "djb-utils"
    
    def extract_filename(self, image):
        """
        Enhanced filename extraction with debugging information.
        """
        filename = ""
        debug_info = []
        
        # Debug: Check what attributes the image tensor has
        debug_info.append(f"Image type: {type(image)}")
        debug_info.append(f"Image shape: {getattr(image, 'shape', 'No shape')}")
        debug_info.append(f"Available attributes: {[attr for attr in dir(image) if not attr.startswith('_')]}")
        
        # Try multiple methods to extract filename
        methods_tried = []
        
        # Method 1: Direct filename attribute
        if hasattr(image, 'filename') and image.filename:
            filename = str(image.filename)
            methods_tried.append("Direct filename attribute - SUCCESS")
        else:
            methods_tried.append("Direct filename attribute - FAILED")
        
        # Method 2: Names attribute
        if not filename and hasattr(image, 'names') and image.names:
            try:
                if isinstance(image.names, (list, tuple)):
                    filename = str(image.names[0]) if image.names else ""
                else:
                    filename = str(image.names)
                methods_tried.append("Names attribute - SUCCESS")
            except:
                methods_tried.append("Names attribute - FAILED")
        else:
            methods_tried.append("Names attribute - FAILED or not available")
        
        # Method 3: Check for metadata dict
        if not filename and hasattr(image, 'metadata') and isinstance(image.metadata, dict):
            if 'filename' in image.metadata:
                filename = str(image.metadata['filename'])
                methods_tried.append("Metadata dict - SUCCESS")
            else:
                methods_tried.append("Metadata dict - No filename key")
        else:
            methods_tried.append("Metadata dict - FAILED or not available")
        
        # Method 4: Try to access tensor info
        if not filename:
            try:
                # Some ComfyUI nodes store info in tensor.meta or similar
                if hasattr(image, 'meta'):
                    debug_info.append(f"Meta content: {image.meta}")
                methods_tried.append("Tensor meta - checked")
            except:
                methods_tried.append("Tensor meta - FAILED")
        
        # Clean up filename if found
        if filename and filename not in ["", "None", "none"]:
            filename = os.path.basename(filename)
            
            # Handle -swapped.png removal
            if filename.endswith("-swapped.png"):
                filename = filename[:-len("-swapped.png")]
                if not any(filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']):
                    filename += ".png"
            elif "-swapped.png" in filename:
                filename = filename.replace("-swapped.png", "")
        else:
            filename = "no_filename_found"
        
        debug_info.extend(methods_tried)
        debug_output = " | ".join(debug_info)
        
        return (filename, debug_output)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "ReliableFilenameExtractor": ReliableFilenameExtractor,
    "FilenameFromLoadImageDirect": FilenameFromLoadImageDirect,
    "ImprovedImageFilenameExtractor": ImprovedImageFilenameExtractor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ReliableFilenameExtractor": "Reliable Filename Extractor",
    "FilenameFromLoadImageDirect": "Filename from LoadImage Direct",
    "ImprovedImageFilenameExtractor": "Improved Image Filename Extractor (Debug)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
