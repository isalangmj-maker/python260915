from pathlib import Path
import shutil


DOWNLOAD_DIR = Path(r"C:\Users\student\Downloads")

FILE_GROUPS = {
    "images": {".jpg", ".jpeg"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip",".exe"},
}


def get_available_path(destination: Path) -> Path:
    """같은 이름의 파일이 있으면 덮어쓰지 않고 새 경로를 반환합니다."""
    if not destination.exists():
        return destination

    number = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{number}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        number += 1


def organize_downloads() -> None:
    if not DOWNLOAD_DIR.exists():
        print(f"다운로드 폴더를 찾을 수 없습니다: {DOWNLOAD_DIR}")
        return

    destination_dirs = {
        group: DOWNLOAD_DIR / group for group in FILE_GROUPS
    }
    for destination_dir in destination_dirs.values():
        destination_dir.mkdir(parents=True, exist_ok=True)

    moved_count = 0
    for file_path in DOWNLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()
        target_group = next(
            (
                group
                for group, extensions in FILE_GROUPS.items()
                if extension in extensions
            ),
            None,
        )
        if target_group is None:
            continue

        destination = get_available_path(
            destination_dirs[target_group] / file_path.name
        )
        shutil.move(str(file_path), str(destination))
        print(f"이동 완료: {file_path.name} -> {target_group}")
        moved_count += 1

    print(f"정리 완료: {moved_count}개 파일을 이동했습니다.")


if __name__ == "__main__":
    organize_downloads()