FROM phusion/passenger-full:0.9.20

ARG CONNECTION_STRING=172.17.0.2
ARG COLLECT_STATIC=

ENV HOME /root
ENV PASSENGER_APP_ENV=prod

# CMD ["/sbin/my_init"]

ADD ./compose/build /build
ADD ./django /home/django

RUN bash /build/scripts/run_setup.sh ${CONNECTION_STRING} ${COLLECT_STATIC}

VOLUME /home
WORKDIR /home/django

CMD /usr/bin/python /sbin/my_init