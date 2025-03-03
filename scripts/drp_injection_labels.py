#!/usr/bin/env python
# ruff: noqa

import click
import pandas as pd
import lsst.daf.butler as dafButler
from pathlib import Path


@click.command()
@click.argument("repo")
@click.option("--collections", help="Butler collections.")
@click.option("--where", default="", help="Data query to apply.")
@click.option("--output", "-o", default="./", help="Output location.")
@click.option("--njobs", "-j", default=1, help="Number of jobs to use.")
@click.option(
    "--limit",
    default=None,
    help="Limit on how many data ids to process",
    type=int,
)
def make_drp_labels(
    repo,
    collections,
    where="",
    output="./",
    limit: int | None = None,
    njobs: int = 1,
):
    """Make image subtraction cutouts from a DRP run and output metadata for s3 upload."""
    butler = dafButler.Butler(repo, collections=collections)
    print(collections)

    data_refs = butler.query_datasets(
        "injected_goodSeeingDiff_diaSrcTable", where=where, limit=limit
    )

    label_path = Path(f"{output}/labels/")
    label_path.mkdir(parents=True, exist_ok=True)

    for ref in data_refs:
        label_file = f"{output}/labels/diasrc_injection_labels_{ref.dataId['visit']}_{ref.dataId['detector']}.csv.gz"
        label_file_Path = Path(label_file)
        #        if label_file_Path.is_file():
        #            print(f"{ref.dataId} already processed, continuing")
        #            continue

        print(ref)
        try:
            dv_diaSourceTable = butler.get(ref)

            cols_to_export = [
                "diaSourceId",
                "visit",
                "detector",
                "diaObjectId",
                "ssObjectId",
                "midpointMjdTai",
                "ra",
                "dec",
                "x",
                "y",
                "apFlux",
                "apFluxErr",
                "snr",
                "psfFlux",
                "psfFluxErr",
                "isDipole",
                "trailLength",
                "band",
                "extendedness",
                "pixelFlags_bad",
                "pixelFlags_cr",
                "pixelFlags_crCenter",
                "pixelFlags_edge",
                "pixelFlags_interpolated",
                "pixelFlags_interpolatedCenter",
                "pixelFlags_offimage",
                "pixelFlags_saturated",
                "pixelFlags_saturatedCenter",
                "pixelFlags_suspect",
                "pixelFlags_suspectCenter",
                "pixelFlags_streak",
                "pixelFlags_streakCenter",
                "pixelFlags_injected",
                "pixelFlags_injectedCenter",
                "pixelFlags_injected_template",
                "pixelFlags_injected_templateCenter",
            ]

            out = dv_diaSourceTable[cols_to_export]

            pd.set_option("display.max_columns", None)

            matched_truth = butler.get(
                "injected_goodSeeingDiff_matchDiaSourceTable",
                dataId=ref.dataId,
            )

            out.loc[:, "injection_matched"] = out["diaSourceId"].apply(
                lambda x: x in matched_truth["diaSourceId"].tolist()
            )

            print(sum(out["injection_matched"]))

            out.to_csv(label_file)
        except Exception as e:
            print(f"Failure processing {ref.dataId}")
            print(e)
            continue


if __name__ == "__main__":
    make_drp_labels()
