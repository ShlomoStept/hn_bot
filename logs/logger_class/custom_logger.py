import logging
from datetime import date
from os.path import join,dirname

class Logger:
    
    def __init__(self, logger_name, level=logging.INFO):
        
        self.format = logging.Formatter('%(asctime)s - %(message)s', "%H:%M:%S") 
        # logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%H:%M:%S") 
        self.name = logger_name
        self.level = level

        self.curr_output_file = None
        
        self.logger = self.setup_new_logger()
        self.file_save_date = date.today()
    
    
    '''
        Sets up a new logger object
    '''
    def setup_new_logger(self, name = None, specify_name = False) -> None:
        
        # Step 1 : get the proper filename
        if specify_name :
            self.curr_output_file = name
        else :
            self.curr_output_file = self.generate_file_name()
    
        # Step 2 : Setup a logger - handler
        log_handler = logging.FileHandler(self.curr_output_file)        
        log_handler.setFormatter(self.format)

        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.addHandler(log_handler)
        
        return logger
    


    '''
        Checks if the day has changed after a run, and renews the loggers with a new logging object tied to a new file 
    '''
    def day_change_check(self) -> bool :
        
        
        if self.file_save_date is None or date.today() != self.file_save_date :
            # delete the old logger, and generate a newone, with an updated file_name
            del self.logger
            self.logger = self.setup_new_logger()
            self.file_save_date = date.today()

            return True
        
        return False
    
         
    '''
        Generates a new file name with the format _<current_day>_<error/run_logger>.text
    '''
    def generate_file_name(self)  -> str :
        todays_date =  (date.today()).strftime("_%m_%d_%y_")
        
        proper_log_folder = "../files/_1_run_log_files/" if "run" in self.name  else  "../files/_2_error_log_files/" 
        relative_file_path = join(dirname(__file__), proper_log_folder + str(todays_date + self.name + ".txt" ))
        
        return relative_file_path
        
    
        
        