#!/usr/bin/env python
# ruff: noqa

import click
import pandas as pd
import lsst.daf.butler as dafButler
from lsst.analysis.ap import (
    PlotImageSubtractionCutoutsConfig,
    PlotImageSubtractionCutoutsTask,
)


@click.command()
@click.argument("repo")
@click.option("--collections", help="Butler collections.")
@click.option("--where", default=None, help="Data query to apply.")
@click.option("--output", "-o", default="./", help="Output location.")
@click.option(
    "--limit",
    default=None,
    help="Limit on how many data ids to process",
    type=int,
)
def make_drp_cutouts(
    repo,
    collections,
    where=None,
    output="./",
    limit: int | None = None,
):
    """Make image subtraction cutouts from a DRP run and output metadata for s3 upload."""
    butler = dafButler.Butler(repo, collections=collections)

    cutoutConfigDrp = PlotImageSubtractionCutoutsConfig()
    cutoutTaskDrp = PlotImageSubtractionCutoutsTask(
        config=cutoutConfigDrp, output_path=output
    )

    data_refs = butler.query_datasets(
        "goodSeeingDiff_diaSrcTable", where=where, limit=limit
    )

    for ref in data_refs:
        print(ref.dataId)
        try:
            dv_diaSourceTable = butler.get(ref)

        except Exception as e:
            print(f"Could not load diaSource table for {ref.dataId}")
            print(e)
            continue
        else:
            dv_diaSourceTable["instrument"] = "LSSTComCam"
            upload_df = pd.DataFrame(dv_diaSourceTable["diaSourceId"])
            upload_df.loc[:, "local_path"] = pd.Series(
                [
                    cutoutTaskDrp.cutout_path(did, f"{did}.png")
                    for did in dv_diaSourceTable["diaSourceId"].tolist()
                ],
                index=dv_diaSourceTable.index,
            )
            upload_df.loc[:, "relative_path"] = (
                upload_df["local_path"]
                .str.split("images/")
                .apply(lambda x: x[1])
            )
            upload_df.loc[:, "dataId"] = str(ref.dataId)
            cutoutTaskDrp.run(dv_diaSourceTable, butler)
            upload_df.to_csv(
                f"{output}/upload_{ref.dataId['visit']}_{ref.dataId['detector']}.csv"
            )


if __name__ == "__main__":
    make_drp_cutouts()
