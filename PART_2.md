
---

## 4️⃣ DIFFUSION PROVIDER: `backend/providers/offline_diffusers.py`

This file contains the heavy lifting for Image Generation. It wraps the Hugging Face `diffusers` library and applies the specific optimizations needed for consumer hardware.

### Imports
```python
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from backend.utils.memory import memory_manager
```
*   **`StableDiffusionImg2ImgPipeline`**: The specific pipeline used. It takes an input image + prompt and produces a new image. It is *not* the standard text-to-image pipeline.
*   **`DPMSolverMultistepScheduler`**: A "Scheduler" controls the denoising process. DPM++ is chosen because it produces high-quality images in fewer steps (20-25) compared to the default Euler (50).

### Initialization & Hardware Logic
```python
class OfflineDiffusersProvider:
    def __init__(self):
        if torch.cuda.is_available():
            self.device = "cuda"
            self.dtype = torch.float16
        else:
            self.device = "cpu"
            self.dtype = torch.float32
```
*   **Precision (dtype)**:
    *   **`float16`**: Uses "Half Precision" floating point numbers (16-bit). This halves the VRAM usage (from ~8GB to ~4GB for SD 1.5) with negligible quality loss. **Crucial for this project.**
    *   **`float32`**: CPU operations generally require 32-bit float consistency.

### Pipeline Loading (`initialize`)
```python
    def initialize(self):
        if not settings.low_vram and self.pipeline is not None:
             return # Skip if already loaded in Normal Mode

        memory_manager.ensure_gpu("sd_img2img")
```
*   **Handshake**: Calls `memory_manager.ensure_gpu`. In Low VRAM mode, this triggers the eviction of YOLO or any other resident model.

```python
        self.pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            settings.diffusers_model,
            torch_dtype=self.dtype,
            use_safetensors=True
        )
```
*   **`use_safetensors=True`**: Uses the SafeTensors format. It maps directly to memory (mmap) and loads significantly faster than standard PyTorch `.bin` files.

### Optimizations (The "Secret Sauce")
```python
        if self.device == "cuda":
            self.pipeline.to("cuda")
            self.pipeline.enable_attention_slicing()
            self.pipeline.enable_vae_slicing()
            
            if hasattr(self.pipeline, "enable_xformers_memory_efficient_attention"):
                 self.pipeline.enable_xformers_memory_efficient_attention()
```
*   **`enable_attention_slicing()`**: Splits the massive "Attention Matrix" calculation into smaller chunks.
    *   *Trade-off*: Slightly slower (milliseconds).
    *   *Gain*: Massive VRAM savings. Prevents OOM on 4GB cards.
*   **`enable_vae_slicing()`**: The VAE (Variational Autoencoder) converts the latent representation back to a pixel image. This is often the step that crashes the GPU at 99%. Slicing decodes the image in strips rather than all at once.
*   **`enable_xformers...`**: Uses optimized CUDA kernels provided by the `xformers` library. If installed, it speeds up generation and reduces memory footprint further.

### Image Generation (`generate_image`)
```python
    def generate_image(self, image_path, ...):
        # ... logic ...
        target_size = (512, 512)
        input_image = input_image.resize(target_size)
```
*   **Resolution Cap**: 
    *   Stable Diffusion v1.5 was trained on 512x512 images.
    *   While Normal mode *could* handle 640x640, the code caps it at 512x512 to ensure 100% stability.
    *   Generating non-square aspect ratios or higher resolutions on v1.5 often results in "duplication artifacts" (two heads, stacked rooms).

### Step Capping Logic
```python
        if settings.low_vram:
            strength = settings.img2img_strength
            num_steps = min(settings.num_inference_steps, 20)
        else:
            num_steps = min(30, settings.num_inference_steps)
```
*   **Runtime Config**: This block explicitly overrides global settings based on the runtime hardware profile.
    *   **Low VRAM**: Capped at 20 steps. Users cannot force higher steps via API to prevent timeouts or OOMs.

### Inference Call
```python
        with torch.inference_mode():
            output = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=input_image,
                strength=strength,
                guidance_scale=settings.guidance_scale,
                num_inference_steps=num_steps
            ).images[0]
```
*   **`torch.inference_mode()`**: Disables PyTorch's gradient calculation engine (Autograd). Even though we aren't training, PyTorch tracks history by default. Disabling this saves significant RAM.
*   **`strength`**: This controls how much the AI respects the original image.
    *   0.0 = Identical to original.
    *   1.0 = Complete noise, ignores original structure.
    *   **0.55 (Default)**: Finds the balance between "Keeping walls" and "Changing furniture".

### Immediate Cleanup (Low VRAM)
```python
        if settings.low_vram:
            torch.cuda.empty_cache()
```
*   **Purpose**: Immediately after the heavy lifting is done, it attempts to free VRAM for the next quick task (like UI updates or thumbnail generation), keeping the system snappy.
