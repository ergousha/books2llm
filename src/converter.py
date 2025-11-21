import os
import subprocess
from pathlib import Path
from .config import MARKER_LANGS

class PDFConverter:
    def __init__(self):
        pass

    def convert(self, pdf_path: Path) -> tuple[str, dict]:
        """
        Converts a PDF to Markdown using Marker.
        Returns the markdown content and metadata.
        
        Since Marker is complex to invoke via Python API without exact knowledge of the version,
        we will use the CLI command which is robust.
        """
        output_dir = pdf_path.parent / "marker_temp" / pdf_path.stem
        os.makedirs(output_dir, exist_ok=True)
        
        # Construct command
        # Use the marker_single from the same environment as the current python process
        import sys
        venv_bin = Path(sys.executable).parent
        marker_cmd = venv_bin / "marker_single"
        
        cmd = [
            str(marker_cmd),
            str(pdf_path),
            "--output_dir",
            str(output_dir)
        ]
        
        print(f"Running Marker: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running marker: {e.stderr.decode()}")
            raise e

        # Read the output markdown
        # Marker usually creates [filename].md in the output directory
        md_file = output_dir / f"{pdf_path.stem}.md"
        if not md_file.exists():
            # Fallback: check if it's named differently or inside another subfolder
            # Sometimes it creates a subfolder with the ID
            found_mds = list(output_dir.glob("**/*.md"))
            if found_mds:
                md_file = found_mds[0]
            else:
                raise FileNotFoundError(f"Marker output not found in {output_dir}")
        
        content = md_file.read_text(encoding="utf-8")
        
        # Cleanup temp dir if needed, or keep for debugging
        # shutil.rmtree(output_dir) 
        
        return content, {"images_path": output_dir}
