FROM alpine:3.9.4

RUN apk update && apk add -u gcc g++ bash curl file perl musl-dev make git python3
RUN python3 -m pip install autopep8 hacking pytest
ADD build_mpi.sh /build_mpi.sh
ADD md5checksum.txt /md5checksum.txt
RUN bash /build_mpi.sh
