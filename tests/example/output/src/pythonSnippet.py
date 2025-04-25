import logging

log = logging.getLogger(__name__)

def GetInfoMsg():
    infoMsg = "This python snippet is just an example.\r\n"
    return infoMsg

if __name__ == "__main__":
    log.info(GetInfoMsg())