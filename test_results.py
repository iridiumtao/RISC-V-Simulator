from pathlib import Path
from loguru import logger
import difflib
from typing import Literal
import os
import sys

project_root = Path()




def compare_files(testcases, filenames, stage_text: Literal["FS", "SS"]):
    for testcase in testcases:
        # Rename: Move SS_/RFResult.txt to testcase0 and rename SS_RFResult.txt
        old_path = project_root / f'Sample_Testcases_{stage_text}' / 'input' / testcase / f'{stage_text}_' / 'RFResult.txt'
        new_path = project_root / f'Sample_Testcases_{stage_text}' / 'input' / testcase / f'{stage_text}_RFResult.txt'

        if old_path.exists():
            new_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.rename(new_path)

        # Run tests
        # batch run result would be stored in input folder (as it is seen as io_dir)
        # and the expected result is stored in output folder
        input_path = project_root / f'Sample_Testcases_{stage_text}' / 'input' / testcase
        output_path = project_root / f'Sample_Testcases_{stage_text}' / 'output' / testcase

        for filename in filenames:
            input_file = input_path / filename
            output_file = output_path / filename

            # Compare files
            if input_file.exists() and output_file.exists():
                input_content = input_file.read_text().splitlines()
                output_content = output_file.read_text().splitlines()

                if input_content == output_content:
                    logger.info(f"{testcase}/{filename}: file is identical")
                else:
                    logger.warning(f"{testcase}/{filename}: difference detected")
                    print_diff_with_context(input_content, output_content, testcase, filename)
            else:
                logger.error(f"{testcase}/{filename}: file not found")
def print_diff_with_context(input_content, output_content, testcase, filename):
    """Print the differences with context (10 lines before and 5 lines after)."""
    diff = difflib.unified_diff(
        output_content, input_content,
        fromfile=f"{testcase}/expected/{filename}",
        tofile=f"{testcase}/actual/{filename}",
        lineterm='',
        n=15  # Shows context of 15 lines (10 before + 5 after)
    )

    logger.info(f"\nDiff for {testcase}/{filename}:\n" + "\n".join(diff))

def batch_run():
    # os.system("python3 main.py --iodir './Sample_Testcases_SS/input/testcase0'")
    # os.system("python3 main.py --iodir './Sample_Testcases_SS/input/testcase1'")
    # os.system("python3 main.py --iodir './Sample_Testcases_SS/input/testcase2'")
    os.system("python3 main.py --iodir './Sample_Testcases_FS/input/testcase0'")
    os.system("python3 main.py --iodir './Sample_Testcases_FS/input/testcase1'")
    os.system("python3 main.py --iodir './Sample_Testcases_FS/input/testcase2'")
    # os.system("python3 main.py --iodir './Sample_Testcases_FS/input/testcase3'")

if __name__ == '__main__':
    # batch_run()


    stage_text = "FS"
    testcase_dirs = ['testcase0',
                      'testcase1',
                     'testcase2'
                     ]  # Add more test cases as needed
    filenames = [
        f'{stage_text}_DMEMResult.txt',
        f'{stage_text}_RFResult.txt',
        # f'StateResult_{stage_text}.txt'
                 ]  # Add more filenames if necessary
    compare_files(testcase_dirs, filenames, stage_text)