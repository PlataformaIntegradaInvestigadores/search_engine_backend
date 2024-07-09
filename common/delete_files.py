from config.settings import BASE_DIR


class DeleteFile:
    def __init__(self, file_dir: str):
        self.base_dir = BASE_DIR
        self.file_dir = file_dir

    def build_absolute_path(self):
        return self.base_dir / self.file_dir

    def verify_file_existence(self) -> bool:
        return self.build_absolute_path().exists()

    def delete_file(self) -> bool:
        try:
            self.build_absolute_path().unlink()
            return True
        except FileNotFoundError:
            return False
