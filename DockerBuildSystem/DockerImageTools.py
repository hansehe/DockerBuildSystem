from DockerBuildSystem import TerminalTools
import re
import json
import logging

log = logging.getLogger(__name__)


def GetTargetImage(sourceImage, newTag):
    tagIndex = sourceImage.rfind(':')
    targetImage = sourceImage[:tagIndex + 1] + str(newTag)
    return targetImage


def BuildImage(imageName, dockerfile = 'Dockerfile', context = '.',
               args = None, tags = None, platforms = None, push = False):
    if args is None:
        args = []
    if tags is None:
        tags = []
    if platforms is None:
        platforms = []
    argsCommand = ''
    for arg in args:
        argsCommand += ' --build-arg ' + arg
    tagsCommand = ' -t ' + imageName
    for tag in tags:
        tagsCommand += ' -t ' + GetTargetImage(imageName, tag)
    platformsCommand = ''
    buildxCommand = '' 
    pushCommand = ''
    if push:
        pushCommand = ' --push'
    if len(platforms) > 0:
        createBuildDriverCommand = 'docker buildx create --use'
        TerminalTools.ExecuteTerminalCommands([createBuildDriverCommand], True)
        platformsCommand = '--platform ' + ','.join(platforms) + ' '
        buildxCommand = 'buildx '
    dockerCommand = "docker " + buildxCommand + "build " + platformsCommand + "-f " + dockerfile + argsCommand + tagsCommand + pushCommand + " " + context
    TerminalTools.ExecuteTerminalCommands([dockerCommand], True)


def RunImage(imageName, properties = ""):
    dockerCommand = "docker run " + properties + " " + imageName
    TerminalTools.ExecuteTerminalCommands([dockerCommand], True)


def PullImage(imageName):
    dockerCommand = "docker pull " + imageName
    TerminalTools.ExecuteTerminalCommands([dockerCommand], True)


def PushImage(imageName):
    dockerCommand = "docker push " + imageName
    TerminalTools.ExecuteTerminalCommands([dockerCommand], True)


def TagImage(sourceImage, targetImage):
    dockerCommand = "docker tag " + sourceImage + " " + targetImage
    TerminalTools.ExecuteTerminalCommands([dockerCommand], True)


def SaveImage(imageName, outputPath):
    dockerCommand = "docker save -o " + outputPath + " " + imageName
    TerminalTools.ExecuteTerminalCommands([dockerCommand], True)


def GetContainerExitCode(containerName):
    terminalCommand = "docker inspect " + containerName + " --format='{{.State.ExitCode}}'"
    output = TerminalTools.ExecuteTerminalCommandAndGetOutput(terminalCommand)
    exitCode = TerminalTools.GetNumbersFromString(output)[0]
    return int(exitCode)


def GetContainerRunningCode(containerName):
    terminalCommand = "docker inspect " + \
        containerName + " --format='{{.State.Running}}'"
    output = TerminalTools.ExecuteTerminalCommandAndGetOutput(terminalCommand)
    running = bool(re.search('true', str(output).lower()))
    return running


def CopyFromContainerToHost(containerName, containerSrc, hostDest):
    terminalCommand = "docker cp " + \
        containerName + ":" + containerSrc + " " + hostDest
    TerminalTools.ExecuteTerminalCommands([terminalCommand])


def GetImageRepoDigest(imageName):
    terminalCommand = "docker inspect --format=\"{{index .RepoDigests 0}}\" " + imageName
    repoDigest = str(TerminalTools.ExecuteTerminalCommandAndGetOutput(terminalCommand).decode("utf-8")).replace('\n', '')
    return repoDigest


def GetImageLabels(imageName):
    jsonInfo = GetImageInfo(imageName)
    labels = jsonInfo['Config']['Labels']
    return labels


def GetImageLabel(imageName, labelKey):
    labels = GetImageLabels(imageName)
    if labelKey in labels:
        return labels[labelKey]
    return '<no value>'


def CheckImageLabelExists(imageName, labelKey):
    labelValue = GetImageLabel(imageName, labelKey)
    return not(labelValue == '<no value>')


def GetImageId(imageName):
    terminalCommand = "docker inspect --format=\"{{.Id}}\" " + imageName
    imageId = str(TerminalTools.ExecuteTerminalCommandAndGetOutput(terminalCommand).decode("utf-8")).replace('\n', '')
    return imageId


def GetImageInfo(imageName):
    terminalCommand = "docker inspect " + imageName
    info = str(TerminalTools.ExecuteTerminalCommandAndGetOutput(terminalCommand).decode("utf-8"))
    jsonInfo = json.loads(info)[0]
    return jsonInfo


def GetContainerInfo(containerName):
    return GetImageInfo(containerName)


def GetLogsFromContainer(containerName):
    terminalCommand = 'docker logs {0}'.format(containerName)
    logs = str(TerminalTools.ExecuteTerminalCommandAndGetOutput(terminalCommand, includeErrorOutput=True).decode("utf-8"))
    return logs


def VerifyContainerExitCode(containerNames, assertExitCodes = False):
    sumExitCodes = 0
    sumErrorMsgs = ""
    for containerName in containerNames:
        exitCode = GetContainerExitCode(containerName)
        sumExitCodes += exitCode
        if exitCode > 0:
            errorMsg = "Container '" + containerName + "' FAILED!\r\n"
            sumErrorMsgs += errorMsg
            log.info(errorMsg)
        else:
            log.info(containerName + " container finished with success.\r\n")
    if sumExitCodes > 0 and assertExitCodes:
        raise Exception(sumErrorMsgs)
    return sumExitCodes, sumErrorMsgs


def DockerLogin(server, userName, password, dryRun=False):
    if(dryRun):
        log.info("Would have logged in to {0} with user {1}".format(server, userName))
    else:
        terminalCommand = 'docker login {0} -u {1} -p {2}'.format(server, userName, password)
        TerminalTools.ExecuteTerminalCommands(
            terminalCommands=[terminalCommand], 
            raiseExceptionWithErrorCode=True, 
            printCommand=False)


def DockerLogout(server, dryRun=False):
    if(dryRun):
        log.info("Would have logged out of {0}".format(server))
    else:
        terminalCommand = 'docker logout {0}'.format(server)
        TerminalTools.ExecuteTerminalCommands(
            terminalCommands=[terminalCommand], 
            raiseExceptionWithErrorCode=True, 
            printCommand=False)