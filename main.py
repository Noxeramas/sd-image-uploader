import discord
import os
import time
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
import numpy as np
import onnxruntime as ort
import csv

TOKEN = 'YOUR DISCORD BOT TOKEN HERE'
FOLDER_PATH = 'PATH TO OUTPUT FOLDER'
CHANNEL_MAP = {
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Load the model using ONNX Runtime
model_path = './model.onnx'
csv_path = './selected_tags.csv'
model = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

# Read tags from CSV
tags = []
rating_indexes = []
general_indexes = []
character_indexes = []

with open(csv_path) as f:
    reader = csv.reader(f)
    next(reader)
    for idx, row in enumerate(reader):
        tags.append(row[1])
        if row[2] == "9":
            rating_indexes.append(idx)
        elif row[2] == "0":
            general_indexes.append(idx)
        elif row[2] == "4":
            character_indexes.append(idx)


def get_image_tags_and_nsfw_status(file_path):
    image = Image.open(file_path)
    # Preprocess the image
    input = model.get_inputs()[0]
    height = input.shape[1]

    ratio = float(height) / max(image.size)
    new_size = tuple([int(x * ratio) for x in image.size])
    image = image.resize(new_size, Image.LANCZOS)
    square = Image.new("RGB", (height, height), (255, 255, 255))
    square.paste(image, ((height - new_size[0]) // 2, (height - new_size[1]) // 2))

    image = np.array(square).astype(np.float32)
    image = image[:, :, ::-1]  # RGB -> BGR
    image = np.expand_dims(image, 0)

    # Run the model
    label_name = model.get_outputs()[0].name
    probs = model.run([label_name], {input.name: image})[0]

    result = list(zip(tags, probs[0]))

    general = [item for item in result if item[1] > 0.35 and result.index(item) in general_indexes]
    character = [item for item in result if item[1] > 0.85 and result.index(item) in character_indexes]

    all_tags = character + general
    detected_tags = [tag[0] for tag in all_tags]

    ratings = {tags[i]: probs[0][i] for i in rating_indexes}
    is_nsfw = any(ratings.get(tag, 0) > 0.5 for tag in ["questionable", "explicit"])
    print(f'Ratings: {ratings}')
    print(f'Detected tags: {detected_tags}')
    print(f'NSFW status: {is_nsfw}')
    return detected_tags, is_nsfw


def determine_channels(tags, is_nsfw):
    channels = [CHANNEL_MAP['default']]
    # change any logic needed for your bot
    if 'xyz' in tags:
        channels.append(CHANNEL_MAP['default'])

    for tag in tags:
        if tag in CHANNEL_MAP:
            if is_nsfw and 'nsfw' in CHANNEL_MAP[tag]:
                channels.append(CHANNEL_MAP[tag]['nsfw'])
            elif not is_nsfw and 'sfw' in CHANNEL_MAP[tag]:
                channels.append(CHANNEL_MAP[tag]['sfw'])

    if is_nsfw:
        # Ensure we include all NSFW channels if the content is NSFW
        for category in CHANNEL_MAP.values():
            if 'nsfw' in category:
                channels.append(category['nsfw'])
    else:
        # Ensure we include all SFW channels if the content is SFW
        for category in CHANNEL_MAP.values():
            if 'sfw' in category:
                channels.append(category['sfw'])

    print(f'Channels determined: {channels}')
    return list(set(channels))  # Remove duplicates


async def post_image(file_path, channel_ids):
    for channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        if channel:
            with open(file_path, 'rb') as f:
                picture = discord.File(f)
                await channel.send(file=picture)
    # os.remove(file_path) if we want to delete the file


@client.event
async def on_ready():
    print(f'Bot is ready as {client.user}')
    event_handler = NewFileHandler(loop=client.loop)
    observer = Observer()
    observer.schedule(event_handler, FOLDER_PATH, recursive=False)
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if file_path.endswith(('.png', '.jpg', '.jpeg')):
            # Wait until the file size stabilizes
            initial_size = -1
            while True:
                current_size = os.path.getsize(file_path)
                if current_size == initial_size:
                    break
                initial_size = current_size
                time.sleep(1)
            # Process the image
            tags, is_nsfw = get_image_tags_and_nsfw_status(file_path)
            channel_ids = determine_channels(tags, is_nsfw)
            asyncio.run_coroutine_threadsafe(post_image(file_path, channel_ids), self.loop)


client.run(TOKEN)
