import json
import logging
import requests

from cogs.Player.core.utils import get_web_audio_duration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("player.monster_siren")


class Monster_siren:
    async def get_song_data(page_url: str):
        try:
            logger.info(f"正在從頁面 URL 獲取歌曲資訊...")
            cid = page_url.split("/")[-1]

            song_response = requests.get(url=f"https://monster-siren.hypergryph.com/api/song/{cid}")
            song_response.raise_for_status()
            raw_song_data = song_response.json()["data"]

            album_cid = raw_song_data.get("albumCid")
            if not album_cid:
                raise ValueError("API 回應中未找到專輯 ID (albumCid)")

            album_response = requests.get(url=f"https://monster-siren.hypergryph.com/api/album/{album_cid}/detail")
            album_response.raise_for_status()
            raw_album_data = album_response.json()["data"]
            logger.info("成功獲取 API 元數據！")

            audio_url = raw_song_data.get("sourceUrl")
            calculated_duration = None
            if audio_url:
                calculated_duration = await get_web_audio_duration(audio_url)
            else:
                logger.warning("API 回應中未提供音檔 URL (sourceUrl)。")

            data = {
                "title": raw_song_data.get("name", "N/A"),
                "author": ", ".join(raw_song_data.get("artists", ["N/A"])),
                "duration": calculated_duration,
                "song_url": audio_url,
                "thumbnail": raw_album_data.get("coverUrl", None),
            }
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API 請求失敗: {e}")
        except (KeyError, json.JSONDecodeError):
            logger.error("解析 API 回應失敗，可能是無效的 URL 或 API 結構已變更。")
        except Exception as e:
            logger.error(f"發生非預期錯誤: {e}", exc_info=True)
        return None
