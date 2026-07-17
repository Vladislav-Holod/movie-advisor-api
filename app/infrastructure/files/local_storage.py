import os

import aiofiles

from app.domain.repositories.file_storage import AbstractFileStorage

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class FileTooLargeError(Exception):
    pass


class LocalFileStorage(AbstractFileStorage):
    def __init__(self, base_dir: str = "profile_images"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _path(self, filename: str) -> str:
        return os.path.join(self.base_dir, filename)

    async def save_from_stream(self, filename: str, read_chunk) -> int:
        """read_chunk — async callable, возвращающая очередной кусок байт или b''."""
        file_location = self._path(filename)
        chunk_size = 1024 * 1024
        current_size = 0
        try:
            async with aiofiles.open(file_location, "wb") as f:
                while True:
                    content = await read_chunk(chunk_size)
                    if not content:
                        break
                    current_size += len(content)
                    if current_size > MAX_FILE_SIZE:
                        raise FileTooLargeError()
                    await f.write(content)
        except Exception:
            if os.path.exists(file_location):
                os.remove(file_location)
            raise
        return current_size

    async def save(self, filename: str, content: bytes) -> None:
        async with aiofiles.open(self._path(filename), "wb") as f:
            await f.write(content)

    def delete(self, filename: str) -> None:
        path = self._path(filename)
        if os.path.exists(path):
            os.remove(path)

    def exists(self, filename: str) -> bool:
        return os.path.exists(self._path(filename))