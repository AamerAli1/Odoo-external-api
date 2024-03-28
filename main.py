import json
import os
import time
from parsing import process_file
import logging


def main():
    logging.basicConfig(filename='odooInterface.log', level=logging.INFO)
    logging.info('Program Started')

    with open('config.json') as json_file:
        data = json.load(json_file)
    new_jvs_location = data['new_jvs_location']
    processed_jvs_location = data['processed_jvs_location']
    error_jvs_location = data['error_jvs_location']

    while True:
        # get a list of files in the NewJVs directory
        to_process_files = os.listdir(new_jvs_location)

        # iterate over the files
        for file_name in to_process_files:
            # construct the full file path
            file_path = os.path.join(new_jvs_location, file_name)
            # process the file:
            try:
                print("Processing File: " + file_path)
                process_file(file_path)
                # move the file to the done directory
                os.rename(file_path, os.path.join(processed_jvs_location, file_name))
                print("File Processed successfully: " + file_path)
            except Exception as e:
                # get the current timestamp
                current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                # log the error with the timestamp
                logging.error("Error occurred while processing file: %s. Error message: %s", file_path, str(e))

                # print the error message
                print("error Occured in  file\nmoving file to error folder")
                print(e)

                # move the file to the error directory
                os.rename(file_path, os.path.join(error_jvs_location, file_name))

        # wait for a certain amount of time before checking the directory again
        time.sleep(5)


if __name__ == '__main__':
    main()

