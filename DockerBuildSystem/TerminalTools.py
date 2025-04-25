import subprocess
import os
import re
import logging
from dotenv import load_dotenv

log = logging.getLogger(__name__)


def LoadEnvironmentVariables(environmentVariablesFile):
    load_dotenv(environmentVariablesFile)


def LoadDefaultEnvironmentVariablesFile(defaultEnvFile = '.env'):
    if os.path.isfile(defaultEnvFile):
        LoadEnvironmentVariables(defaultEnvFile)


def PrintAvailableCommands(availableCommands):
    for availableCommand in availableCommands:
        log.info(availableCommand)


def ExecuteTerminalCommands(terminalCommands, raiseExceptionWithErrorCode=False, printCommand=False, transientErrorPatterns=None):
    transientErrorPatterns = transientErrorPatterns if transientErrorPatterns is not None else []
    for terminalCommand in terminalCommands:
        if printCommand:
            log.info(f"Executing: {terminalCommand}")
        try:
            with subprocess.Popen(
                terminalCommand,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            ) as process:
                errorDetected = False
                outputLines = []
                for line in process.stdout:
                    line = line.rstrip()
                    log.info(line)
                    outputLines.append(line)
                    for pattern in transientErrorPatterns:
                        if pattern.lower() in line.lower():
                            errorDetected = True
                returnCode = process.wait()
                if returnCode != 0 or errorDetected:
                    errorMsg = f"Command failed: {terminalCommand}\nReturn code: {returnCode}"
                    if errorDetected:
                        errorMsg += "\nTransient error detected in output."
                    if raiseExceptionWithErrorCode:
                        raise Exception(errorMsg)
                    else:
                        log.info(errorMsg)
        except KeyboardInterrupt:
            if raiseExceptionWithErrorCode:
                raise Exception("Command interrupted by user (KeyboardInterrupt)")


def ExecuteTerminalCommandAndGetOutput(terminalCommand, includeErrorOutput=False, printCommand=False, transientErrorPatterns=None):
    transientErrorPatterns = transientErrorPatterns if transientErrorPatterns is not None else []
    if printCommand:
        log.info(f"Executing: {terminalCommand}")
    try:
        with subprocess.Popen(
            terminalCommand,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT if includeErrorOutput else subprocess.DEVNULL
        ) as process:
            outputBytes = b""
            errorDetected = False
            for line in process.stdout:
                try:
                    log.info(line.decode("utf-8", errors="replace"), end="")
                except Exception:
                    pass
                outputBytes += line
                for pattern in transientErrorPatterns:
                    if pattern.encode("utf-8") in line.lower():
                        errorDetected = True
            returnCode = process.wait()
            if returnCode != 0 or errorDetected:
                errorMsg = f"Command failed with return code {returnCode}"
                if errorDetected:
                    errorMsg += "\nTransient error detected in output."
                raise Exception(f"{errorMsg}\n\nOutput:\n{outputBytes.decode('utf-8', errors='replace')}")
            return outputBytes
    except KeyboardInterrupt:
        raise Exception("Command interrupted by user (KeyboardInterrupt)")


def GetNumbersFromString(string):
    strNumbers = re.findall(r'\d+', str(string))
    numbers = [int(i) for i in strNumbers]
    return numbers


def ExportVariableToEnvironment(variable, variableName):
    os.environ[variableName] = str(variable)
