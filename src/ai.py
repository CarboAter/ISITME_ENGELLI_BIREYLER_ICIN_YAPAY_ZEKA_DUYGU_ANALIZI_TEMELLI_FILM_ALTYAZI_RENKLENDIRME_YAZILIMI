if __name__ != "__main__":

    import openai
    from openai.error import RateLimitError
    from whisper.utils import get_writer
    import whisper
    import numpy as np
    import keras
    import librosa
    import json

    import gui

    openai.api_key = "YOUR_API_KEY"

    colors = ["white", "aquamarine1", "DarkOrange1", "RoyalBlue1", "Red", "Purple", "GreenYellow", "Gold1"]

    label_conversion = {'0': 'neutral',
                        '1': 'calm',
                        '2': 'happy',
                        '3': 'sad',
                        '4': 'angry',
                        '5': 'fearful',
                        '6': 'disgust',
                        '7': 'surprised'}

    class livePredictions:
        """
        Main class of the application.
        """

        def __init__(self, path, file):
            """
            Init method is used to initialize the main parameters.
            """
            self.path = path
            self.file = file

        def load_model(self):
            """
            Method to load the chosen model.
            :param path: path to your h5 model.
            :return: summary of the model with the .summary() function.
            """
            livePredictions.loaded_model = keras.models.load_model(self.path)
            return self.loaded_model.summary()

        def makepredictions(self):
            """
            Method to process the files and create your features.
            """
            data, sampling_rate = librosa.load(self.file)
            mfccs = np.mean(librosa.feature.mfcc(y = data, sr = sampling_rate, n_mfcc = 40).T, axis = 0)
            x = np.expand_dims(mfccs, axis = 1)
            x = np.expand_dims(x, axis = 0)
            predict_x = self.loaded_model.predict(x) 
            predictions = np.argmax(predict_x, axis = 1)
            return predictions

        @staticmethod
        def convertclasstoemotion(pred):
            """
            Method to convert the predictions (int) into human readable strings.
            """

            for key, value in label_conversion.items():
                if int(key) == pred:
                    label = value
            return label

    def chat_with_bot(sentence, emotion_from_audio, srt):
        try:
            response = openai.ChatCompletion.create(
                model = "gpt-3.5-turbo",  # Use the appropriate chat model here
                messages = [{"role": "system", "content": f""}, {"role": "user", "content": f"You will now recieve a segment of a transcript of an audio transcripted by Whisper. You will analyse it and give back a color related to the strongest emotion: (0: neutral, 1: calm, 2:happy, 3:sad, 4:angry, 5:fearful, 6:disgust, 7:surprised) Here is the full SRT file ({srt}) so you can understand the context better. An audio sentiment recognition AI gave the output {emotion_from_audio} so make your desicion by considering that adn the context of the speech. Give your answer in JSON format, just giving the emotion number. IF THERE ARE NO ACTIVE EMOTIONS, RETURN 0(NEUTRAL)! Example: emotion:1. | The sentence: {sentence}   "}],
                max_tokens = 10  # You can adjust this value to control response length
            )

            bot_response = response.choices[0].message['content'].strip()
            try:
                return json.loads(bot_response)
            except:
                return {"emotion": 0}
        except:
            return {"emotion": 0}

    def transcribe_audio(audio):
        try:
            model = whisper.load_model("medium")
            result = model.transcribe(audio)

            srt_writer = get_writer("srt", gui.save_location_value)
            srt_writer(result, audio)
            print("SRT file creation done.")

        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"