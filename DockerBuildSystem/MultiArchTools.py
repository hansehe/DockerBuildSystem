from DockerBuildSystem import TerminalTools, YamlTools, DockerImageTools
import os
import json
import logging

log = logging.getLogger(__name__)


def MultiBuildPushByDigest(composeFile, platforms, digestsFile):
    """Build each service in the compose file with `docker buildx build`
    using `push-by-digest=true,push=true`. Captures the resulting digest
    from the buildx metadata file and writes a JSON map keyed by service
    name to `digestsFile`.

    The output JSON is a dictionary like:
        {
          "myService": {
            "image": "aimzas/foo:1.2.3",
            "repo": "aimzas/foo",
            "tag": "1.2.3",
            "digest": "sha256:...",
            "platforms": ["linux/amd64"]
          },
          ...
        }
    """
    yamlData = YamlTools.GetYamlData([composeFile])
    services = yamlData.get('services', {})
    digests = {}

    for service in services:
        svc = services[service]
        if 'build' not in svc:
            continue

        image = svc['image']
        repo, tag = DockerImageTools.SplitImageRepoAndTag(image)

        buildCfg = svc['build']
        context = buildCfg.get('context', '.')
        dockerfile = buildCfg.get('dockerfile', 'Dockerfile')
        args = buildCfg.get('args', []) or []
        if isinstance(args, dict):
            args = ['{0}={1}'.format(k, v) for k, v in args.items()]

        argsCommand = ''
        for arg in args:
            argsCommand += ' --build-arg ' + arg

        metaFile = '.dbm-meta-{0}.json'.format(service)
        if os.path.isfile(metaFile):
            os.remove(metaFile)

        createBuildDriverCommand = 'docker buildx create --use'
        TerminalTools.ExecuteTerminalCommands([createBuildDriverCommand], True)

        platformsCsv = ','.join(platforms)
        fullPathDockerfile = os.path.join(context, dockerfile)
        outputArg = (
            '--output type=image,'
            '"name={0}",'
            'push-by-digest=true,'
            'name-canonical=true,'
            'push=true'
        ).format(repo)

        dockerCommand = (
            'docker buildx build '
            + '--platform ' + platformsCsv + ' '
            + '-f ' + fullPathDockerfile
            + argsCommand + ' '
            + outputArg + ' '
            + '--metadata-file ' + metaFile + ' '
            + context
        )
        TerminalTools.ExecuteTerminalCommands([dockerCommand], True)

        digest = ReadDigestFromMetadataFile(metaFile)
        digests[service] = {
            'image': image,
            'repo': repo,
            'tag': tag,
            'digest': digest,
            'platforms': list(platforms),
        }

        try:
            os.remove(metaFile)
        except OSError:
            pass

    WriteDigestsFile(digestsFile, digests)
    log.info('Wrote {0} digest entries to {1}'.format(len(digests), digestsFile))
    return digests


def ReadDigestFromMetadataFile(metaFile):
    if not os.path.isfile(metaFile):
        raise Exception(
            "Buildx metadata file '{0}' not found - cannot capture image digest.".format(metaFile))
    with open(metaFile, 'r') as f:
        meta = json.load(f)
    digest = meta.get('containerimage.digest')
    if not digest:
        raise Exception(
            "Buildx metadata file '{0}' did not contain 'containerimage.digest'. "
            "Got keys: {1}".format(metaFile, list(meta.keys())))
    return digest


def WriteDigestsFile(digestsFile, digests):
    parent = os.path.dirname(os.path.abspath(digestsFile))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(digestsFile, 'w') as f:
        json.dump(digests, f, indent=2)


def LoadDigestsFiles(digestFiles):
    """Load multiple digest JSON files produced by MultiBuildPushByDigest
    and group them by service. Returns a dict like:
        { service: [ { image, repo, tag, digest, platforms }, ... ], ... }
    Entries are kept in the order the files were provided.
    """
    grouped = {}
    for digestFile in digestFiles:
        if not os.path.isfile(digestFile):
            raise Exception("Digest file not found: {0}".format(digestFile))
        with open(digestFile, 'r') as f:
            data = json.load(f)
        for service in data:
            grouped.setdefault(service, []).append(data[service])
    return grouped


def CreateMultiArchManifest(repo, tags, digests):
    """Run `docker buildx imagetools create` to combine per-arch digests into
    a single multi-arch manifest list, tagging it with all `tags`.

    `digests` is a list of digest strings (sha256:...). `tags` is a list of
    tag strings (e.g. ['1.2.3', 'latest']).
    """
    if not tags:
        raise Exception("CreateMultiArchManifest requires at least one tag for repo '{0}'".format(repo))
    if not digests:
        raise Exception("CreateMultiArchManifest requires at least one digest for repo '{0}'".format(repo))

    tagsCommand = ''
    for tag in tags:
        tagsCommand += ' -t ' + repo + ':' + str(tag)

    sourcesCommand = ''
    for digest in digests:
        sourcesCommand += ' ' + repo + '@' + digest

    dockerCommand = 'docker buildx imagetools create' + tagsCommand + sourcesCommand
    TerminalTools.ExecuteTerminalCommands([dockerCommand], True)
