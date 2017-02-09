#!/bin/bash
APT_CONTAINER=apt-cacher-ng

CONTAINER_NAME=$(cat ./compose/var/container_name)
VERSION=$(cat ./compose/var/version)
DOMAIN=$(cat ./compose/var/domain)

CONTAINER=$CONTAINER_NAME:$VERSION
APT_PROXY_PORT=3142

IFS='rev' read -ra VER <<< "$VERSION"
for i in "${VER[@]}"; do
    REV=$i
done
VER=${VER[1]}
NEXT_REVISION=v${VER[1]}rev$((REV+1))
NEXT_VERSION=v0$(echo $VER+0.01 | bc)rev1

if [ "$2" = "sudo" ] || [ "$3" = "sudo" ] || [ "$4" = "sudo" ]; then
    SUDO=1
fi

echo -e "\033[1;33m
    ######################################################################
    #                \033[1;31mTwitterbot \033[0;37mUnified Container Management                \033[1;33m#
    ######################################################################\033[0m
    "

RUNNING=$(docker inspect --format="{{ .State.Running }}" "$APT_CONTAINER" 2> /dev/null)
NETWORK=$(docker inspect --format="{{ .NetworkSettings.IPAddress }}" apt-cacher-ng)
STARTED=$(docker inspect --format="{{ .State.StartedAt }}" "$APT_CONTAINER")

CONNECTION_STRING="http://$NETWORK:$APT_PROXY_PORT"

if ! [ "$1" ]; then
    echo -e "\033[1;36m
        $ ./manage.sh build <bump> <collectstatic> <sudo>           [Build the container. Optional bump revision and collectstatic. Sudo if something complains.]
        $ ./manage.sh bump_version                                  [Bump the version number for distrobution]
        $ ./manage.sh deis_<push/bs>                                [Push to Deis and Bootstrap Deis]
        $ ./manage.sh apt                                           [Start Aptitude Cache]
    \033[0m"
else
    echo -e "
    \033[1;31mAPT CACHE CONNECTION STRING IS $CONNECTION_STRING\033[0m
    "
fi

if [ "$RUNNING" = "true" ]; then
    echo -e "\033[1;37m
    OK - \033[1;34m$APT_CONTAINER\033[0;37m is running. IP: \033[1;34m$NETWORK\033[0;37m, StartedAt: \033[1;34m$STARTED\033[0m
    \033[1;37mView apt cache control panel: \033[1;34mhttp://localhost:3142/acng-report.html\033[0m
    "
else
    echo -e "
    \033[1;31mapt-catcher-ng is not running! This will make build times significantly longer.\033[0m
    "
fi

echo -e "\033[1;37m"

if [ "$1" == "build" ]; then
    echo -e "
    Building $CONTAINER ...
    \033[0m
    "
    COLLECT_STATIC='false'
    if [ "$2" = "collectstatic" ] || [ "$3" = "collectstatic" ]; then
        echo -e "\033[1;36m \nBuilding with collectstatic \033[0m \n"
        COLLECT_STATIC='true'
    fi

    if [ "$2" = "bump" ]; then
        echo -e "\033[1;36m \nIncrementing revision from $VERSION to $NEXT_REVISION.\033[0m \n"
        sed -i -e "s/$VERSION/$NEXT_REVISION/" docker-compose.yml
        sed -i -e "s/$VERSION/$NEXT_REVISION/" ./compose/var/version
        if [ -d "./compose/var/version-e" ]; then
          rm ./compose/var/version-e docker-compose.yml-e
        fi
        docker build -t $CONTAINER_NAME:$NEXT_REVISION --build-arg CONNECTION_STRING="$CONNECTION_STRING" --build-arg COLLECT_STATIC=$COLLECT_STATIC .
    fi
    if ! [ "$2" = "bump" ]; then
        docker build -t $CONTAINER --build-arg CONNECTION_STRING="$CONNECTION_STRING" --build-arg COLLECT_STATIC=$COLLECT_STATIC .
    fi
fi

if [ "$1" == "bump_version" ]; then
    echo -e "\033[1;36m \nIncrementing version from $VERSION to $NEXT_VERSION.\033[0m \n"
    sed -i -e "s/$VERSION/$NEXT_VERSION/" docker-compose.yml
    sed -i -e "s/$VERSION/$NEXT_VERSION/" ./compose/var/version
    if [ -d "./compose/var/version-e" ]; then
        rm ./compose/var/version-e docker-compose.yml-e
    fi
fi

if [ "$1" = "deis_push" ]; then
    echo -e "
    Pushing $CONTAINER to gcloud then deis...
    \033[0m"

    if [ "$SUDO" ]; then
        sudo gcloud docker -- push $CONTAINER
    fi

    if ! [ "$SUDO" ]; then
        gcloud docker -- push $CONTAINER
    fi
    deis pull $CONTAINER
fi

if [ "$1" = "deis_bs" ]; then
    echo -e "
    Bootstraping Deis
    \033[0m"
    deis create
    deis domains:add $DOMAIN
    deis config:push
    deis config:set DEBUG=False
    deis config:set FONT_DEBUG=False
    deis registry:set username=_json_key password="$(cat gcloud-auth.json | jq -c .)"
fi

if [ "$1" = "apt" ]; then
    echo -e "
    Launching apt cache ...
    \033[0m"
    docker run --name "$APT_CONTAINER" -d --restart=always \
        --publish "$APT_PROXY_PORT":"$APT_PROXY_PORT" \
        --volume "${PWD}"/.cache:/var/cache/apt-cacher-ng \
        sameersbn/apt-cacher-ng:latest
fi

if [ "$1" = "split_env" ]; then
    echo -e "
    split out .env for container environment ...
    \033[0m"
    if [ ! -d "./compose/build/deploy/container_environment" ]; then
        mkdir ./compose/build/deploy/container_environment
    fi

    input=".env"
    while IFS= read -r var
    do
        OIFS="$IFS"
        IFS='='
        read -a envvar <<< "${var}"
        IFS="$OIFS"
        if ! [[ $envvar[0] =~ ^# ]]; then
            echo ${envvar[1]} > ./compose/build/deploy/container_environment/${envvar[0]};
        fi
    done < "$input"
fi

echo -e "\033[0m"

