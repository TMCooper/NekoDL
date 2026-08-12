from ..core.core import YuiCleanLogger
from .info import get_anime_metadata
from .episodes import get_seasons, get_episode_links
from .resolvers import resolve_video_url
import yt_dlp
import sys
import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

print_lock = threading.Lock()

class ThreadedCleanLogger:
    def __init__(self, slot_index=None, total_slots=4):
        self.path_printed = False
        self.slot_index = slot_index
        self.total_slots = total_slots

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        if self.slot_index is not None:
            with print_lock:
                sys.stdout.write(f"\nError in thread {self.slot_index}: {msg}\n")
        else:
            print(msg)

    def hook(self, d):
        try:
            terminal_width = shutil.get_terminal_size().columns
        except OSError:
            terminal_width = 80

        if d['status'] == 'downloading':
            progress_line = (
                f"[download] {d.get('_percent_str', 'N/A')} of {d.get('total_bytes_str', 'N/A')}"
                f" at {d.get('_speed_str', 'N/A')} ETA {d.get('_eta_str', 'N/A')}"
            )
            
            if self.slot_index is not None:
                filename = os.path.basename(d['filename'])
                if len(filename) > 15:
                    filename = filename[:12] + "..."
                progress_line = f"{filename}: {progress_line}"
                
                line_to_write = f"\r{progress_line:<{terminal_width - 1}}"
                
                with print_lock:
                    # ANSI codes for moving cursor up and down
                    sys.stdout.write(f"\033[{self.total_slots - self.slot_index}A")
                    sys.stdout.write(line_to_write)
                    sys.stdout.write(f"\033[{self.total_slots - self.slot_index}B")
                    sys.stdout.flush()
            else:
                if not self.path_printed:
                    print(f"Destination: {d['filename']}")
                    self.path_printed = True
            
                line_to_write = f"\r{progress_line:<{terminal_width - 1}}"
                sys.stdout.write(line_to_write) 
                sys.stdout.flush()

        if d['status'] == 'finished':
            if self.slot_index is None:
                self.path_printed = False


def _download_raw(url, path, quality="best", headers=None, slot_index=None, total_slots=1):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
            'Accept': '*/*'
        }

    logger = ThreadedCleanLogger(slot_index, total_slots) if slot_index is not None else YuiCleanLogger()

    ydl_opts = {
        'outtmpl': path,
        'format': quality,
        'ignoreerrors': True,
        'logger': logger,
        'progress_hooks': [logger.hook],
        'verbose': False,
        'http_headers': headers
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.download([url])
    except KeyboardInterrupt:
        return None


def _resolve_episode(episodes_dict, ep_index, allowed_sites=None):
    """
    Try to resolve a working direct URL for a single episode by iterating
    across all available players (eps1, eps2, eps3, ...).
    Returns a dict {"url": ..., "type": ..., "headers": ...} or None.
    """
    if allowed_sites is None:
        allowed_sites = [
            "sibnet.ru", "video.sibnet.ru",
            "embed4me.com", "lpayer.embed4me.com", "player.embed4me.com",
            "ansembed.net", "ansembed.com",
            "vidmoly.to", "vidmoly.net", "vidmoly.me",
            "smoothpre.com", "vidhide.com", "vidhidepro.com",
            "streamwish.com", "streamwish.to",
            "sendvid.com", "oneupload.to", "oneupload.net",
            "filemoon.sx", "filemoon.to", "vidoza.net"
        ]

    players = sorted(episodes_dict.keys(), key=lambda k: int(k.replace("eps", "")))

    for player in players:
        ep_list = episodes_dict[player]
        if ep_index >= len(ep_list):
            continue

        ep_url = ep_list[ep_index]

        # Check if URL belongs to an allowed site
        is_allowed = any(site in ep_url.lower() for site in allowed_sites)
        if not is_allowed:
            continue

        try:
            resolved = resolve_video_url(ep_url)
            if resolved and resolved.get("url"):
                return resolved
        except Exception:
            continue

    return None


def _prepare_download_tasks(anime_url, season=None, episode=None, path=None):
    metadata = get_anime_metadata(anime_url)
    anime_name = metadata.get("title") or "Unknown_Anime"
    
    anime_name = "".join([c for c in anime_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()

    seasons_data = get_seasons(anime_url)
    if not seasons_data:
        raise ValueError("No seasons found or blocked by Cloudflare.")

    target_season = None
    if season is None:
        target_season = seasons_data[0]
    else:
        for s in seasons_data:
            if s["season"].lower().replace(" ", "") == str(season).lower().replace(" ", ""):
                target_season = s
                break
        if not target_season:
            raise ValueError(f"Season '{season}' not found.")

    season_name = target_season["season"]
    season_name = "".join([c for c in season_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()

    # 3. Get episodes
    episodes_dict = get_episode_links(target_season["url"])
    if not episodes_dict:
        raise ValueError("No episodes found.")

    # Determine episode count from the first player
    first_player = sorted(episodes_dict.keys(), key=lambda k: int(k.replace("eps", "")))[0]
    num_episodes = len(episodes_dict[first_player])

    tasks = []
    if episode is not None:
        if isinstance(episode, int):
            ep_indices = [episode - 1]
        elif isinstance(episode, list):
            ep_indices = [e - 1 for e in episode]
        else:
            ep_indices = range(num_episodes)
    else:
        ep_indices = range(num_episodes)

    base_path = path or os.path.join(os.getcwd(), "anime", anime_name, season_name)

    for i in ep_indices:
        if 0 <= i < num_episodes:
            resolved = _resolve_episode(episodes_dict, i)
            if resolved:
                final_url = resolved["url"]
            
                ep_filename = f"ep{i+1}.mp4"
                final_path = os.path.join(base_path, ep_filename)
                
                tasks.append({
                    "url": final_url,
                    "path": final_path,
                    "ep_number": i + 1,
                    "headers": resolved.get("headers"),
                })

    return tasks


def download(anime_url, season=None, episode=None, path=None, quality="best", headers=None):
    """
    Downloads an anime episode (or all episodes) sequentially.
    
    :param anime_url: The Anime-Sama base URL.
    :param season: The season name (defaults to the first season).
    :param episode: The episode number (int) or list of ints. If None, downloads all.
    :param path: Base output path. Defaults to [CWD]/anime/[Anime_Name]/[Season]/
    """
    tasks = _prepare_download_tasks(anime_url, season, episode, path)
    for task in tasks:
        # Merge resolver-specific headers with user-provided headers
        dl_headers = {**(headers or {}), **(task.get("headers") or {})}
        os.makedirs(os.path.dirname(task["path"]), exist_ok=True)
        _download_raw(task["url"], task["path"], quality=quality, headers=dl_headers or None)


def download_many(anime_url, season=None, episode=None, path=None, quality="best", headers=None, max_workers=4):
    """
    Downloads an anime episode (or all episodes) concurrently.
    """
    tasks = _prepare_download_tasks(anime_url, season, episode, path)
    
    if not tasks:
        return

    # Print enough newlines to make space for the multi-line progress bars
    print("\n" * min(max_workers, len(tasks)))
    
    download_slots = Queue()
    for i in range(max_workers):
        download_slots.put(i)

    def _worker(dl_task):
        slot = download_slots.get()
        try:
            dl_headers = {**(headers or {}), **(dl_task.get("headers") or {})}
            os.makedirs(os.path.dirname(dl_task["path"]), exist_ok=True)
            _download_raw(
                url=dl_task["url"], 
                path=dl_task["path"], 
                quality=quality, 
                headers=dl_headers or None, 
                slot_index=slot, 
                total_slots=max_workers
            )
        finally:
            download_slots.put(slot)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for task in tasks:
            executor.submit(_worker, task)
