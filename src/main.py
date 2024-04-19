import pathlib

from config import load_config_from_file


def main() -> None:
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config_from_file(config_file_path)
    print(config)


if __name__ == '__main__':
    main()
