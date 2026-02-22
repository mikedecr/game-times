from ..game_name import GameName

__all__ = ["game_name_overrides", "avg_time_overrides", "play_time_overrides"]

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

# game_number_overrides will need to be interpolated from surrounding games
# this will have to be a separate routine against the dataframe w/ datetimes

avg_time_overrides: dict[str, str] = {
    "IMG_1207": "1:55",
}

play_time_overrides: dict[str, str] = {
    "IMG_1207": "1:12",
    "IMG_1832": "1:16",
}
