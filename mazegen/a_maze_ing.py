from src import config_parser


if __name__ == "__main__":
    config = config_parser.parse_config('config.txt')
    print(config)