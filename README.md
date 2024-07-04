# webdiffbot

Telegram Bot notification about changes on a website.

## Usage

First of all, you have to create a Bot, if you havnt, here:
[BotFather](https://t.me/BotFather)

To track a website and get notified about changes, you need to `cp .env.sample
.env` and adjust values.

The `CHATID` you can get here: [RawDataBot](https://t.me/RawDataBot)

Then build `docker compose build` and run your container for a check `docker
compose run webpage_monitor`. If you have a different hash, than in
`content_hash.txt`, you will get notified by Telegram.

## License

Apache. See [LICENSE](LICENSE).
Copyright (c) 2024 Dmitrij Vogt <divogt@vogt.dev>
