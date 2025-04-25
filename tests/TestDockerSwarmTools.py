import unittest
import random
import os
import logging
from tests import TestTools
from DockerBuildSystem import DockerSwarmTools
from DockerBuildSystem import DockerComposeTools, TerminalTools

log = logging.getLogger(__name__)

class TestDockerSwarmTools(unittest.TestCase):

    def test_a_StartSwarm(self):
        log.info('SWARM START')
        DockerSwarmTools.StartSwarm()
        log.info('DONE SWARM START')

    def test_b_CreateRemoveNetwork(self):
        log.info('CREATE NETWORK')
        network = 'my-network-' + str(random.randint(0, 10000))
        DockerSwarmTools.CreateSwarmNetwork(network)
        DockerSwarmTools.RemoveSwarmNetwork(network)

        DockerSwarmTools.CreateSwarmNetwork(network, encrypted=True, driver="overlay", attachable=False, options=['--ipv6'])
        DockerSwarmTools.RemoveSwarmNetwork(network)

        log.info('DONE CREATE NETWORK')

    def test_c_CreateRemoveConfig(self):
        log.info('CREATE CONFIG')
        config = 'changelog-config-' + str(random.randint(0, 10000))
        DockerSwarmTools.CreateSwarmConfig(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'CHANGELOG.md'), config)
        DockerSwarmTools.RemoveSwarmConfig(config)
        log.info('DONE CREATE CONFIG')

    def test_d_CreateRemoveSecret(self):
        log.info('CREATE SECRET')
        secret = 'changelog-secret-' + str(random.randint(0, 10000))
        DockerSwarmTools.CreateSwarmSecret(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'CHANGELOG.md'), secret)
        DockerSwarmTools.RemoveSwarmSecret(secret)
        log.info('DONE CREATE SECRET')

    def test_e_CreateRemoveVolume(self):
        log.info('CREATE VOLUME')
        volume = 'test-volume-' + str(random.randint(0, 10000))
        DockerSwarmTools.CreateSwarmVolume(volume)
        DockerSwarmTools.RemoveSwarmVolume(volume)

        DockerSwarmTools.CreateSwarmVolume(volume, driver='local')
        DockerSwarmTools.RemoveSwarmVolume(volume)

        log.info('DONE CREATE VOLUME')

    def test_f_CreateRemoveStack(self):
        log.info('CREATE STACK')
        stack = 'test-stack-' + str(random.randint(0, 10000))
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        DockerComposeTools.DockerComposeBuild([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')])
        DockerSwarmTools.DeployStack(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml'), stack)
        serviceName = stack + '_nginx-service'
        assert DockerSwarmTools.CheckIfSwarmServiceIsRunning(serviceName) == False
        DockerSwarmTools.WaitUntilSwarmServicesAreRunning(10, 1, serviceName)
        DockerSwarmTools.RemoveStack(stack)
        log.info('DONE CREATE STACK')


if __name__ == '__main__':
    unittest.main()