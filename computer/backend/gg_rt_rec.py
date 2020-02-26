#!/usr/bin/env python

# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.
NOTE: This module requires the dependencies `pyaudio` and `termcolor`.
To install using pip:
    pip install pyaudio
    pip install termcolor
Example usage:
    python transcribe_streaming_infinite.py
"""

# [START speech_transcribe_infinite_streaming]

import keyboard as kb

import time
import sys
from threading import Thread, Lock

# uses result_end_time currently only avaialble in v1p1beta, will be in v1 soon
from google.cloud import speech_v1p1beta1 as speech
import pyaudio
from six.moves import queue

# Audio recording parameters
STREAMING_LIMIT = 10000
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'


def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))


class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk_size):
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

    def __enter__(self):

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):

        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def flush(self):
        self._buff.queue.clear()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""

        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Stream Audio from microphone to API and to local buffer"""

        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:

                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:

                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round((self.final_request_end_time -
                                            self.bridging_offset) / chunk_time)

                    self.bridging_offset = (round((
                                                          len(self.last_audio_input) - chunks_from_ms)
                                                  * chunk_time))

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            yield b''.join(data)


class SpeechToTextController:

    def __init__(self, callback):
        self.callback = callback
        self.client = speech.SpeechClient()
        self.config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code='en-US',
            max_alternatives=1)
        self.streaming_config = speech.types.StreamingRecognitionConfig(
            config=self.config,
            interim_results=True)
        self.mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
        self.mutex = Lock()
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            t = Thread(target=self.listen, args=(self,))
            t.start()

    def listen(self, _):
        """start bidirectional streaming from microphone input to speech API"""
        with self.mic_manager as stream:
            stream.flush()
            print("Started listening")
            while self.running:
                stream.audio_input = []
                audio_generator = stream.generator()

                requests = (speech.types.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

                responses = self.client.streaming_recognize(self.streaming_config, requests)

                self.listen_print_loop(responses, stream)

                if stream.result_end_time > 0:
                    stream.final_request_end_time = stream.is_final_end_time
                stream.result_end_time = 0
                stream.last_audio_input = []
                stream.last_audio_input = stream.audio_input
                stream.audio_input = []
                stream.restart_counter = stream.restart_counter + 1

                if not stream.last_transcript_was_final:
                    sys.stdout.write('\n')
                stream.new_stream = True
        print("Finished listening")

    def listen_print_loop(self, responses, stream):
        """Iterates through server responses and prints them.
        The responses passed is a generator that will block until a response
        is provided by the server.
        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.
        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """

        for response in responses:

            if get_current_time() - stream.start_time > STREAMING_LIMIT:
                stream.start_time = get_current_time()
                break

            if not response.results:
                continue

            result = response.results[0]

            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            result_seconds = 0
            result_nanos = 0

            if result.result_end_time.seconds:
                result_seconds = result.result_end_time.seconds

            if result.result_end_time.nanos:
                result_nanos = result.result_end_time.nanos

            stream.result_end_time = int((result_seconds * 1000)
                                         + (result_nanos / 1000000))

            # corrected_time = (stream.result_end_time - stream.bridging_offset
            #                   + (STREAMING_LIMIT * stream.restart_counter))

            if result.is_final:
                self.callback(transcript, True)

                stream.is_final_end_time = stream.result_end_time
                stream.last_transcript_was_final = True
            else:
                self.callback(transcript, False)

                stream.last_transcript_was_final = False

    def stop(self):
        self.mutex.acquire()
        try:
            self.running = False
        finally:
            self.mutex.release()


def callback_displayer(text, final):
    if final:
        print("Final: " + text)
    else:
        print("Potential: " + text)


if __name__ == '__main__':
    controller = SpeechToTextController(callback_displayer)
    kb.on_press_key(80, lambda e: controller.stop())
    kb.on_press_key(75, lambda e: controller.start())
    print("Starting")
    kb.wait('escape')

# [END speech_transcribe_infinite_streaming]
