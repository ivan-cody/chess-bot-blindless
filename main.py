import os
import sys
import time
import openai
import pyttsx3
import logging
import speech_recognition as sr
from dotenv import load_dotenv
from stockfish import Stockfish

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set path to system FLAC
os.environ['FLAC_PATH'] = '/opt/homebrew/bin/flac'

IS_PLAYING_WHITE = True

def speak_text(text, rate=130):
    """Speak text aloud at a given rate using pyttsx3."""
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('voice', 'com.apple.voice.compact.ru-RU.Milena')

    engine.say(text)
    engine.runAndWait()

def transcribe_user_move():
    """
    Listen to microphone input and use Whisper + GPT-3.5-turbo for move recognition.
    Expects a move in standard algebraic notation like 'e2e4'.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Произнесите ваш ход. Слушаю...")
        # Wait for sound before starting to record
        print("Настраиваю микрофон...")
        r.adjust_for_ambient_noise(source, duration=1.0)
        r.dynamic_energy_threshold = False  # Use fixed threshold
        r.energy_threshold = 200  # Fixed threshold value
        r.pause_threshold = 2.0    # Wait for 2 seconds of silence to stop recording
        
        print("Готов к записи. Говорите...")
        # Now record the actual move
        try:
            print("Начинаю запись...")
            audio = r.listen(source, timeout=None, phrase_time_limit=10)  # Maximum 10 seconds for a move
            print("Запись окончена, распознаю...")
        except sr.WaitTimeoutError:
            print("Не удалось услышать ход. Пожалуйста, говорите громче.")
            return ""

    try:
        # Save audio to temporary file
        temp_wav = "temp_recording.wav"
        with open(temp_wav, "wb") as f:
            f.write(audio.get_wav_data())

        # Transcribe audio using Whisper
        with open(temp_wav, "rb") as audio_file:
            transcription = openai.Audio.transcribe(
                "whisper-1",
                audio_file,
                prompt="В этом аудио может быть текст с шахматным ходом. Сохрани как есть."
            )

        # Get text from transcription
        audio_text = transcription["text"]
        print(f"Transcribed text: {audio_text}")

        # Extract chess move using GPT-3.5-turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — ассистент, который умеет извлекать из текста только шахматный ход. "
                        "При этом учитывай русские буквы и их соответствие английским в ходах:"
                        "А = a"
                        "Э = a"
                        "Б = b"
                        "С = c"
                        "Ц = c"
                        "Д = d"
                        "И = e"
                        "Е = e"
                        "Ф = f"
                        "Ж = g"
                        "Ш = h"
                        "Ч = h"
                        "Щ = h"
                        "Ответ должен быть строго в формате хода, например e2e4."
                        "Никакого другого текста, только сам ход с правильно преобразованными буквами. Если нет хода, то ответ пустой."
                        "То есть строго формат e2e4, или пустой ответ."
                    )
                },
                {
                    "role": "user",
                    "content": audio_text
                }
            ],
            temperature=0
        )

        # Get the extracted move
        recognized_text = response.choices[0].message["content"].lower().strip()
        print(f"Extracted move: {recognized_text}")
        return recognized_text
    except Exception as e:
        print(f"Error while transcribing audio: {e}")
        return ""

def show_board(stockfish):
    print(stockfish.get_board_visual(IS_PLAYING_WHITE))

def log_move(move_number, white_move, black_move=None):
    """Log moves to moves.txt file"""
    with open("moves.txt", "a") as f:
        if black_move:
            f.write(f"{move_number}. {white_move} - {black_move}\n")
        else:
            f.write(f"{move_number}. {white_move} - \n")

def check_game_state(stockfish):
    """Check if the game has ended and announce the result"""
    logger.debug("Getting evaluation")
    evaluation = stockfish.get_evaluation()
    print("Evaluation:", evaluation)
    result = None
    
    if evaluation['type'] == 'mate' and evaluation['value'] == 0:
        result = "Мат! Игра окончена."
    
    if result:
        print(result)
        speak_text(result, rate=120)
        return True
    return False

def log_final_position(stockfish):
    """Log the final board position to moves.txt"""
    with open("moves.txt", "a") as f:
        f.write("\nPosition game finished with:\n")
        f.write(stockfish.get_board_visual(IS_PLAYING_WHITE))
        f.write("\n")

def main():
    global IS_PLAYING_WHITE
    load_dotenv()  # Load environment variables from .env
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Clear and initialize moves.txt at the start of a new game
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("moves.txt", "w") as f:
        f.write(f"Game: {current_time}\n")
        if IS_PLAYING_WHITE:
            f.write("I play White, Computer plays Black\n\n")
        else:
            f.write("I play Black, Computer plays White\n\n")

    # Parse PLAY_WHITE=TRUE/FALSE from sys.argv
    # To play as Black, run the script with the argument: PLAY_WHITE=FALSE
    # Example: python main.py PLAY_WHITE=FALSE
    # To play as White, run the script with the argument: PLAY_WHITE=TRUE
    # Example: python main.py PLAY_WHITE=TRUE
    for arg in sys.argv:
        if arg.upper() == "PLAY_WHITE=FALSE":
            IS_PLAYING_WHITE = False
        elif arg.upper() == "PLAY_WHITE=TRUE":
            IS_PLAYING_WHITE = True

    stockfish_path = "/opt/homebrew/bin/stockfish"
    logger.debug(f"Using Stockfish at: {stockfish_path}")
    logger.debug(f"Stockfish exists: {os.path.exists(stockfish_path)}")
    logger.debug(f"Stockfish is executable: {os.access(stockfish_path, os.X_OK)}")

    # Initialize Stockfish
    try:
        stockfish = Stockfish(
            path=stockfish_path,
            depth=15,
            parameters={
                "Debug Log File": "",
                "Contempt": 0,
                "Min Split Depth": 0,
                "Threads": 1, # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
                "Ponder": "false",
                "Hash": 32, # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
                "MultiPV": 1,
                "Skill Level": 20,
                "Move Overhead": 10,
                "Minimum Thinking Time": 20,
                "Slow Mover": 100,
                "UCI_Chess960": "false",
                "UCI_LimitStrength": "false"
            }
        )
        logger.debug("Stockfish initialized successfully")
        stockfish.set_elo_rating(1150)
        logger.debug("Stockfish ELO set")
        initial_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        stockfish.set_fen_position(initial_fen)
        logger.debug("Stockfish initial position set")
    except Exception as e:
        logger.error(f"Error initializing Stockfish: {e}")
        raise

    print("Starting a new game of blindfold chess!")
    print("Playing as White" if IS_PLAYING_WHITE else "Playing as Black")
    speak_text("Начинаем новую партию. Вы играете " + ("белыми" if IS_PLAYING_WHITE else "черными"), rate=120)

    # A simple turn indicator: True -> White to move, False -> Black to move
    white_to_move = True  # Start with White to move in standard chess

    move_number = 1
    last_white_move = None

    while True:
        try:
            # Print board & evaluation
            print("\nCurrent board position:")
            show_board(stockfish)

            # Check game state after each move
            if check_game_state(stockfish):
                log_final_position(stockfish)
                break

            # Check if Stockfish can continue:
            logger.debug("About to get best move")
            best_move = stockfish.get_best_move_time(10)  # quick check
            if best_move is None or best_move == "":
                print("No possible moves. Game over.")
                speak_text("Игра окончена. Нет возможных ходов.", rate=120)
                log_final_position(stockfish)
                break

            if white_to_move == IS_PLAYING_WHITE:
                print("Your turn!")
                move_made = False
                while not move_made:
                    move_input = transcribe_user_move()
                    # Clean up recognized move, just in case
                    move_input = move_input.replace(" ", "").lower()

                    # Attempt the move if it's presumably valid format
                    if len(move_input) == 4:  # e2e4 or e7e8q
                        # Let's try to make the move
                        print(f"Making move: {move_input}")
                        if stockfish.is_move_correct(move_input):
                            # Store position before move
                            position_before = stockfish.get_fen_position()
                            stockfish.make_moves_from_current_position([move_input])
                            # Check if position actually changed
                            position_after = stockfish.get_fen_position()
                            
                            if position_before != position_after:
                                print(f"Made move: {move_input}")
                                move_made = True
                                show_board(stockfish)
                                if IS_PLAYING_WHITE:
                                    last_white_move = move_input
                                else:
                                    log_move(move_number, last_white_move, move_input)
                                    move_number += 1
                            else:
                                print(f"Illegal move '{move_input}'. Please retry.")
                                speak_text("Этот ход невозможен, попробуйте снова", rate=120)
                        else:
                            print(f"Illegal move '{move_input}'. Please retry.")
                            speak_text("Этот ход невозможен, попробуйте снова", rate=120)
                    else:
                        print(f"Unrecognized or invalid format move '{move_input}'. Please retry.")
                        speak_text("Этот ход невозможен, попробуйте снова", rate=120)
            else:
                # It's Stockfish's move
                best_move = stockfish.get_best_move_time(1000)
                if best_move is None or best_move == "":
                    print("No possible moves. Game over.")
                    break
                print(f"Engine plays: {best_move}")
                # Make the move
                stockfish.make_moves_from_current_position([best_move])
                # Speak the move in Russian
                move_announcement = f"Я хожу {best_move[0].upper()} {best_move[1]} на {best_move[2].upper()} {best_move[3]}"
                speak_text(move_announcement, rate=90)
                
                if IS_PLAYING_WHITE:
                    log_move(move_number, last_white_move, best_move)
                    move_number += 1
                else:
                    last_white_move = best_move

            # Switch turn
            white_to_move = not white_to_move

            # Optional small delay to avoid frantic looping
            time.sleep(1)

        except KeyboardInterrupt:
            print("\nGame interrupted by user. Exiting.")
            try:
                # Try to log final position before closing Stockfish
                final_position = stockfish.get_board_visual(IS_PLAYING_WHITE)
                with open("moves.txt", "a") as f:
                    f.write("\nPosition game finished with:\n")
                    f.write(final_position)
                    f.write("\n")
            except Exception as e:
                logger.error(f"Failed to log final position: {e}")
            break
        except Exception as e:
            logger.error(f"Error during game: {e}")
            try:
                # Try to log final position before closing Stockfish
                final_position = stockfish.get_board_visual(IS_PLAYING_WHITE)
                with open("moves.txt", "a") as f:
                    f.write("\nPosition game finished with:\n")
                    f.write(final_position)
                    f.write("\n")
            except Exception as log_error:
                logger.error(f"Failed to log final position: {log_error}")
            raise

if __name__ == "__main__":
    main() 