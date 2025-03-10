import os
import soundfile as sf
import numpy as np

def merge_audio_clips(folder_path, output_path=None):
    """
    Merges all MP3 files in the specified folder into a single MP3 file.
    
    Args:
        folder_path: Path to the folder containing MP3 files
        output_path: Path for the output merged MP3 file (default: folder_path/merged_output.mp3)
    
    Returns:
        Path to the merged audio file
    """
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder path does not exist: {folder_path}")
    
    # If output path not specified, create one in the same folder
    if output_path is None:
        output_path = os.path.join(folder_path, "merged_output.mp3")
    
    # Find all MP3 files in the folder
    mp3_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.mp3'):
            mp3_files.append(os.path.join(folder_path, file))
    
    if not mp3_files:
        raise ValueError(f"No MP3 files found in {folder_path}")
    
    # Sort the files to ensure consistent ordering
    mp3_files.sort()
    
    # Read the first file to get sample rate
    data_list = []
    sample_rate = None
    
    for mp3_file in mp3_files:
        data, sr = sf.read(mp3_file)
        if sample_rate is None:
            sample_rate = sr
        elif sr != sample_rate:
            raise ValueError(f"MP3 file {mp3_file} has different sample rate")
        
        # Convert to mono if stereo
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        
        data_list.append(data)
    
    # Concatenate all audio data
    merged_data = np.concatenate(data_list)
    
    # Write the merged data
    sf.write(output_path, merged_data, sample_rate)
    print(f"Merged {len(mp3_files)} audio clips into {output_path}")
    
    return output_path

#python3 audio/merge_audio_clips.py /Users/kodykendall/SoftEngineering/story/agents 
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        merge_audio_clips(folder_path, output_path)
    else:
        print("Usage: python merge_audio_clips.py <folder_path> [output_path]")