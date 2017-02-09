from fabric.api import env,local
import os

PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "django")

def opbeat_notice():
    local(
        """
            curl https://intake.opbeat.com/api/v1/organizations/cccbff44c5f34fb08f38bbf218f7c4c6/apps/597c88fc5b/releases/ \
            -H "Authorization: Bearer 690e25ea3c13af27ffa00a45ddc4202a5636cf2a" \
            -d rev=`git log -n 1 --pretty=format:%H` \
            -d branch=`git rev-parse --abbrev-ref HEAD` \
            -d status=completed
        """
    )

def deis_push():
    """
    push the container to gcloud and then to deis

    :return:
    """
    local("./manage.sh deis_push")

def mount_fonts():
    """
    mount the fonts from GCS for local development

    :return:
    """
    local("docker-compose exec django bash /build/util/gcs.sh")

def deis_reset():
    """
    reset the deis

    """
    local("deis destroy")
    local("./manage.sh deis_bs")
    local("./manage.sh deis_push")


def get_env(prod=''):
    """
    Usage `$ fab get_env:prod=True` : Get the environment from the server and buld the env directory. Prod gets prod.

    :return:
    """
    if prod:
        prod = '-e PROD=True '
    if not os.path.isfile(".env"):
        local("docker run -i -v ${PWD}:/app %sgit.brandly.com:5005/brandly/factory:distro" % prod)

    _container_env_path = os.path.join(PATH, "../compose/build/deploy/container_environment")
    if not os.path.isdir(_container_env_path):
        local("mkdir " + _container_env_path)

    with open(".env") as f:
        for line in f:
            if line.startswith('#') or '=' not in line:
                continue
            key,value = line.split('=',1)
            dockerfile = open(_container_env_path + "/" + key, "w")
            dockerfile.write(value)
            dockerfile.close()


def touch_pickle():
    """
    I wish we didn't have to do this. Touch the pickle. The shame will pass.

    :return:
    """
    local("touch brandly/non_baseline_font_names.p")


def clear_dead(images=False, force=False, containers=True):
    """
    Scuttle the bones of wrecked docker containers and images.

    Usage `$ fab clear_dead:<remote=False,containers=False,force=False)>`

    :param remote:
    :param containers:
    :return:
    """
    force=(" --force" if force else '')
    try:
        local("docker rm"+force+" $(docker ps - a - q)")
    except:
        print("no running images to clear")
    local("docker rmi"+force+" $(docker images | grep \"^<none>\" | awk \"{print $3}\")")


