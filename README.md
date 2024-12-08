# Houdini Flipbook Automation  

This project provides an automated workflow using Houdini's Flipbook feature. The workflow includes setting custom resolutions, saving render information as a JSON file, converting outputs to MOV format using FFmpeg, and previewing the MOV file directly in the file explorer.  

## Features  
- **Custom Resolution**: Adjust the Flipbook's resolution for high-quality output.  
- **JSON File Output**: Save render settings and details into a JSON file for reuse or reference.  
- **MOV File Conversion**: Convert image sequences into an MOV file using FFmpeg.  
- **File Explorer Integration**: Easily preview the MOV file directly in your file explorer.  

## How It Works  
1. **Set Resolution**: Define the desired resolution in the Flipbook settings.  
2. **Generate Flipbook**: Render the Flipbook and save metadata as a JSON file.  
3. **Convert to MOV**: Use FFmpeg to convert the image sequence into a video file.  
4. **Preview Video**: Open the MOV file directly from the output directory in the file explorer.  

## Prerequisites  
- Houdini (version X.X or higher).  
- FFmpeg installed and added to the system PATH.  

## Getting Started  
1. Clone this repository.  
2. Open the Houdini project file and configure Flipbook settings as needed.  
3. Run the automation script to generate outputs and preview the results.  

## Example Command for FFmpeg  
```bash
ffmpeg -framerate 24 -i output_%04d.png -c:v libx264 -pix_fmt yuv420p output.mov
