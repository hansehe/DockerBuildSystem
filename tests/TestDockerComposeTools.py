import unittest
import random
import os
import logging
from tests import TestTools
from DockerBuildSystem import DockerComposeTools, YamlTools, DockerImageTools, TerminalTools

log = logging.getLogger(__name__)

TEST_IMAGE = 'test.image'
TEST_CONTAINER_NAME = 'test-container-' + str(random.randint(0, 100000))

class TestDockerComposeTools(unittest.TestCase):

    def test_a_ComposeBuild(self):
        log.info('COMPOSE BUILD')
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        DockerComposeTools.DockerComposeBuild([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')])
        log.info('DONE COMPOSE BUILD')

    def test_b_ComposeUp(self):
        log.info('COMPOSE RUN')
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        DockerComposeTools.DockerComposeUp([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')])
        log.info('DONE COMPOSE RUN')

    def test_c_ComposeRemove(self):
        log.info('COMPOSE REMOVE')
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        DockerComposeTools.DockerComposeRemove([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')])
        log.info('DONE COMPOSE REMOVE')

    def test_d_TagImages(self):
        log.info('COMPOSE TAG')
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        DockerComposeTools.TagImages(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml'), '1.0.0')
        log.info('DONE COMPOSE TAG')

    def test_e_SaveImages(self):
        log.info('COMPOSE SAVE')
        folder = os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'output')
        log.info(folder)
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        DockerComposeTools.SaveImages(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml'), folder)
        self.assertTrue(os.path.isfile(os.path.join(folder, 'my.service-1.0.0.tar')))
        log.info('DONE COMPOSE SAVE')

    def test_f_ComposeTest(self):
        log.info('COMPOSE TEST')
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        DockerComposeTools.ExecuteComposeTests([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')], ['my-service'])
        log.info('DONE COMPOSE TEST')

    def test_g_ComposeTestWithContainerNamesNotSet(self):
        log.info('COMPOSE TEST UNKNOWN NAME')
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        yamlData = YamlTools.GetYamlData([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.test.yml')])
        DockerComposeTools.AddContainerNames(yamlData)
        YamlTools.DumpYamlDataToFile(yamlData, os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.test.temp.yml'))
        DockerComposeTools.ExecuteComposeTests([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.test.temp.yml')])
        log.info('DONE COMPOSE TEST UNKNOWN NAME')

    def test_h_AddDigestsToImageTags(self):
        log.info('COMPOSE ADD DIGESTS')
        DockerImageTools.PullImage('nginx')
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        yamlData = YamlTools.GetYamlData([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')], replaceEnvironmentVariablesMatches=False)
        DockerComposeTools.AddDigestsToImageTags(yamlData)
        for service in yamlData['services']:
            if 'my.service' in yamlData['services'][service]['image']:
                self.assertEqual('my_repo/my.service:1.0.0', yamlData['services'][service]['image'])
            else:
                self.assertTrue('nginx@sha256:' in yamlData['services'][service]['image'])
            self.assertTrue(yamlData['services'][service]['environment']['SOME_VARIABLE'] == '${SOME_ENV_VARIABLE}')
        log.info('DONE COMPOSE ADD DIGESTS')

    def test_i_MultiBuildImages(self):
        log.info('COMPOSE MULTI BUILD')
        TerminalTools.LoadEnvironmentVariables(os.path.join(TestTools.TEST_SAMPLE_FOLDER, '.env'))
        DockerComposeTools.MergeComposeFiles([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')], os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.test.publish.yml'))
        DockerComposeTools.MultiBuildDockerImages(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.test.publish.yml'), ['linux/amd64', 'linux/arm64'], ['tag2', 'tag3'])
        log.info('DONE COMPOSE MULTI BUILD')


if __name__ == '__main__':
    unittest.main()