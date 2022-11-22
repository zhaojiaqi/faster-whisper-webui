# External programs
import whisper

class WhisperContainer:
    def __init__(self, model_name: str, device: str = None):
        self.model_name = model_name
        self.device = device

        # Will be created on demand
        self.model = None
    
    def get_model(self):
        if self.model is None:
            print("Loading model " + self.model_name)
            self.model = whisper.load_model(self.model_name, device=self.device)
        return self.model

    def create_callback(self, language: str = None, task: str = None, initial_prompt: str = None, **decodeOptions: dict):
        """
        Create a WhisperCallback object that can be used to transcript audio files.

        Parameters
        ----------
        language: str
            The target language of the transcription. If not specified, the language will be inferred from the audio content.
        task: str
            The task - either translate or transcribe.
        initial_prompt: str
            The initial prompt to use for the transcription.
        decodeOptions: dict
            Additional options to pass to the decoder. Must be pickleable.

        Returns
        -------
        A WhisperCallback object.
        """
        return WhisperCallback(self, language=language, task=task, initial_prompt=initial_prompt, **decodeOptions)

    # This is required for multiprocessing
    def __getstate__(self):
        return { "model_name": self.model_name, "device": self.device }

    def __setstate__(self, state):
        self.model_name = state["model_name"]
        self.device = state["device"]
        self.model = None


class WhisperCallback:
    def __init__(self, model_container: WhisperContainer, language: str = None, task: str = None, initial_prompt: str = None, **decodeOptions: dict):
        self.model_container = model_container
        self.language = language
        self.task = task
        self.initial_prompt = initial_prompt
        self.decodeOptions = decodeOptions
        
    def invoke(self, audio, segment_index: int, prompt: str, detected_language: str):
        """
        Peform the transcription of the given audio file or data.

        Parameters
        ----------
        audio: Union[str, np.ndarray, torch.Tensor]
            The audio file to transcribe, or the audio data as a numpy array or torch tensor.
        segment_index: int
            The target language of the transcription. If not specified, the language will be inferred from the audio content.
        task: str
            The task - either translate or transcribe.
        prompt: str
            The prompt to use for the transcription.
        detected_language: str
            The detected language of the audio file.

        Returns
        -------
        The result of the Whisper call.
        """
        model = self.model_container.get_model()

        return model.transcribe(audio, \
                 language=self.language if self.language else detected_language, task=self.task, \
                 initial_prompt=self._concat_prompt(self.initial_prompt, prompt) if segment_index == 0 else prompt, \
                 **self.decodeOptions)

    def _concat_prompt(self, prompt1, prompt2):
        if (prompt1 is None):
            return prompt2
        elif (prompt2 is None):
            return prompt1
        else:
            return prompt1 + " " + prompt2