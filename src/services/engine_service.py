import os
import subprocess
import shutil
import logging
import threading
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer
import sys
from utils.resource_path import resource_path

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_VALID_FEN_PIECES = set('prnbqkPRNBQK')


def _validate_fen(fen: str):
    """
    Validate a FEN string before sending to Stockfish.
    Returns (is_valid, error_message).
    """
    if not fen or not isinstance(fen, str):
        return False, "FEN is empty or not a string"

    parts = fen.split()
    if len(parts) < 2:
        return False, f"FEN has too few fields ({len(parts)})"

    if parts[1] not in ('w', 'b'):
        return False, f"Invalid side-to-move: '{parts[1]}'"

    rows = parts[0].split('/')
    if len(rows) != 8:
        return False, f"FEN has {len(rows)} rows instead of 8"

    white_kings = 0
    black_kings = 0
    white_pieces = 0
    black_pieces = 0
    white_pawns = 0
    black_pawns = 0

    for i, row in enumerate(rows):
        sq = 0
        for ch in row:
            if ch.isdigit():
                sq += int(ch)
            elif ch in _VALID_FEN_PIECES:
                sq += 1
                if ch.isupper():
                    white_pieces += 1
                    if ch == 'K':
                        white_kings += 1
                    elif ch == 'P':
                        white_pawns += 1
                else:
                    black_pieces += 1
                    if ch == 'k':
                        black_kings += 1
                    elif ch == 'p':
                        black_pawns += 1
            else:
                return False, f"Invalid character '{ch}' in row {i + 1}"
        if sq != 8:
            return False, f"Row {i + 1} has {sq} squares instead of 8"

    if white_kings != 1:
        return False, f"White has {white_kings} kings (needs exactly 1)"
    if black_kings != 1:
        return False, f"Black has {black_kings} kings (needs exactly 1)"
    if white_pieces > 16:
        return False, f"White has {white_pieces} pieces (max 16)"
    if black_pieces > 16:
        return False, f"Black has {black_pieces} pieces (max 16)"
    if white_pawns > 8:
        return False, f"White has {white_pawns} pawns (max 8)"
    if black_pawns > 8:
        return False, f"Black has {black_pawns} pawns (max 8)"

    return True, ""


# Global Stockfish process and thread lock
_stockfish_process = None
_stockfish_lock = threading.Lock()
_is_shutting_down = False

def get_root_dir():
    # When bundled by PyInstaller, __file__ doesn't point to the EXE location
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def _get_config_path():
    """Get config file path, with fallback to %APPDATA% if exe dir is not writable."""
    root = get_root_dir()
    primary = os.path.join(root, "engine_config.txt")
    
    # If file exists, use it
    if os.path.exists(primary):
        return primary
    
    # Try to write to primary location
    try:
        with open(primary, 'a'):
            pass
        os.remove(primary)
        return primary
    except (PermissionError, OSError):
        pass
    
    # Fallback to %APPDATA%/RAMURI/
    appdata = os.getenv("APPDATA", os.path.expanduser("~"))
    fallback_dir = os.path.join(appdata, "RAMURI")
    os.makedirs(fallback_dir, exist_ok=True)
    return os.path.join(fallback_dir, "engine_config.txt")

CONFIG_FILE = _get_config_path()

def create_default_config(config_path):
    """Creates a default config file with user-friendly comments."""
    with open(config_path, "w") as f:
        f.write("# ================================\n")
        f.write("# RAMURI Engine Configuration\n")
        f.write("# ================================\n")
        f.write("# You can edit these values to change engine behavior.\n")
        f.write("# Be sure to restart the app after editing this file.\n\n")

        f.write("# Memory used in MB (64-1024+ recommended depending on your system)\n")
        f.write("setoption name Hash value 1024\n\n")

        f.write("# CPU threads to use (1-8 usually; match your CPU core count)\n")
        f.write("setoption name Threads value 4\n")
    
    logger.info(f"Created default config file at {config_path}")

def load_engine_config(stockfish_proc, config_path=CONFIG_FILE):
    """Loads Stockfish engine settings from a config file. Creates default with comments if missing."""
    if not os.path.exists(config_path):
        create_default_config(config_path)

    with open(config_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                logger.info(f"Applying engine option: {line}")
                stockfish_proc.stdin.write(f"{line}\n")
            except Exception as e:
                logger.warning(f"Failed to apply config line '{line}': {e}")

    stockfish_proc.stdin.write("isready\n")
    stockfish_proc.stdin.flush()
    while True:
        if stockfish_proc.stdout.readline().strip() == "readyok":
            break

def ensure_config_exists():
    """Ensures the config file exists, creating it if necessary."""
    if not os.path.exists(CONFIG_FILE):
        logger.warning("Config file missing during gameplay, regenerating...")
        create_default_config(CONFIG_FILE)
        return True
    return False

def _initialize_stockfish():
    """Initialize a persistent Stockfish process."""
    global _stockfish_process
    
    if _is_shutting_down:
        logger.warning("Refusing to initialize Stockfish during shutdown")
        return None
    
    if _stockfish_process is not None:
        return _stockfish_process
    
    try:
        stockfish_path = resource_path("stockfish.exe" if os.name == "nt" else "stockfish")
        
        if os.name != "nt" and not os.path.exists(stockfish_path):
            sys_stock = shutil.which("stockfish")
            if sys_stock:
                logger.debug(f"Falling back to system Stockfish at {sys_stock}")
                stockfish_path = sys_stock
                
        if not os.path.exists(stockfish_path) and shutil.which(stockfish_path) is None:
            raise FileNotFoundError(f"Stockfish not found at {stockfish_path}")
        
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        logger.debug(f"Using Stockfish path: {stockfish_path}")
        
        _stockfish_process = subprocess.Popen(
            [stockfish_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=flags
        )

        load_engine_config(_stockfish_process)
        
        logger.info("Stockfish process initialized")
        return _stockfish_process
        
    except Exception as e:
        logger.error(f"Failed to initialize Stockfish: {e}")
        _stockfish_process = None
        raise

def _cleanup_stockfish():
    """Clean up the persistent Stockfish process."""
    global _stockfish_process
    
    if _stockfish_process is None:
        return
    
    proc = _stockfish_process
    _stockfish_process = None  # Clear global immediately to prevent concurrent access
    
    # Step 1: Check if process is already dead
    if proc.poll() is not None:
        logger.debug("Stockfish process already exited (code %s)", proc.poll())
        _close_pipes(proc)
        logger.info("Stockfish process cleaned up")
        return
    
    # Step 2: Try graceful shutdown via UCI 'quit' command
    try:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.write("quit\n")
            proc.stdin.flush()
    except (BrokenPipeError, OSError, ValueError):
        pass  # Pipe already closed/broken — that's fine
    
    # Step 3: Wait for graceful exit
    try:
        proc.wait(timeout=2)
        logger.debug("Stockfish exited gracefully")
        _close_pipes(proc)
        logger.info("Stockfish process cleaned up")
        return
    except subprocess.TimeoutExpired:
        logger.debug("Stockfish did not exit within 2s, forcing terminate")
    except OSError:
        # Process already gone — [Errno 22] or similar
        _close_pipes(proc)
        logger.info("Stockfish process cleaned up")
        return
    
    # Step 4: Force terminate
    try:
        if proc.poll() is None:  # Still alive
            proc.terminate()
            proc.wait(timeout=2)
            logger.debug("Stockfish terminated via terminate()")
    except (OSError, subprocess.TimeoutExpired):
        # Step 5: Last resort — kill
        try:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=1)
                logger.debug("Stockfish killed via kill()")
        except (OSError, subprocess.TimeoutExpired):
            logger.warning("Could not kill Stockfish process — it may be orphaned")
    
    _close_pipes(proc)
    logger.info("Stockfish process cleaned up")


def _close_pipes(proc: subprocess.Popen) -> None:  # type: ignore[type-arg]
    """Safely close all pipes on a Popen instance."""
    for pipe_name in ('stdin', 'stdout', 'stderr'):
        pipe = getattr(proc, pipe_name, None)
        if pipe and not pipe.closed:
            try:
                pipe.close()
            except (OSError, ValueError):
                pass

def _initialize_stockfish_at_startup():
    """Initialize Stockfish at application startup."""
    try:
        logger.info("Initializing Stockfish at application startup...")
        stockfish_process = _initialize_stockfish()
        if stockfish_process:
            logger.info("Stockfish successfully initialized with config settings")
            return True
        else:
            logger.error("Failed to initialize Stockfish at startup")
            return False
    except Exception as e:
        logger.error(f"Error initializing Stockfish at startup: {e}")
        return False

def _setup_stockfish_engine():
    config_recreated = ensure_config_exists()
    stockfish = _initialize_stockfish()
    
    if config_recreated and stockfish:
        logger.info("Reloading config into existing Stockfish process")
        load_engine_config(stockfish)
    
    return stockfish

def _get_move_from_engine(stockfish, depth_var, fen, root=None):
    # Check if process is still alive before writing
    if stockfish.poll() is not None:
        logger.warning("Stockfish process already dead before sending position")
        return None, False
    
    try:
        stockfish.stdin.write(f"position fen {fen}\n")
        stockfish.stdin.write(f"go depth {depth_var}\n")
        stockfish.stdin.flush()
    except (BrokenPipeError, OSError) as e:
        logger.warning(f"Failed to write to Stockfish: {e}")
        return None, False
    
    best_move = None
    mate_flag = False
    last_depth = 0
    engine_error = None
    
    while True:
        line = stockfish.stdout.readline()
        if not line:
            break
        
        if "CRITICAL ERROR" in line:
            engine_error = line.strip()
            logger.warning(f"Stockfish CRITICAL ERROR: {engine_error}")
            try:
                remaining = stockfish.stdout.read()
                if remaining:
                    logger.debug(f"Drained remaining output after error")
            except Exception:
                pass
            try:
                stockfish.wait(timeout=2)
            except Exception:
                pass
            break
        
        # Throttled UI updates — only update every 3 depths to reduce overhead
        if "info depth" in line and root and hasattr(root, 'update_status'):
            try:
                depth_part = line.split("info depth")[1].split()[0]
                current_depth = int(depth_part)
                if current_depth > last_depth:
                    last_depth = current_depth
                    if current_depth % 3 == 0 or current_depth >= depth_var - 1:
                        root.update_status(f"Processing... Depth {current_depth}/{depth_var}")
            except (IndexError, ValueError):
                pass
        
        mate_flag = _check_for_mate(line, mate_flag)
        best_move = _extract_best_move(line)
        
        if best_move:
            logger.info(f"Best move received: {best_move}")
            break
    
    if engine_error:
        logger.warning(f"Stockfish rejected position: {engine_error}")
        # Engine process is dead after CRITICAL ERROR — restart it now
        _cleanup_stockfish()
        new_engine = _initialize_stockfish()
        if new_engine:
            logger.info("Stockfish restarted after CRITICAL ERROR")
        else:
            logger.error("Failed to restart Stockfish after CRITICAL ERROR")
    
    return best_move, mate_flag


def _flip_side_to_move(fen: str) -> str:
    """Flip the side-to-move in a FEN string (w -> b, b -> w)."""
    parts = fen.split()
    if len(parts) >= 2:
        parts[1] = 'b' if parts[1] == 'w' else 'w'
    return ' '.join(parts)

def _check_for_mate(line, current_mate_flag):
    if "score mate" not in line:
        return current_mate_flag
    
    try:
        parts = line.split("score mate")
        mate_val = int(parts[1].split()[0])
        if abs(mate_val) == 1:
            logger.info("Mate in 1 detected")
            return True
    except (IndexError, ValueError):
        logger.warning("Could not parse mate score")
    
    return current_mate_flag

def _extract_best_move(line):
    if line.startswith("bestmove"):
        return line.strip().split()[1]
    return None

def _get_updated_fen(stockfish, original_fen, best_move):
    if not best_move:
        return None
    
    # Check process is alive before writing
    if stockfish.poll() is not None:
        logger.warning("Stockfish dead before _get_updated_fen, skipping")
        return None
    
    try:
        stockfish.stdin.write(f"position fen {original_fen} moves {best_move}\n")
        stockfish.stdin.write("d\n")
        stockfish.stdin.flush()
    except (BrokenPipeError, OSError) as e:
        logger.warning(f"Failed to write to Stockfish for updated FEN: {e}")
        return None
    
    updated_fen = None
    max_lines = 200
    lines_read = 0
    
    try:
        while lines_read < max_lines:
            line = stockfish.stdout.readline()
            lines_read += 1
            if not line:
                break
            
            if "CRITICAL ERROR" in line:
                logger.warning(f"Stockfish CRITICAL ERROR during FEN update")
                break
            
            if "Fen:" in line:
                updated_fen = line.split("Fen:")[1].strip()
            
            if "Checkers:" in line:
                break
    except (OSError, ValueError) as e:
        logger.warning(f"Error reading Stockfish output for updated FEN: {e}")
    
    if updated_fen:
        logger.info(f"Updated FEN: {updated_fen}")
    
    return updated_fen

def _handle_stockfish_failure(error_msg, root, auto_mode_var):
    logger.error(error_msg)
    _show_error_dialog(root, error_msg)
    _disable_auto_mode(auto_mode_var, root)
    return None, None, False

def _handle_error(error, root, auto_mode_var):
    error_msg = f"Stockfish error: {str(error)}"
    _show_error_dialog(root, error_msg)
    _disable_auto_mode(auto_mode_var, root)
    return None, None, False

def _show_error_dialog(root, message):
    if root:
        QTimer.singleShot(0, lambda: QMessageBox.critical(root, "Error", message))

def _disable_auto_mode(auto_mode_var, root):
    if auto_mode_var and root:
        if callable(auto_mode_var):
            root.auto_mode_var = False
            if hasattr(root, 'auto_mode_check'):
                root.auto_mode_check.setChecked(False)

class EngineService:
    @staticmethod
    def initialize():
        logger.info("Initializing engine service")
        return _initialize_stockfish_at_startup()

    @staticmethod
    def cleanup():
        global _is_shutting_down
        logger.info("Cleaning up engine service")
        _is_shutting_down = True
        _cleanup_stockfish()

    @staticmethod
    def get_best_move(depth: int, fen: str, root=None, auto_mode_var=None):
        logger.debug(f"Querying best move for FEN: {fen} at depth {depth}")
        with _stockfish_lock:
            try:
                logger.info("Getting best move from Stockfish")
                
                # Validate FEN BEFORE sending to Stockfish to prevent crashes
                is_valid, fen_error = _validate_fen(fen)
                if not is_valid:
                    logger.warning(f"Invalid FEN detected (skipping Stockfish): {fen_error}")
                    logger.warning(f"FEN was: {fen}")
                    if root and hasattr(root, 'update_status'):
                        root.update_status(f"Board detection issue: {fen_error}. Try again.")
                    return None
                
                if root and hasattr(root, 'update_status'):
                    root.update_status("Processing... Stockfish is thinking...")
                
                stockfish = _setup_stockfish_engine()
                if stockfish is None:
                    return _handle_stockfish_failure("Failed to initialize Stockfish", root, auto_mode_var)
                
                # Ensure Stockfish is alive and ready
                stockfish = EngineService._ensure_engine_ready(stockfish, root, auto_mode_var)
                if stockfish is None:
                    return None
                
                best_move, mate_flag = _get_move_from_engine(stockfish, depth, fen, root)
                
                # If Stockfish rejected the position, try flipped side-to-move
                if best_move is None:
                    flipped_fen = _flip_side_to_move(fen)
                    logger.info(f"First attempt failed. Restarting and retrying with flipped FEN: {flipped_fen}")
                    
                    _cleanup_stockfish()
                    stockfish = _initialize_stockfish()
                    if stockfish is None:
                        return _handle_stockfish_failure("Failed to restart Stockfish", root, auto_mode_var)
                    
                    # Send isready before retrying
                    if not EngineService._send_isready(stockfish):
                        _cleanup_stockfish()
                        return _handle_stockfish_failure("Stockfish not ready after restart", root, auto_mode_var)
                    
                    best_move, mate_flag = _get_move_from_engine(stockfish, depth, flipped_fen, root)
                    
                    if best_move is not None:
                        logger.info(f"Flipped FEN succeeded, best move: {best_move}")
                        fen = flipped_fen
                    else:
                        logger.warning("Both original and flipped FEN failed")
                        _cleanup_stockfish()
                        _initialize_stockfish()
                        return _handle_stockfish_failure(
                            "Board detection error — could not analyze this position. Try again.",
                            root, auto_mode_var
                        )
                
                if root and hasattr(root, 'update_status'):
                    root.update_status(f"Best move found: {best_move}")
                
                # Get updated FEN (non-critical — if it fails, still return the move)
                updated_fen = None
                try:
                    if stockfish and stockfish.poll() is None:
                        updated_fen = _get_updated_fen(stockfish, fen, best_move)
                    else:
                        logger.warning("Stockfish died after finding move, restarting for next call")
                        _cleanup_stockfish()
                        _initialize_stockfish()
                except Exception as e:
                    logger.warning(f"Non-critical error getting updated FEN: {e}")
                
                return best_move, updated_fen, mate_flag

            except Exception as e:
                logger.error(f"Stockfish error: {str(e)}")
                _cleanup_stockfish()
                return _handle_error(e, root, auto_mode_var)

    @staticmethod
    def _ensure_engine_ready(stockfish, root, auto_mode_var):
        """Ensure Stockfish process is alive. Only sends isready after a restart."""
        if stockfish.poll() is None:
            # Process alive — skip isready for speed on hot path
            return stockfish
        
        # Process dead — restart and verify with isready
        logger.warning("Stockfish process has died, restarting...")
        _cleanup_stockfish()
        stockfish = _initialize_stockfish()
        if stockfish is None:
            _handle_stockfish_failure("Failed to restart Stockfish", root, auto_mode_var)
            return None
        
        # Verify new process is responsive
        if not EngineService._send_isready(stockfish):
            logger.warning("Restarted Stockfish not responding, trying once more...")
            _cleanup_stockfish()
            stockfish = _initialize_stockfish()
            if stockfish is None:
                _handle_stockfish_failure("Failed to restart Stockfish", root, auto_mode_var)
                return None
        
        return stockfish

    @staticmethod
    def _send_isready(stockfish, timeout_lines=50):
        """Send 'isready' and wait for 'readyok'. Returns True if ready."""
        try:
            stockfish.stdin.write("isready\n")
            stockfish.stdin.flush()
            
            for _ in range(timeout_lines):
                line = stockfish.stdout.readline()
                if not line:
                    return False
                if "readyok" in line:
                    return True
            
            logger.warning("isready timeout — no 'readyok' received")
            return False
        except (BrokenPipeError, OSError) as e:
            logger.warning(f"isready failed: {e}")
            return False

