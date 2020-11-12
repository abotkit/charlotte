import yaml

from persistence.files.ifile_handler import IDataHandler


class YAMLDataHandler(IDataHandler):
    def read_yaml_file(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                yaml_file = yaml.full_load(file)
            return yaml_file
        except (TypeError, FileNotFoundError) as e:
            print(f"File errors with file: {path} - Exception: {str(e)}")

    def write_yaml_file(self, path: str, content: dict):
        with open(path, 'w', encoding='utf-8') as file:
            file_content = yaml.dump(content, file)