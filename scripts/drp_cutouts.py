#!/usr/bin/env python
# ruff: noqa

import click
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
    "--limit", default=None, help="Limit on how many data ids to process"
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
        try:
            dv_diaSourceTable = butler.get(ref)
        except:
            print(f"Could not load diaSource table for {ref.dataId}")
            continue
        else:
            dv_diaSourceTable["instrument"] = "LSSTComCam"
            cutoutTaskDrp.run(dv_diaSourceTable, butler)


if __name__ == "__main__":
    make_and_upload_drp_cutouts()
