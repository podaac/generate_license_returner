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
import sys

# Local imports
from License import License

def run_uploader():
    
    start = datetime.datetime.now()
    
    # Command line arguments
    unique_id = int(sys.argv[1])
    prefix = sys.argv[2]
    dataset = sys.argv[3]
    processing_type = sys.argv[4]
    
    # Return licenses
    logger = get_logger()
    license = License(unique_id, prefix, dataset, processing_type, logger)
    license.return_licenses()
    
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
    console_format = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s : %(message)s")
    console_handler.setFormatter(console_format)

    # Add handlers to logger
    logger.addHandler(console_handler)

    # Return logger
    return logger
    
if __name__ == "__main__":
    run_uploader()