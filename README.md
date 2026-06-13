# LovherkBot
Koden til LovherkBot#8281 som viser regler og slikt for /r/Norge sin discordserver.

#### Oppsett
Avhengigheter styres med [uv](https://docs.astral.sh/uv/):

```
uv sync                       # lag virtuelt miljø fra uv.lock
uv run python lovherk.py      # kjør botten (krever config.json)
```

`config.json` (se `config.json.example`) må inneholde `token`, `default_prefix` og `playing`.

#### Utvikling
```
uv run --with ruff ruff check .     # linting
uv run --with pytest pytest         # tester
```

#### Hvordan bruke lovherket
Sjekk [HOWTO.md](https://github.com/Ev-1/lovherk/blob/master/HOWTO.md)
