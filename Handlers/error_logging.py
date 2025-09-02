import logging
from datetime import datetime
from Handlers.cleanLogs import *
# 1. Create three separate loggers
software_logger = logging.getLogger("software_error")
process_error_logger = logging.getLogger("process_error")
process_info_logger = logging.getLogger("process_info")

# 2. Set levels (controls what gets through)
software_logger.setLevel(logging.ERROR)   # software log only ERROR+
process_error_logger.setLevel(logging.ERROR)  # process error log only ERROR+
process_info_logger.setLevel(logging.INFO)    # process info log INFO+

# 2.5 Delete any old logs for now
check_for_logfiles()

# 3. Create file handlers
fh_software = logging.FileHandler(f"softwareErrorLog_{datetime.now().strftime('%m%d%y_%H%M')}.log")
fh_process_error = logging.FileHandler(f"process_errors_{datetime.now().strftime('%m%d%y_%H%M')}.log")
fh_process_info = logging.FileHandler(f"process_info_{datetime.now().strftime('%m%d%y_%H%M')}.log")

# 4. Create a formatter (consistent format)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# 5. Attach formatter to each handler
fh_software.setFormatter(formatter)
fh_process_error.setFormatter(formatter)
fh_process_info.setFormatter(formatter)

# 6. Add handlers to each logger
software_logger.addHandler(fh_software)
process_error_logger.addHandler(fh_process_error)
process_info_logger.addHandler(fh_process_info)