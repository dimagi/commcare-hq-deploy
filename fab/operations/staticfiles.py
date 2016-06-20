from fabric.api import roles, parallel, sudo
from fabric.context_managers import cd

from ..const import ROLES_STATIC, ROLES_DJANGO


@roles(set(ROLES_STATIC + ROLES_DJANGO))
@parallel
def version_static(code_root, virtualenv_root):
    """
    Put refs on all static references to prevent stale browser cache hits when things change.
    This needs to be run on the WEB WORKER since the web worker governs the actual static
    reference.

    """

    cmd = 'resource_static'
    with cd(code_root):
        sudo(
            'rm -f tmp.sh resource_versions.py; {venv}/bin/python manage.py {cmd}'.format(
                venv=virtualenv_root, cmd=cmd
            ),
        )


@parallel
@roles(ROLES_STATIC)
def bower_install(code_root):
    with cd(code_root):
        sudo('bower prune --production --config.interactive=false')
        sudo('bower update --production --config.interactive=false')


@parallel
@roles(ROLES_DJANGO)
def npm_install(code_root):
    with cd(code_root):
        sudo('npm prune --production')
        sudo('npm install --production')
        sudo('npm update --production')


@parallel
@roles(ROLES_STATIC)
def collectstatic(code_root, virtualenv_root):
    """Collect static after a code update"""
    with cd(code_root):
        sudo('{}/bin/python manage.py collectstatic --noinput -v 0'.format(virtualenv_root))
        sudo('{}/bin/python manage.py fix_less_imports_collectstatic'.format(virtualenv_root))
        sudo('{}/bin/python manage.py compilejsi18n'.format(virtualenv_root))


@parallel
@roles(ROLES_STATIC)
def compress(code_root, virtualenv_root):
    """Run Django Compressor after a code update"""
    with cd(code_root):
        sudo('{}/bin/python manage.py compress --force -v 0'.format(virtualenv_root))
        sudo('{}/bin/python manage.py purge_compressed_files'.format(virtualenv_root))
