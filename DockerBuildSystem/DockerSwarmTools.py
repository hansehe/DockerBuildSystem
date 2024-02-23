import subprocess
import json
import time

from DockerBuildSystem import TerminalTools


def DeployStack(composeFile, stackName, environmentVariablesFiles = [], withRegistryAuth = False):
    for environmentVariablesFile in environmentVariablesFiles:
        TerminalTools.LoadEnvironmentVariables(environmentVariablesFile)
    print("Deploying stack: " + stackName)
    dockerCommand = "docker stack deploy -c " + composeFile
    if withRegistryAuth:
        dockerCommand += " --with-registry-auth"
    dockerCommand += " " + stackName
    TerminalTools.ExecuteTerminalCommands([dockerCommand], True)


def RemoveStack(stackName):
    print("Removing stack: " + stackName)
    dockerCommand = "docker stack rm " + stackName
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def CreateSwarmNetwork(networkName, encrypted = False, driver = 'overlay', attachable = True, options = []):
    print("Creating network: " + networkName)
    dockerCommand = "docker network create "
    dockerCommand += "--driver {0} ".format(driver)
    if attachable:
        dockerCommand += "--attachable "
    if encrypted:
        dockerCommand += "--opt encrypted "
    for option in options:
        dockerCommand += "{0} ".format(option)
    dockerCommand += networkName
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def RemoveSwarmNetwork(networkName):
    print("Removing network: " + networkName)
    dockerCommand = "docker network rm " + networkName
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def CreateSwarmSecret(secretFile, secretName):
    print("Creating secret: " + secretName)
    dockerCommand = "docker secret create " + secretName + " " + secretFile
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def RemoveSwarmSecret(secretName):
    print("Removing secret: " + secretName)
    dockerCommand = "docker secret rm " + secretName
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def CreateSwarmConfig(configFile, configName):
    print("Creating config: " + configName)
    dockerCommand = "docker config create " + configName + " " + configFile
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def RemoveSwarmConfig(configName):
    print("Removing config: " + configName)
    dockerCommand = "docker config rm " + configName
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def CreateSwarmVolume(volumeName, driver = 'local', driverOptions = []):
    print("Creating volume: {0}, with driver: {1} and driver options: {2}".format(volumeName, driver, driverOptions))
    dockerCommand = "docker volume create --driver {0}".format(driver)
    for driverOption in driverOptions:
        dockerCommand += " --opt {0}".format(driverOption)
    dockerCommand += ' {0}'.format(volumeName)
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def RemoveSwarmVolume(volumeName):
    print("Removing volume: " + volumeName)
    dockerCommand = "docker volume rm " + volumeName
    TerminalTools.ExecuteTerminalCommands([dockerCommand])


def CheckIfSwarmServiceIsRunning(serviceNames = None):
    terminalCommand = "docker service ls --format=json"
    servicesRaw = str(TerminalTools.ExecuteTerminalCommandAndGetOutput(terminalCommand).decode("utf-8"))
    servicesRaw = servicesRaw.splitlines()
    for serviceRaw in servicesRaw:
        if serviceRaw.strip() == "":
            continue
        service = json.loads(serviceRaw)
        if serviceNames == None or service['Name'] in serviceNames:
            replicas = service['Replicas'].split('/')
            currentReplicas = int(replicas[0])
            totalReplicas = int(replicas[1])
            if currentReplicas < totalReplicas:
                print("Service: " + service['Name'] + " is not running. Current replicas: " + str(currentReplicas) + " of " + str(totalReplicas))
                return False
    return True


def SwarmIsInitiated():
    terminalCommand = "docker node inspect self --pretty"
    returnCode = subprocess.Popen(terminalCommand, shell=True).wait()
    return returnCode == 0


def WaitUntilSwarmServicesAreRunning(timeoutInSeconds = 60, intervalInSeconds = 1, serviceNames = None):
    timeOut = time.time() + timeoutInSeconds
    while time.time() < timeOut:
        print("Waiting for services to start. Seconds left: " + str(int(timeOut - time.time())))
        if CheckIfSwarmServiceIsRunning(serviceNames):
            print("Services started.")
            return
        time.sleep(intervalInSeconds)
    raise Exception("Services did not start in time.")


def StartSwarm():
    if SwarmIsInitiated():
        print("Swarm is already initiated.")
        return

    print("Starting swarm")
    dockerCommand = "docker swarm init"
    TerminalTools.ExecuteTerminalCommands([dockerCommand])
