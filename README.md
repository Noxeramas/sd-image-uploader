# Image Uploader Discord Bot

This Discord bot monitors a specified folder for new image files and automatically posts these images to the appropriate channels based on their content. The bot uses an AI model to tag the images and determine if they are NSFW (Not Safe For Work) or SFW (Safe For Work).

## Features

- Monitors a folder for new images
- Uses an AI model to tag images and determine NSFW status
- Posts images to specified Discord channels based on their content

## Requirements

- Python 3.8 or higher
- Discord bot token
- ONNX Runtime
- Pillow
- Watchdog
- Numpy
- ONNX model (`wd-v1-4-moat-tagger-v2.onnx`)
- CSV file with tags (`selected_tags.csv`)

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/Noxeramas/sd-image-uploader.git
cd sd-image-uploader
```

2. **Install the required packages:**

```bash
pip install -r requirements.txt
```

## Configuration

1. Set your discord bot token in main.py
2. Set the path to the folder you want to monitor in main.py
3. Set the channel IDs in your channel map in main.py

channel map example
```python
channel_map = {
    "sfw": 1234567890,
    "nsfw": 1234567890
}

#or if you have channel groups

channel_map = {
    "group1": {
        "sfw": 1234567890,
        "nsfw": 1234567890
    },
    "group2": {
        "sfw": 1234567890,
        "nsfw": 1234567890
    }
}
```

## Running the Bot

```bash
python main.py
```

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

Contact
For any questions or issues, please open an issue in the repository or contact the maintainer.