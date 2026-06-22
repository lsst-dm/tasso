#!/usr/bin/env python

import click
from glob import glob
import csv
import boto3
from botocore.config import Config

import os
import subprocess


@click.command()
@click.argument("indir")
@click.argument("run_id")
def upload_s3(indir: str, run_id: int):
    """Take outputs of drp_cutouts and upload to s3, store in tasso db"""

    session = boto3.Session(profile_name="tasso")
    endpoint_url = "https://s3dfrgw.slac.stanford.edu"
    s3 = session.client(
        "s3",
        endpoint_url=endpoint_url,
        # https://github.com/boto/boto3/issues/4400
        config=Config(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
    )

    # get environment for shelling out to tasso
    env = {}
    env.update(os.environ)

    for upload in glob(f"{indir}/upload*.csv"):
        with open(upload) as csvfile:
            reader = csv.DictReader(csvfile, dialect="unix")
            for row in reader:
                print(row["diaSourceId"])
                s3.upload_file(
                    row["local_path"],
                    "rubin-ap-cutouts",
                    f"{run_id}/{row['relative_path']}",
                )

                uri = f"s3://rubin-ap-cutouts/{run_id}/{row['relative_path']}"

                args = [
                    "tasso",
                    "add-subject",
                    run_id,
                    row["diaSourceId"],
                    uri,
                    f"--data-id={row['dataId']}",
                ]

                subprocess.run(args)


if __name__ == "__main__":
    upload_s3()
