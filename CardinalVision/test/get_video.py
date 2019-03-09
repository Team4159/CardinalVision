import pkg_resources


def get_video(category, name):
    return pkg_resources.resource_filename('CardinalVision.test', '{category}/{name}.mov'.format(
        category=category,
        name=name))
