# see https://github.com/karlicoss/pymplate for up-to-date reference


from setuptools import setup, find_packages # type: ignore


def main():
    pkgs = find_packages('src') # todo find_namespace_packages??
    pkg = 'dashboard'
    assert pkg in pkgs
    setup(
        name=pkg,
        use_scm_version={
            'version_scheme': 'python-simplified-semver',
            'local_scheme': 'dirty-tag',
        },
        setup_requires=['setuptools_scm'],

        zip_safe=False,

        packages=pkgs,
        package_dir={'': 'src'},
        package_data={pkg: ['py.typed']},

        ## ^^^ this should be mostly automatic and not requiring any changes

        url='https://github.com/TODO',
        author='TODO',
        author_email='todo@todo.com',
        description='TODO',
        # TODO include readme so pip has it?
        # Rest of the stuff -- classifiers, license, etc, I don't think it matters for PIP
        # it's just unnecessary duplication

        install_requires=[
            'more-itertools',
            'pytz',
            'pandas',
            'bokeh',

            # todo could be optional?
            'hvplot',
            'statsmodels',
        ],
        extras_require={
            'testing': [
                'pytest',
                'hypothesis',
                'faker',

                'HPI @ git+https://github.com/karlicoss/HPI',
                # uncomment to use local HPI
                # 'HPI @ git+file:///DUMMY/path/to/local/hpi@branch',

                # HPI modules dependencies
                'rescuexport @ git+https://github.com/karlicoss/rescuexport',
                'emfitexport @ git+https://github.com/karlicoss/emfitexport',
                'endoexport  @ git+https://github.com/karlicoss/endoexport' ,
                'matplotlib', # todo emfitexport dependency for now, get rid later
            ],
            'linting': ['pytest', 'hypothesis', 'mypy'],
        },
    )


if __name__ == '__main__':
    main()

# TODO
# from setuptools_scm import get_version
# https://github.com/pypa/setuptools_scm#default-versioning-scheme
# get_version(version_scheme='python-simplified-semver', local_scheme='no-local-version')
