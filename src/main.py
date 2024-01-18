import time

def main():
    import gui
    import ai
    import srt_creator
    
    start_time = time.time()

    ai.transcribe_audio(gui.audio_location_value)
    
    transcription_time = time.time()
    
    audio_emotions = srt_creator.extract_audio_clips()
    
    audio_emotion_predictions_time = time.time()
    
    gui.audio_emotions = audio_emotions

    srt_creator.add_color_to_srt(gui.raw_srt_location_value, gui.colored_srt_location_value)
    
    colorization_time = time.time()

    srt_creator.create_file()
    
    video_creation_time = time.time()


    end_time = time.time()
    runtime = end_time - start_time
    print(f"Transcription Runtime: {transcription_time - start_time}")
    print(f"Audio Emotion Predictions Runtime: {audio_emotion_predictions_time - transcription_time}")
    print(f"SRT Colorization Runtime: {colorization_time - audio_emotion_predictions_time}")
    print(f"Video Creation Runtime: {video_creation_time - colorization_time}")
    print(f"Total Runtime: {runtime} seconds")

if __name__ == "__main__":
    main()