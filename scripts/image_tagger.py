# -*- coding: utf-8 -*-
"""
Author: Nick Tan (DSAID)
Supported Python Version: >= 3.7.5
Tested on Windows 10

Note: This script is attended to be run as a command line program.

"""
import sys
import io
import os
import re
from PIL import Image
import pandas as pd

from gooey import Gooey, GooeyParser
from google.cloud import vision



# if arguments are added, Gooey GUI is not active
if len(sys.argv) >= 2:
    if not "--ignore-gooey" in sys.argv:
        sys.argv.append("--ignore-gooey")


#region GUI Config (Decorator)
@Gooey(program_name="Image Tagger",
       program_description="Use A.I. to generate the keywords that describe your image. \n"
                           "It offers option to insert the keywords as EXIF tags of the images.",
       #tabbed_groups=True,
       required_cols=1,
       optional_cols=1,
       default_size=(610, 860),
       #advanced=False,
       image_dir='../_resources',
       progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
       progress_expr="current / total * 100"
)
#endregion
def _set_arguments_config():
    """
    Private function.
    Not meant to be used called directly.

    Returns
    -------
    args : dict
        Internally it returns "parser.parse_args()"

    """
    parser = GooeyParser(description="Image Tagger")
    arg_group_secure = parser.add_argument_group("Security")
    arg_group_secure.add_argument("credential",
                                  metavar='Credential File',
                                  help="Credential file (.json) downloaded from Google Cloud Platform.",
                                  widget="FileChooser",
                                  gooey_options=dict(
                                      wildcard="json file (*.json)|*.json"
                                  ))

    arg_group_inputs = parser.add_argument_group("Inputs")
    arg_group_inputs.add_argument("input_folder", widget="DirChooser",
                                  metavar='Image Folder', help="Folder containing the images to be tagged.",
                                  gooey_options=dict(
                                      default_path=os.path.join(os.getcwd(), os.path.pardir, "inputs")
                                  ))

    arg_group_inputs.add_argument("-r", "--recursive",
                                  action="store_true",
                                  metavar='Include Subfolders', help="Include Images in Subfolders")

    arg_group_outputs = parser.add_argument_group("Outputs")
    arg_group_outputs.add_argument("output_filepath", widget="FileSaver",
                        metavar='Save Results As', help="Path for the results in .csv file",
                        gooey_options=dict(
                            wildcard="Comma separated file (*.csv)|*.csv",
                            default_dir="../outputs",
                            default_file="Results_tagged_images.csv"
                        ))
                        #gooey_options=dict(wildcard="Video files (*.mp4, *.mkv)|*.mp4;*.mkv")

    arg_group_outputs.add_argument("-e", "--export-score",
                                   metavar='Export Relevance Score',
                                   help="Whether to export the relevance score of each keyword.",
                                   choices=['yes', 'no'], default='yes',
                                   )
    arg_group_outputs.add_argument("-m", "--maxkeywords",
                                   metavar='Maximum Keywords', help="Maximum number of keywords to be extracted per image."
                                                                  " Set 0 for unlimited.",
                                   widget="Slider", default=0, type=int,
                                   gooey_options=dict(
                                       min=0,
                                       max=255,
                                   ))
    arg_group_outputs_adv = parser.add_argument_group("Outputs: Advanced")
    arg_group_outputs_adv.add_argument("-t", "--tag",
                                  action="store_true",
                                  metavar='Insert Keywords as Tags', help="Insert Keywords as Images' EXIF Tags")
    arg_group_outputs_adv.add_argument("-rm", "--remove-existing-tags",
                                  action="store_true",
                                  metavar='Remove existing tags',
                                  help="[Warning: Irreversible] Remove existing tags before adding the generated EXIF Tags")


    args = parser.parse_args()
    return args


def run_image_annotation(input_folder:str, recursive:bool, output_filepath:str, maxkeywords:int, export_score:str) -> None:
    """
    This function calls Google-Cloud-Vision API to generate the keywordss for each of the images.
    It exports the images' filepath and keywordss in a csv file.

    Parameters
    ----------
    input_folder : str
        Path of the root folder where the images are stored on a local disk.
    recursive : bool
        If set to True, images in subfolders within the input_folder will also be processed.
    output_filepath : str
        Filepath of the csv file.
    maxkeywords : int
        Number of maximum to export into the csv file. Keywordss are sorted by relevancy.
    export_score : str
        "yes" or "no". Set to "no", will exclude the "relevancy score" in the csv file to be expoerted.

    Returns
    -------
    None
    """
    # Pre-scan the directories
    pat = re.compile('/\.')
    n_files = 0
    for root, dirs, files in os.walk(input_folder, topdown=False):
        if len(pat.findall(root)) == 0:
            n_files += len(files)
        if not recursive:
            break


    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    df = []

    counter = 0
    for root, dirs, files in os.walk(input_folder, topdown=True):
        # Ignore folder starts with .
        if len(pat.findall(root)) == 0:
            for filename in files:
                if str(filename).lower().endswith(('.jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff')):
                    img_filepath = os.path.join(root, filename)

                    with io.open(img_filepath, 'rb') as image_file:
                        content = image_file.read()
                        image = vision.Image(content=content)

                    response = client.label_detection(image=image)
                    results = [(os.path.abspath(os.path.join(root, filename)), x.description, x.score) for x in response.label_annotations]
                    df.append(pd.DataFrame(results, columns=['filepath', 'keyword', 'relevance']))

                    counter += 1
                    print("--------------------------")
                    print("Start to generate tags for the images.")
                    print("progress: {}/{}".format(counter, n_files))
            if not recursive:
                break

    df = pd.concat(df, axis=0, ignore_index=True, sort=False)
    df = df.sort_values(['filepath', 'relevance'], axis=0, ascending=False)

    if maxkeywords > 0:
        df = df.groupby('filepath').head(maxkeywords).reset_index()
    if export_score == "no":
        df = df.drop('relevance', axis=1)

    df.to_csv(output_filepath, index=False, encoding="utf-8")
    print("--------------------------")
    print("Exported CSV file to {}".format(output_filepath))


def insert_exif_tags(output_filepath:str, remove_existing_tags:bool) -> None:
    """
    This function inserts the generated tags into each of the image file.
    It relies on the csv exported as the input.
    Parameters
    ----------
    output_filepath : str
        The csv file exported from the function run_image_annotation().

    remove_existing_tags : bool
        If set to True. Existing EXIF tags in the image will be overwritten.

    Returns
    -------
    None
    """
    df = pd.read_csv(output_filepath)
    df = df.groupby('filepath').apply(lambda x: ', '.join(x.keyword)).reset_index()
    df.columns = ['filepath', 'tags_string']

    print("--------------------------")
    print("Start to insert exif tags.")
    counter = 0
    total_len = len(df)
    for index, row in df.iterrows():
        image = Image.open(row.filepath)

        XPKeywords = 0x9C9E
        #XPComment = 0x9C9C
        exifdata = image.getexif()

        if remove_existing_tags:
            exifdata[XPKeywords] = row.tags_string.encode("utf16")
        else:
            tags_string_concat = exifdata[XPKeywords].decode('utf16') + ', ' + row.tags_string
            exifdata[XPKeywords] = tags_string_concat.encode("utf16")

        image.save(row.filepath, exif=exifdata)


        # progress
        counter += 1
        print("progress: {}/{}".format(counter, total_len))
        print("--------------------------")
        print("Start to insert EXIF tags.")


def main():
    args = _set_arguments_config()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.credential


    run_image_annotation(args.input_folder,
                         args.recursive,
                         args.output_filepath,
                         args.maxkeywords,
                         args.export_score)
    if args.tag:
        insert_exif_tags(args.output_filepath, args.remove_existing_tags)

    print("--------------------------")
    print("All processes are successfully executed")


if __name__ == "__main__":
    main()