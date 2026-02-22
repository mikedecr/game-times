import polars as pl


def main() -> None:
    df = pl.read_csv("build/table/game_results.csv").sort("source_file")

    output = []

    for col in ["game", "round", "play_time", "avg_time"]:
        missing = df.filter(pl.col(col).is_null())["source_file"].to_list()
        output.append(f"{col}: {len(missing)} missing")
        output.append("")
        for f in missing:
            output.append(f"  {f}")
        output.append("")

    content = "\n".join(output)
    print(content)

    with open("build/table/missing_values.txt", "w") as f:
        f.write(content)


if __name__ == "__main__":
    main()
