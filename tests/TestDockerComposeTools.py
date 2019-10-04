import unittest
import random
import os
from tests import TestTools
from DockerBuildSystem import DockerComposeTools, YamlTools, DockerImageTools

TEST_IMAGE = 'test.image'
TEST_CONTAINER_NAME = 'test-container-' + str(random.randint(0, 100000))

class TestDockerComposeTools(unittest.TestCase):

    def test_a_ComposeBuild(self):
        print('COMPOSE BUILD')
        DockerComposeTools.DockerComposeBuild([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')])
        print('DONE COMPOSE BUILD')

    def test_b_ComposeUp(self):
        print('COMPOSE RUN')
        DockerComposeTools.DockerComposeUp([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')])
        print('DONE COMPOSE RUN')

    def test_c_ComposeRemove(self):
        print('COMPOSE REMOVE')
        DockerComposeTools.DockerComposeRemove([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')])
        print('DONE COMPOSE REMOVE')

    def test_d_TagImages(self):
        print('COMPOSE TAG')
        DockerComposeTools.TagImages(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml'), '1.0.0')
        print('DONE COMPOSE TAG')

    def test_e_SaveImages(self):
        print('COMPOSE SAVE')
        folder = os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'output')
        print(folder)
        DockerComposeTools.SaveImages(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml'), folder)
        self.assertTrue(os.path.isfile(os.path.join(folder, 'my.service-tag.tar')))
        print('DONE COMPOSE SAVE')

    def test_f_ComposeTest(self):
        print('COMPOSE TEST')
        DockerComposeTools.ExecuteComposeTests([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')], ['my-service'])
        print('DONE COMPOSE TEST')

    def test_f_AddDigestsToImageTags(self):
        print('COMPOSE ADD DIGESTS')
        DockerImageTools.PullImage('nginx')
        outputFolder = os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'output')
        if not(os.path.isdir(outputFolder)):
            os.makedirs(outputFolder)

        DockerComposeTools.AddDigestsToImageTags([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'docker-compose.yml')], os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'output/docker-compose.digests.yml'))
        yamlData = YamlTools.GetYamlData([os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'output/docker-compose.digests.yml')])
        for service in yamlData['services']:
            if 'my.service' in yamlData['services'][service]['image']:
                self.assertEqual('my_repo/my.service:tag', yamlData['services'][service]['image'])
            else:
                self.assertTrue('nginx@sha256:' in yamlData['services'][service]['image'])
        print('DONE COMPOSE ADD DIGESTS')


if __name__ == '__main__':
    unittest.main()