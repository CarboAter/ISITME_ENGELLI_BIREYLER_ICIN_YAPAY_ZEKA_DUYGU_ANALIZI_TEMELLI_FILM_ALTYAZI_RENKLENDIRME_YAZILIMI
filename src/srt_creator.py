if __name__ != "__main__":
    
    import os
    import re
    import pysrt
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    from pydub import AudioSegment
    from dateutil import parser

    import gui
    import ai

    def timestamp_to_milliseconds(timestamp):
        dt = parser.parse(timestamp.replace(",", "."))
        if dt.microsecond == 0:
            dt = dt.replace(microsecond=0)

        total_milliseconds = int((dt.hour * 3600 + dt.minute * 60 + dt.second) * 1000 + dt.microsecond / 1000)
        return total_milliseconds

    def get_timestamps_from_srt(n):
        with open(gui.raw_srt_location_value, 'r', encoding='utf-8') as file:
            srt_content = file.read()

        # Using regular expression to extract start and end timestamps from SRT format
        timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
        matches = timestamp_pattern.findall(srt_content)

        # Check if the requested index is within the range of available timestamps
        if 1 <= n <= len(matches):
            start_timestamp, end_timestamp = matches[n - 1]
            return [start_timestamp, end_timestamp]
        else:
            return ["Done", "Done"]

    def extract_audio_clips():
        audio_emotions = []
        ctr = 0
        while True:
            ctr += 1
            start_timestamp, end_timestamp = get_timestamps_from_srt(ctr)
            if start_timestamp == "Done":
                break

            # Load the entire audio file
            audio = AudioSegment.from_file(gui.audio_location_value, format="mp3")

            # Convert timestamps to milliseconds
            start_time = timestamp_to_milliseconds(start_timestamp)
            end_time = timestamp_to_milliseconds(end_timestamp)

            # Extract the audio clip
            audio_clip = audio[start_time:end_time]

            # Save the audio clip to a new file
            audio_clip.export(gui.save_location_value + f"/{ctr}.mp3", format="mp3")

            file_path = os.path.abspath(__file__)
            src_directory = os.path.dirname(file_path)
            models_directory = os.path.join(src_directory, "..", "models")
            model_file_path = os.path.join(models_directory, "SER_model.h5")
            
            pred = ai.livePredictions(path = model_file_path, file = gui.save_location_value + f"/{ctr}.mp3")

            pred.load_model()
            audio_emotions.append(pred.makepredictions())

        return audio_emotions

    def add_color_to_srt(input_file, output_file):
        with open(input_file, 'r', encoding = "utf-8") as infile, open(output_file, 'w', encoding = "utf-8") as outfile:
            lines = infile.readlines()
            iterator = iter(lines)
            ctr = 0
            for line in iterator:
                if re.match(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+', line):
                    # This line contains timestamps, add '#{emotioin}' to the next line
                    outfile.write(line)
                    try:
                        next_line = next(iterator)
                        response = ai.chat_with_bot(next_line, gui.audio_emotions[ctr], lines)
                        scolor = ai.colors[response["emotion"]]
                        outfile.write(next_line.rstrip() + f"#{scolor}\n")
                    except StopIteration:
                        pass  # No more lines to read
                    ctr += 1
                else:
                    outfile.write(line)

    def clean_text(subtitle):
        parts = subtitle.rsplit("#", 1)
        if len(parts) > 1:
            return parts[0].strip()
        else:
            return subtitle.strip()

    def find_color(subtitle):
        last_hash_index = subtitle.rfind('#')

        if last_hash_index != -1:
            color = subtitle[last_hash_index + 1:].strip()
            return color
        else:
            return None

    def time_to_seconds(time_obj):
        return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

    def create_subtitle_clips(subtitles, videosize, fontsize = 28, font = "Arial", debug = False):
        subtitle_clips = []

        for subtitle in subtitles:
            start_time = time_to_seconds(subtitle.start)
            end_time = time_to_seconds(subtitle.end)
            scolor = find_color(subtitle.text)
            subtitle.text = clean_text(subtitle.text)
            duration = end_time - start_time

            video_width, video_height = videosize
            text_clip = TextClip(subtitle.text, fontsize = fontsize, font = font, color = scolor, bg_color = "black",
            size=(None,None ), method = "label").set_start(start_time).set_duration(duration)
            subtitle_x_position = "center"
            subtitle_y_position = video_height * 9 / 10

            text_position = (subtitle_x_position, subtitle_y_position)
            subtitle_clips.append(text_clip.set_position(text_position))

        return subtitle_clips

    def create_file():
        subtitles = pysrt.open(gui.colored_srt_location_value, "utf-8")
        if gui.video_location_value != "":
            subtitle_clips = create_subtitle_clips(subtitles, VideoFileClip(gui.video_location_value).size)
            final_video = CompositeVideoClip([VideoFileClip(gui.video_location_value)] + subtitle_clips)
            final_video.write_videofile(gui.subtitled_location_value)