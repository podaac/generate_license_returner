"""return_license runs the License class with the appropriate data.

The License class returns the IDL licenses used by the current exectuion of the
Generate workflow.

Args:
[1] unique_id: Integer to identify IDL licenses used by workflow in Parameter Store.
[2] prefix: String Prefix for environment that Generate is executing in.
[3] dataset: Name of dataset that has been processed.
"""

# Standard imports 
import datetime
import logging
import os
import sys

# Local imports
from License import License

def run_license_returner():
    
    start = datetime.datetime.now()
    
    # Command line arguments
    unique_id = int(sys.argv[1])
    prefix = sys.argv[2]
    dataset = sys.argv[3]
    processing_type = sys.argv[4]
    
    # Log current execution state
    logger = get_logger()
    if dataset == "aqua":
        ds = "MODIS Aqua"
    elif dataset == "terra":
        ds = "MODIS Terra"
    else:
        ds = "VIIRS"
    logger.info(f"Job identifier: {os.environ.get('AWS_BATCH_JOB_ID')}")
    logger.info(f"Unique identifier: {unique_id}")
    logger.info(f"Dataset: {ds}")
    logger.info(f"Processing type: {processing_type.upper()}")
    execution_data = f"job_id {os.environ.get('AWS_BATCH_JOB_ID')} - unique_id: {unique_id} - dataset: {ds} - processing_type: {processing_type.upper()}"
    
    # Return licenses
    license = License(unique_id, prefix, dataset, processing_type, logger)
    license.return_licenses()
    
    # Print final log message
    print_final_log(logger, execution_data, license.idl_license_dict)
    
    end = datetime.datetime.now()
    logger.info(f"Total execution time: {end - start}")

def get_logger():
    """Return a formatted logger object."""
    
    # Remove AWS Lambda logger
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    # Create a Logger object and set log level
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a handler to console and set level
    console_handler = logging.StreamHandler()

    # Create a formatter and add it to the handler
    console_format = logging.Formatter("%(module)s - %(levelname)s : %(message)s")
    console_handler.setFormatter(console_format)

    # Add handlers to logger
    logger.addHandler(console_handler)

    # Return logger
    return logger

def print_final_log(logger, execution_data, idl_license_dict):
    """Print final log message."""
    
    # Organize file data into a string
    final_log_message = execution_data
    for key,value in idl_license_dict.items():
        final_log_message += f" - {key}: {value}"
    
    # Print final log message and remove temp log file
    logger.info(final_log_message)
    
if __name__ == "__main__":
    run_license_returner()