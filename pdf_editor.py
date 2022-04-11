import argparse
import os
import sys
import shutil

import PyPDF2

from tqdm import tqdm
from PyPDF2 import PdfFileReader, PdfFileMerger

from typing import List, Optional, Tuple

#######################################################################################################################
###### Constants
#######################################################################################################################

MERGE = "merge"
RENAME = "rename"

#######################################################################################################################
###### Functions
#######################################################################################################################


def get_pdf_metadata(pdf_file: str) -> dict:
    """ Gets the pdf metadata from a pdf file path

    pdf_file: path str to pdf
    """
    with open(pdf_file, 'rb') as file_in:
        pdf_reader = PdfFileReader(file_in)
        metadata = pdf_reader.getDocumentInfo()
        raw_metadata = dict(metadata.items())

    metadata = {key: value for key, value in raw_metadata.items() if isinstance(value, str)}
    return metadata


def write_new_pdf(input_pdf: str, metadata: dict, output_pdf: str) -> None:
    """ Writes a pdf with new metadata given a template pdf

    pdf_file: path str to pdf
    metadata: dict of pdf metadata values
    output_pdf: path str to write new pdf
    """
    with open(input_pdf, 'rb') as input_pdf_handle, open(output_pdf, 'wb') as output_pdf_handle:
        pdf_merger = PdfFileMerger()
        pdf_merger.append(input_pdf_handle)
        pdf_merger.addMetadata(metadata)
        pdf_merger.write(output_pdf_handle)


def change_file_metadata_to_file_name(pdf_file: str) -> None:
    """ Changes the pdf metadata to reflect the file name

    pdf_file: path str to pdf
    """

    temp_pdf_file = pdf_file + ".tmp"
    metadata = get_pdf_metadata(pdf_file)
    metadata["/Title"] = pdf_file.strip(".pdf")

    write_new_pdf(pdf_file, metadata, temp_pdf_file)

    shutil.move(temp_pdf_file, pdf_file)


def merge_pdfs(pdf_path_list: List[str], output_path: str) -> None:
    """ Merges the given pdfs

    pdf_path_list: list of pdf paths to be concatenated
    output_path: path to output pdf
    """
    merger = PyPDF2.PdfFileMerger()
    for pdf in pdf_path_list:
        merger.append(pdf)

    merger.write(output_path)
    merger.close()


#######################################################################################################################
###### Main
#######################################################################################################################


def argument_parser() -> Tuple[List[str], str, Optional[str]]:
    """"""
    parser = argparse.ArgumentParser(description='Changes pdf metadata file name to match the current file name')
    parser.add_argument('--pdfs', dest="pdf_paths", help='pdf paths', nargs="+", required=True)
    parser.add_argument('--merge', dest="merge", action="store_true", help='merge mode')
    parser.add_argument('--rename', dest="rename", action="store_true", help='rename mode')
    parser.add_argument('-o', "--out", type=str, dest="output_path", default=None, help='Output of merged pdf.')
    inputs = parser.parse_args()

    assert inputs.merge != inputs.rename, "Either --merge or --rename flags can be given, not both,"
    mode = MERGE if inputs.merge else RENAME

    assert len(inputs.pdf_paths) > 0, "No pdfs given."

    if mode == MERGE:
        assert inputs.output_path, "No output PDF given."
        assert inputs.output_path.endswith(".pdf"), "Output PDF must end with '.pdf'"
        assert len(inputs.pdf_paths) > 1, "More than one pdf must be provided for concatenation."

    for pdf_path in inputs.pdf_paths:
        assert os.path.exists(pdf_path), f"{pdf_path} does not exist."
        assert pdf_path.endswith(".pdf"), f"{pdf_path} is invalid. PDF editor requires that pdfs must end with '.pdf'"

    return inputs.pdf_paths, mode, inputs.output_path


def main():
    pdf_paths, mode, output_path = argument_parser()

    if mode == RENAME:
        pbar = tqdm(pdf_paths, unit=" pdf", desc=f"Editing PDF Metadata {pdf_paths[0]:<60}")
        for pdf_path in pbar:
            pbar.desc = f"Editing PDF Metadata: {pdf_path:>40}"
            change_file_metadata_to_file_name(pdf_path)
    else:
        merge_pdfs(pdf_paths, output_path)


if __name__ == '__main__':
    main()

#######################################################################################################################
###### End
#######################################################################################################################
