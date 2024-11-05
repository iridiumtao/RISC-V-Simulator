from pathlib import Path
from loguru import logger

project_root = Path()


def compare_files(testcases, filenames):
    for testcase in testcases:
        # Rename: Move SS_/RFResult.txt to testcase0 and rename SS_RFResult.txt
        old_path = project_root / 'Sample_Testcases_SS' / 'input' / testcase / 'SS_' / 'RFResult.txt'
        new_path = project_root / 'Sample_Testcases_SS' / 'input' / testcase / 'SS_RFResult.txt'

        if old_path.exists():
            new_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.rename(new_path)


        # Run tests
        input_path = project_root / 'Sample_Testcases_SS' / 'input' / testcase
        output_path = project_root / 'Sample_Testcases_SS' / 'output' / testcase

        for filename in filenames:
            input_file = input_path / filename
            output_file = output_path / filename

            # compare files
            if input_file.exists() and output_file.exists():
                input_content = input_file.read_text()
                output_content = output_file.read_text()

                if input_content == output_content:
                    logger.info(f"{testcase}/{filename}: file is identical")
                else:
                    logger.warning(f"{testcase}/{filename}: difference detected")
            else:
                logger.error(f"{testcase}/{filename}: file not found")

if __name__ == '__main__':

    'Sample_Testcases_SS/input/testcase0'
    testcase_dirs = ['testcase0', 'testcase1', 'testcase2']  # Add more test cases as needed
    filenames = ['SS_DMEMResult.txt', 'SS_RFResult.txt','StateResult_SS.txt']  # Add more filenames if necessary
    compare_files(testcase_dirs, filenames)