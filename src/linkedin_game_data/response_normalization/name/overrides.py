from ...game_name import GameName

Tango = GameName.Tango
Queens = GameName.Queens

game_name_overrides: dict[str, GameName] = dict(
    # name missing for no reason, but using the color to infer
    IMG_2181=Tango,
    IMG_2182=Queens,
    IMG_2183=Tango,
    IMG_2184=Queens,
    # maybe in this case the time screen never loaded,
    # but we see the time of a solved game?
    IMG_1585=Tango,
)
