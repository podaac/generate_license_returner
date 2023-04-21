# Standard imports
import time

# Third-party imports
import boto3
import botocore

class License:
    """A class that returns IDL licenses back into use.
    
    License removes uniquely identified license reservations for the current
    Generat workflow and adds those licenses back into the appriopriate dataset
    and floating parameters.
    
    Attributes
    ----------
    unique_id: int
        Identifies IDL licenses used by workflow in Parameter Store.
    prefix: str 
        Prefix for environment that Generate is executing in
    dataset: str
        Name of dataset that has been processed
    logger: logging.StreamHandler
        Logger object to use for logging statements
    
    Methods
    -------
    """
    
    def __init__(self, unique_id, prefix, dataset, processing_type, logger):
        """
        Attributes
        ----------
        unique_id: int
            Identifies IDL licenses used by workflow in Parameter Store.
        prefix: str 
            Prefix for environment that Generate is executing in
        dataset: str
            Name of dataset that has been processed
        processing_type: str
            Either "quicklook" or "refined"
        logger: logging.StreamHandler
            Logger object to use for logging statements
        """
        
        self.unique_id = unique_id
        self.prefix = prefix
        self.dataset = dataset
        self.ptype = "ql" if processing_type == "quicklook" else "r"
        self.logger = logger
        
    def return_licenses(self):
        """Returns IDL licenses that were in use by the current workflow execution.
        """
        
        ssm = boto3.client("ssm", region_name="us-west-2")
        
        # Retrieve reserved floating licenses
        floating_lic = self.check_existence(ssm, f"{self.prefix}-idl-{self.dataset}-{self.unique_id}-floating")

        # Retreive quicklook for refined processing type
        if self.ptype == "r":
            quicklook_lic = self.check_existence(ssm, f"{self.prefix}-idl-{self.dataset}-{self.unique_id}-ql")
            # If quicklook exists then don't delete floating license
            if quicklook_lic != None:
                floating_lic = None
        
        try:
            # Get number of dataset licenses that were used in the workflow
            dataset_lic = ssm.get_parameter(Name=f"{self.prefix}-idl-{self.dataset}-{self.unique_id}-{self.ptype}")["Parameter"]["Value"]
              
            # Wait until no other process is updating license info
            retrieving_lic =  ssm.get_parameter(Name=f"{self.prefix}-idl-retrieving-license")["Parameter"]["Value"]
            while retrieving_lic == "True":
                self.logger.info("Watiing for license retrieval...")
                time.sleep(3)
                retrieving_lic =  ssm.get_parameter(Name=f"{self.prefix}-idl-retrieving-license")["Parameter"]["Value"]
            
            # Place hold on licenses so they are not changed
            self.hold_license(ssm, "True")  
            
            # Return licenses to appropriate parameters
            self.write_licenses(ssm, dataset_lic, floating_lic)
            
            # Release hold as done updating
            self.hold_license(ssm, "False")
            
            # Delete unique parameters
            if floating_lic:
                deletion_list = [f"{self.prefix}-idl-{self.dataset}-{self.unique_id}-{self.ptype}", f"{self.prefix}-idl-{self.dataset}-{self.unique_id}-floating"]
            else:
                deletion_list = [f"{self.prefix}-idl-{self.dataset}-{self.unique_id}-{self.ptype}"]
            response = ssm.delete_parameters(Names=deletion_list)
            for parameter in deletion_list: self.logger.info(f"Deleted parameter: {parameter}.")
            
        except botocore.exceptions.ClientError as e:
            self.logger.error(e)
            self.logger.info("System exit.")
            exit(1)
            
    def check_existence(self, ssm, parameter_name):
        """Check existence of SSM parameter and return value if it exists.
        
        Returns None if does not exist.
        """
        
        try:
            parameter = ssm.get_parameter(Name=parameter_name)["Parameter"]["Value"]
        except botocore.exceptions.ClientError as e:
            if "(ParameterNotFound)" in str(e) :
                parameter = None
            else:
                self.logger.error(e)
                self.logger.info("System exit.")
                exit(1)
        return parameter        
    
    def hold_license(self, ssm, on_hold):
        """Put parameter license number ot use indicating retrieval in process."""
        
        try:
            response = ssm.put_parameter(
                Name=f"{self.prefix}-idl-retrieving-license",
                Type="String",
                Value=on_hold,
                Tier="Standard",
                Overwrite=True
            )
        except botocore.exceptions.ClientError as e:
            hold_action = "place" if on_hold == "True" else "remove"
            self.logger.error(f"Could not {hold_action} a hold on licenses...")
            raise e
        
    def write_licenses(self, ssm, dataset_lic, floating_lic):
        """Write license data to indicate number of licenses ready to be used."""
      
        try:
            current = ssm.get_parameter(Name=f"{self.prefix}-idl-{self.dataset}")["Parameter"]["Value"]
            total = int(dataset_lic) + int(current)
            response = ssm.put_parameter(
                Name=f"{self.prefix}-idl-{self.dataset}",
                Type="String",
                Value=str(total),
                Tier="Standard",
                Overwrite=True
            )
            self.logger.info(f"Wrote {dataset_lic} license(s) to {self.dataset}.")
            if floating_lic:
                current_floating = ssm.get_parameter(Name=f"{self.prefix}-idl-floating")["Parameter"]["Value"]
                floating_total = int(floating_lic) + int(current_floating)
                response = ssm.put_parameter(
                    Name=f"{self.prefix}-idl-floating",
                    Type="String",
                    Value=str(floating_total),
                    Tier="Standard",
                    Overwrite=True
                )
                self.logger.info(f"Wrote {floating_lic} license(s)to floating.")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"Could not return {self.dataset} and floating licenses...")
            raise e