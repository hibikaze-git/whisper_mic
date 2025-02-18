#!/usr/bin/env python3
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

import click
import torch
import speech_recognition as sr
from typing import Optional

from whisper_mic import WhisperMic

print(torch.cuda.get_device_name(0))
#print(torch.cuda.get_device_name(1))


@click.command()
@click.option(
    "--model",
    default="base",
    help="Model to use",
    type=click.Choice(["tiny", "base", "small", "medium", "large", "large-v2"]),
)
@click.option(
    "--device",
    default=("cuda:0" if torch.cuda.is_available() else "cpu"),
    help="Device to use",
    type=click.Choice(["cpu", "cuda", "mps", "cuda:0", "cuda:0"]),
)
@click.option("--english", default=False, help="Whether to use English model", is_flag=True, type=bool)
@click.option("--verbose", default=False, help="Whether to print verbose output", is_flag=True, type=bool)
@click.option("--energy", default=300, help="Energy level for mic to detect", type=int)
@click.option("--dynamic_energy", default=False, is_flag=True, help="Flag to enable dynamic energy", type=bool)
@click.option("--pause", default=0.8, help="Pause time before entry ends", type=float)
@click.option("--save_file", default=False, help="Flag to save file", is_flag=True, type=bool)
@click.option("--loop", default=False, help="Flag to loop", is_flag=True, type=bool)
@click.option("--dictate", default=False, help="Flag to dictate (implies loop)", is_flag=True, type=bool)
@click.option("--mic_index", default=None, help="Mic index to use", type=int)
@click.option("--list_devices", default=False, help="Flag to list devices", is_flag=True, type=bool)
@click.option("--vrchat", default=False, help="Flag to send vrchat", is_flag=True, type=bool)
def main(
    model: str,
    english: bool,
    verbose: bool,
    energy: int,
    pause: float,
    dynamic_energy: bool,
    save_file: bool,
    device: str,
    loop: bool,
    dictate: bool,
    mic_index: Optional[int],
    list_devices: bool,
    vrchat: bool
) -> None:
    if list_devices:
        print("Possible devices: ", sr.Microphone.list_microphone_names())
        return
    mic = WhisperMic(
        model=model,
        english=english,
        verbose=verbose,
        energy=energy,
        pause=pause,
        dynamic_energy=dynamic_energy,
        save_file=save_file,
        device=device,
        mic_index=mic_index,
        model_root="./cache",
        vrchat=vrchat
    )
    if not loop:
        result = mic.listen()
        print("You said: " + result)
    else:
        mic.listen_loop(dictate=dictate, phrase_time_limit=2)


if __name__ == "__main__":
    main()
