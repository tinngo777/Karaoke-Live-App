import os 
import shutil
import subprocess
import sys


def run_demucs (input_path: str, output_dir: str = "output_audio", model_name: str = "htdemucs_6s") -> str:
    # Clean or create output folder
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Demucs command
    cmd = [sys.executable, "-m", "demucs", "--device", "cuda", "--name", model_name, "--out", output_dir, input_path]

    # Demucs subprocess
    try:
        result = subprocess.run(cmd, check = True, capture_output = True, text = True)
        print("Demucs completed")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Demucs failed to separate stems.")
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        raise RuntimeError("Demucs separation failed.")
    
    # Find model output dir 
    model_dir = os.path.join(output_dir, model_name)
    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"Model output folder not found: {model_dir}")
    
    subfolders = os.listdir(model_dir)
    if not subfolders:
        raise FileNotFoundError(f"No stem folders found inside {model_dir}")
    
    stems_dir = os.path.join(model_dir, subfolders[0])

    return stems_dir
    