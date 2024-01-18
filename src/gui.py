if __name__ != "__main__":

    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from pytube import YouTube
    from moviepy.editor import *

    def create_subtitles_window():
        def checkbox_state_change():
            youtube_link_state.set(youtube_link_var.get())
            if youtube_link_var.get():
                youtube_link_entry.config(state = "normal")
                browse_video_button.config(state = "disabled")
            else:
                youtube_link_entry.config(state = "disabled")
                browse_video_button.config(state = "normal")
            update_submit_button_state()

        def youtube_link_entry_change(*args):
            update_submit_button_state()

        def browse_save_location():
            save_location = filedialog.askdirectory()
            if save_location:
                save_location_text.set(save_location)
                update_submit_button_state()

        def browse_video():
            video_location = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
            if video_location:
                video_location_entry_text.set(video_location)
                update_submit_button_state()

        def update_submit_button_state():
            youtube_link_value = youtube_link_entry_text.get()
            youtube_checkbox_value = youtube_link_state.get()
            save_location_value = save_location_text.get()
            video_location_value = video_location_entry_text.get()

            if (youtube_checkbox_value and youtube_link_value.startswith("https://www.youtube.com/")) or \
               (not youtube_checkbox_value and video_location_value):
                browse_save_location_button.config(state = "normal")
            else:
                browse_save_location_button.config(state = "disabled")

            if ((youtube_checkbox_value and youtube_link_value.startswith("https://www.youtube.com/")) or
               (not youtube_checkbox_value and video_location_value)) and save_location_value:
                submit_button.config(state = "normal")
            else:
                submit_button.config(state = "disabled")

        def subtitles_window_submit_clicked():
            try:
                youtube_link_state_value = youtube_link_state.get()
                youtube_link_value = youtube_link_entry_text.get()
                save_location_value = save_location_text.get()
                video_location_value = video_location_entry_text.get()

                if youtube_link_state_value == True:
                    video = YouTube(youtube_link_value)
                    stream = video.streams.get_highest_resolution()
                    stream.download(save_location_value, "raw_video.mp4")
                    video_location_value = save_location_value + "/raw_video.mp4"
                    print("Video download done.")
                move = True

            except:
                messagebox.showerror("Python Error", "An error occured while downloading the video! What you can do:\n1. Check if you are connected to the internet.\n2. Check if the link you provided is correct.")
                move = False

            try:
                if move == True:
                    subtitles_window.destroy()
            except tk.TclError:
                pass  # Ignore the error if the window has already been destroyed

            return (
                youtube_link_state_value,
                youtube_link_value,
                video_location_value,
                save_location_value,
            )

        subtitles_window = tk.Tk()
        subtitles_window.title("Subtitles Configuration")

        youtube_link_var = tk.BooleanVar()
        youtube_link_state = tk.BooleanVar()
        youtube_link_entry_text = tk.StringVar()
        video_location_entry_text = tk.StringVar()
        save_location_text = tk.StringVar()

        youtube_link_checkbox = tk.Checkbutton(subtitles_window, text = "Youtube Link", variable = youtube_link_var)
        youtube_link_label = tk.Label(subtitles_window, text = "YouTube Video Link:")
        youtube_link_entry = tk.Entry(subtitles_window, state = "disabled", textvariable = youtube_link_entry_text)

        youtube_link_var.trace("w", lambda *args: checkbox_state_change())
        youtube_link_entry_text.trace("w", youtube_link_entry_change)

        browse_video_button = tk.Button(subtitles_window, text = "Browse Video", command = browse_video, state = "normal")
        video_location_label = tk.Label(subtitles_window, textvariable = video_location_entry_text)

        browse_save_location_button = tk.Button(subtitles_window, text = "Browse Save Location", command = browse_save_location, state = "disabled")
        save_location_label = tk.Label(subtitles_window, textvariable = save_location_text)

        submit_button = tk.Button(subtitles_window, text = "Submit", command = subtitles_window_submit_clicked, state = "disabled")


        youtube_link_checkbox.pack()
        youtube_link_label.pack()
        youtube_link_entry.pack()
        browse_video_button.pack()
        video_location_label.pack()
        browse_save_location_button.pack()
        save_location_label.pack()
        submit_button.pack()

        subtitles_window.mainloop()

        return subtitles_window_submit_clicked()

    result = create_subtitles_window()

    # Get the results
    if result is not None:
        youtube_link_state_value, youtube_link_value, video_location_value, save_location_value = result
        print(f"Youtube Checkbox Checked: {youtube_link_state_value}")
        print(f"Youtube Link: {youtube_link_value}")
        print(f"Video Location: {video_location_value}")
        print(f"Save Location: {save_location_value}")
        audio_location_value = save_location_value + "/raw_audio.mp3"
        raw_srt_location_value = save_location_value + "/raw_audio.srt"
        colored_srt_location_value = save_location_value + "/colored_subtitles.srt"
        subtitled_location_value = save_location_value + "/subtitled_video.mp4"
        video = VideoFileClip(video_location_value)
        audio = video.audio
        audio.write_audiofile(audio_location_value)
        print("Audio Extraction done.")