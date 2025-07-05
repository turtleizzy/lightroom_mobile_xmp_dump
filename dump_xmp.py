import argparse
import os
import shutil
import sqlite3
import tempfile
import traceback
import urllib.parse
from string import Template

import dateutil.parser
import tqdm


def dump_xmp_files(data_root, output_dir, copy_source_files=True):
    file_uri = urllib.parse.quote(os.path.join(data_root, "Managed Catalog.wfindex"))
    template = Template(
        "select path, size "
        " from cacheReferences "
        "where docId = '$doc_id' and isTrash = 0 and renditionName = '$rendition_name' "
        "order by userUpdated desc"
    )
    db = sqlite3.connect(f"file://{file_uri}?mode=ro", uri=True)
    all_docs = db.execute(
        "select docId, captureDate, fileName from coreInfo"
    ).fetchall()

    for doc_id, capture_date, original_file_name in tqdm.tqdm(all_docs):
        try:
            src_files = db.execute(
                template.safe_substitute(doc_id=doc_id, rendition_name="original")
            ).fetchall()
            xmp_files = db.execute(
                template.safe_substitute(doc_id=doc_id, rendition_name="xmp_develop")
            ).fetchall()
            date_str = dateutil.parser.parse(capture_date).strftime("%Y-%m-%d")
            os.makedirs(os.path.join(output_dir, date_str), exist_ok=True)
            if copy_source_files:
                for path, file_size in src_files:
                    cur_org_file = os.path.join(
                        output_dir, date_str, original_file_name
                    )
                    if not os.path.isfile(cur_org_file) or int(
                        os.stat(cur_org_file).st_size
                    ) != int(file_size):
                        shutil.copy2(os.path.join(data_root, path), cur_org_file)
            for path, file_size in xmp_files[:1]:
                xmp_filename, _ = os.path.splitext(original_file_name)
                cur_xmp_file = os.path.join(output_dir, date_str, xmp_filename + ".xmp")
                shutil.copy2(os.path.join(data_root, path), cur_xmp_file)
        except Exception:
            traceback.print_exc()
    db.close()


def mount_lightroom_document_path():
    tmp_path = tempfile.mkdtemp()
    retval = os.system(f"ifuse --documents com.adobe.lrmobile {tmp_path}")
    if retval != 0:
        retval = os.system(f"ifuse --documents com.adobe.lrmobilephone {tmp_path}")
        if retval != 0:
            raise Exception("Lightroom mobile app not found.")
    return tmp_path


def umount_document_path(mount_path):
    os.system(f"fusermount -u {mount_path}")
    os.rmdir(mount_path)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir")
    parser.add_argument("--no-copy-source-file", action="store_false")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    mount_path = mount_lightroom_document_path()
    try:
        for d in os.listdir(mount_path):
            if os.path.isdir(os.path.join(mount_path, d)):
                dump_xmp_files(
                    os.path.join(mount_path, d),
                    args.output_dir,
                    args.no_copy_source_file,
                )
    finally:
        umount_document_path(mount_path)
