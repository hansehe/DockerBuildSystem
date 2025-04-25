import unittest
import random
import os
import logging
from tests import TestTools
from DockerBuildSystem import DockerImageTools

TEST_IMAGE = 'test.image'
TEST_CONTAINER_NAME = 'test-container-' + str(random.randint(0, 100000))

log = logging.getLogger(__name__)

class TestDockerImageTools(unittest.TestCase): 

    def test_a_BuildImage(self):
        log.info('BUILD IMAGE')
        DockerImageTools.BuildImage(TEST_IMAGE, dockerfile=os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'Dockerfile'), context=TestTools.TEST_SAMPLE_FOLDER)
        DockerImageTools.BuildImage(TEST_IMAGE, dockerfile=os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'Dockerfile'), context=TestTools.TEST_SAMPLE_FOLDER, args=['VERSION=1.2.3'], platforms=['linux/amd64', 'linux/arm64'])
        log.info('DONE BUILD IMAGE')

    def test_b_RunImage(self):
        log.info('RUN IMAGE')
        DockerImageTools.RunImage(TEST_IMAGE, '--name ' + TEST_CONTAINER_NAME)
        log.info('DONE RUN IMAGE')

    def test_c_GetContainerExitCode(self):
        log.info('CONTAINER EXIT CODE')
        exitCode = DockerImageTools.GetContainerExitCode(TEST_CONTAINER_NAME)
        self.assertEqual(exitCode, 0)
        log.info('DONE CONTAINER EXIT CODE')

    def test_d_GetContainerRunningCode(self):
        log.info('CONTAINER RUNNING CODE')
        running = DockerImageTools.GetContainerRunningCode(TEST_CONTAINER_NAME)
        self.assertEqual(running, False)
        log.info('DONE CONTAINER RUNNING CODE')

    def test_e_TagImage(self):
        log.info('TAG IMAGE')
        DockerImageTools.TagImage(TEST_IMAGE, TEST_IMAGE + ':1.0.0')
        log.info('DONE TAG IMAGE')

    def test_f_CopyFromContainerToHost(self):
        log.info('COPY FROM CONTAINER TO HOST')
        outputFolder = os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'output/')
        if not (os.path.isdir(outputFolder)):
            os.makedirs(outputFolder)

        DockerImageTools.CopyFromContainerToHost(TEST_CONTAINER_NAME, 'src/', outputFolder)
        log.info(os.listdir(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'output/src')))
        self.assertTrue(os.path.isfile(os.path.join(TestTools.TEST_SAMPLE_FOLDER, 'output/src/pythonSnippet.py')))
        log.info('DONE COPY FROM CONTAINER TO HOST')

    def test_g_GetImageRepoDigest(self):
        log.info('GET IMAGE REPO DIGEST')
        DockerImageTools.PullImage('nginx')
        repoDigest = DockerImageTools.GetImageRepoDigest('nginx')
        self.assertTrue('nginx@sha256:' in repoDigest)
        self.assertFalse('\n' in repoDigest)
        log.info('DONE GET IMAGE REPO DIGEST')

    def test_h_GetImageLabels(self):
        log.info('GET IMAGE LABELS')
        labels = DockerImageTools.GetImageLabels(TEST_IMAGE)
        self.assertGreater(len(labels), 0)
        self.assertTrue('owner', labels)
        self.assertTrue(labels['owner'] == 'example owner')
        log.info('DONE GET IMAGE LABELS')

    def test_h_GetImageLabel(self):
        log.info('GET IMAGE LABEL')
        labelValue = DockerImageTools.GetImageLabel(TEST_IMAGE, 'org.opencontainers.image.version')
        self.assertEqual('1.0.0', labelValue)

        labelValue = DockerImageTools.GetImageLabel(TEST_IMAGE, 'none_existent')
        self.assertEqual('<no value>', labelValue)
        log.info('DONE GET IMAGE LABEL')

    def test_i_CheckImageLabelExists(self):
        log.info('CHECK IMAGE LABEL EXISTS')
        exists = DockerImageTools.CheckImageLabelExists(TEST_IMAGE, 'owner')
        self.assertTrue(exists)
        exists = DockerImageTools.CheckImageLabelExists(TEST_IMAGE, 'org.opencontainers.image.version')
        self.assertTrue(exists)

        exists = DockerImageTools.CheckImageLabelExists(TEST_IMAGE, 'none_existent')
        self.assertFalse(exists)
        log.info('DONE CHECK IMAGE LABEL EXISTS')

    def test_j_GetImageId(self):
        log.info('GET IMAGE ID')
        imageId = DockerImageTools.GetImageId(TEST_IMAGE)
        self.assertTrue('sha256:' in imageId)
        log.info('DONE GET IMAGE ID')

    def test_k_GetImageInfo(self):
        log.info('GET IMAGE INFO')
        jsonInfo = DockerImageTools.GetImageInfo(TEST_IMAGE)
        self.assertTrue('sha256:' in jsonInfo['Id'])
        log.info('DONE GET IMAGE INFO')

    def test_l_GetContainerInfo(self):
        log.info('GET CONTAINER INFO')
        jsonInfo = DockerImageTools.GetContainerInfo(TEST_CONTAINER_NAME)
        self.assertTrue(len(jsonInfo['Id']) > 0)
        log.info('DONE GET CONTAINER INFO')

    def test_m_GetLogsFromContainer(self):
        log.info('GET CONTAINER LOGS')
        logs = DockerImageTools.GetLogsFromContainer(TEST_CONTAINER_NAME)
        self.assertTrue(len(logs) > 0)
        log.info('DONE GET CONTAINER LOGS')

if __name__ == '__main__':
    unittest.main()