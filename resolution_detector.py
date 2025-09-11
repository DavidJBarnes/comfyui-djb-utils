import re
import os
import folder_paths

class ResolutionDetectorFromFilename:
    @classmethod
    def INPUT_TYPES(cls):
        # Get list of diffusion models from ComfyUI's folder system
        try:
            model_list = folder_paths.get_filename_list("diffusion_models")
        except:
            # Fallback if diffusion_models folder doesn't exist in folder_paths
            diffusion_path = os.path.join(folder_paths.models_dir, "diffusion_models")
            if os.path.exists(diffusion_path):
                model_list = [f for f in os.listdir(diffusion_path) if f.endswith(('.safetensors', '.ckpt', '.pt', '.pth'))]
            else:
                model_list = ["No models found"]
        
        return {
            "required": {
                "model_filename": (model_list,),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("resolution",)
    FUNCTION = "detect_resolution"
    CATEGORY = "WAN"
    
    def detect_resolution(self, model_filename):
        print(f"ResolutionDetector: Checking filename: {model_filename}")
        
        if model_filename and model_filename != "No models found":
            # Search for 480p or 720p in the filename (case insensitive)
            match = re.search(r'(480p|720p)', model_filename, re.IGNORECASE)
            if match:
                result = match.group(1).lower()  # Return lowercase for consistency
                print(f"ResolutionDetector: Found resolution: {result}")
                return (result,)
        
        print("ResolutionDetector: No resolution found")
        return ("",)

# Alternative version that tries to intercept model loading
class WAN21ModelTracker:
    _loaded_models = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("resolution",)
    FUNCTION = "detect_resolution"
    CATEGORY = "WAN"
    
    def detect_resolution(self, model):
        # Try to find resolution from recently loaded models
        model_id = str(id(model))
        
        print(f"WAN21ModelTracker: Looking for model ID: {model_id}")
        print(f"WAN21ModelTracker: Available tracked models: {list(self._loaded_models.keys())}")
        
        # First try exact model ID match
        if model_id in self._loaded_models:
            filename = self._loaded_models[model_id]
            match = re.search(r'(480p|720p)', filename, re.IGNORECASE)
            if match:
                result = match.group(1).lower()
                print(f"WAN21ModelTracker: Found resolution from exact tracking: {result}")
                return (result,)
        
        # If no exact match, try the most recent loaded files
        recent_files = [v for k, v in self._loaded_models.items() if k.startswith('recent_')]
        if recent_files:
            print(f"WAN21ModelTracker: Checking recent files: {recent_files}")
            # Check the most recently loaded file
            latest_file = recent_files[-1]
            match = re.search(r'(480p|720p)', latest_file, re.IGNORECASE)
            if match:
                result = match.group(1).lower()
                print(f"WAN21ModelTracker: Found resolution from recent file {latest_file}: {result}")
                return (result,)
        
        # Fallback: try to extract from model attributes (more thorough search)
        print(f"WAN21ModelTracker: Checking model attributes...")
        model_attrs = []
        try:
            for attr_name in dir(model):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(model, attr_name)
                        if isinstance(attr_value, str) and attr_value:
                            model_attrs.append(f"{attr_name}: {attr_value}")
                            match = re.search(r'(480p|720p)', attr_value, re.IGNORECASE)
                            if match:
                                result = match.group(1).lower()
                                print(f"WAN21ModelTracker: Found resolution in attribute {attr_name}: {result}")
                                return (result,)
                    except:
                        continue
            
            # Print all string attributes for debugging
            if model_attrs:
                print(f"WAN21ModelTracker: Model string attributes: {model_attrs[:10]}")  # Limit to first 10
            else:
                print("WAN21ModelTracker: No string attributes found")
                
        except Exception as e:
            print(f"WAN21ModelTracker: Error checking attributes: {e}")
        
        print("WAN21ModelTracker: No resolution found")
        return ("",)

# Try to hook into ComfyUI's model loading - this is a bit experimental
try:
    # Try to patch the UNetModel or DiffusionModel loading
    import comfy.model_management
    import comfy.utils
    
    # Store original load_models function if it exists
    if hasattr(comfy.utils, 'load_torch_file'):
        original_load_torch_file = comfy.utils.load_torch_file
        
        def tracked_load_torch_file(path, *args, **kwargs):
            print(f"WAN21ModelTracker: Loading file: {path}")
            result = original_load_torch_file(path, *args, **kwargs)
            
            # If this looks like a model loading, track it
            if isinstance(path, str) and any(ext in path.lower() for ext in ['.safetensors', '.ckpt', '.pt', '.pth']):
                filename = os.path.basename(path)
                # We'll use a simple counter approach since we can't easily get the model ID here
                WAN21ModelTracker._loaded_models[f"recent_{len(WAN21ModelTracker._loaded_models)}"] = filename
                print(f"WAN21ModelTracker: Tracked loading of {filename}")
            
            return result
        
        comfy.utils.load_torch_file = tracked_load_torch_file
except Exception as e:
    print(f"Could not patch ComfyUI loading functions: {e}")

# Node registration
NODE_CLASS_MAPPINGS = {
    "ResolutionDetectorFromFilename": ResolutionDetectorFromFilename,
    "WAN21ModelTracker": WAN21ModelTracker
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolutionDetectorFromFilename": "WAN Resolution Detector (Select File)",
    "WAN21ModelTracker": "WAN Resolution Detector (Model Input)"
}
