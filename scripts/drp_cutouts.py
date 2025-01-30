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
@click.option("--run-id", help="tasso run to upload to.")
@click.option("--where", default=None, help="Data query to apply.")
@click.option("--output", "-o", default="./", help="Output location.")
@click.option(
    "--limit",
    default=None,
    help="Limit on how many data ids to process",
    type=int,
)
def make_and_upload_drp_cutouts(
    repo,
    collections,
    run_id,
    where=None,
    output="./",
    limit: int | None = None,
):
    """Make image subtraction cutouts from a DRP run and upload them to s3."""
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
            upload_df.loc[:, "relative_path"] = upload_df[
                "local_path"
            ].str.split("images/")
            upload_df.loc[:, "s3_path"] = pd.Series(
                [
                    f"s3://rubin-ap-cutouts/{run_id}/{rel}"
                    for rel in upload_df["relative_path"].values
                ],
                index=dv_diaSourceTable.index,
            )
            del upload_df["relative_path"]
            upload_df.loc[:, "dataId"] = str(ref.dataId)
            print(upload_df.head(2))
            # cutoutTaskDrp.run(dv_diaSourceTable, butler)

        # now loop over DIASources to upload to s3


if __name__ == "__main__":
    make_and_upload_drp_cutouts()
