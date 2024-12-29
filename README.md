# Voice-Controlled Chess Bot

![Demo](Demo_of_app.mp4)

## Overview
A voice-controlled chess application that allows you to play chess against Stockfish engine using voice commands in Russian. The app uses OpenAI's GPT-4 Audio model (Whisper + 3.5-turbo) for speech recognition and move interpretation from regular speach.

## Features
- Voice control in Russian language
- Move validation and illegal move detection
- Game state logging to moves.txt
- Final position recording
- Configurable player color (White/Black)
- Voice feedback for computer moves
- Adjustable engine strength (ELO rating, thinking time etc.)

## Requirements
- Python 3.12+
- Stockfish chess engine
- OpenAI API key to OpenAI project with Whisper and 3.5-turbo models enabled
- FLAC audio codec

## Installation
1. Install Stockfish (f.e. via brew):
```bash
brew install stockfish
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
```

## Usage
1. To play as White:
```bash
python main.py
```

2. To play as Black:
```bash
python main.py PLAY_WHITE=FALSE
```

3. Speak your moves in Russian using standard algebraic notation (e.g., "<any words and among them smth like "e-2-e-4">")

## Game Logging
All moves are logged to `moves.txt` in the following format:
```
Game: YYYY-MM-DD HH:MM:SS
I play White/Black, Computer plays Black/White

1. e2e4 - e7e5
2. g1f3 - b8c6
...

Position game finished with:

Game: 2024-12-29 17:39:01
I play White, Computer plays Black

1. d2d4 - g8f6
2. e2e3 - d7d5
3. a2a3 - c8f5
4. g1f3 - e7e6
5. c2c4 - c7c6
...
27. g1h1 - c7g3
28. a1c1 - d7b7
29. a6d3 - b7b3
30. d3b3 - b8b3
31. c1d1 - b3e3
32. f3d4 - e3c3

Current board position:
+---+---+---+---+---+---+---+---+
| K |   | R |   | R |   |   |   | 1
+---+---+---+---+---+---+---+---+
|   | P |   |   |   |   | r |   | 2
+---+---+---+---+---+---+---+---+
| P | b |   |   |   | r |   | P | 3
+---+---+---+---+---+---+---+---+
|   |   |   |   | N |   |   |   | 4
+---+---+---+---+---+---+---+---+
|   |   |   |   | p | P |   |   | 5
+---+---+---+---+---+---+---+---+
| p |   |   | p |   | p |   |   | 6
+---+---+---+---+---+---+---+---+
|   | p | p |   |   |   |   | p | 7
+---+---+---+---+---+---+---+---+
|   | k |   |   |   |   |   |   | 8
+---+---+---+---+---+---+---+---+
  h   g   f   e   d   c   b   a

DEBUG:__main__:Getting evaluation
Evaluation: {'type': 'cp', 'value': -493}
``` 