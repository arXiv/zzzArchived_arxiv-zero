# arxiv/flask base docker file

FROM centos:centos7

RUN yum -y update && yum -y install epel-release \
&& yum -y install https://centos7.iuscommunity.org/ius-release.rpm \  
&& echo $'#!/bin/bash\n\
PKGS_TO_INSTALL=$(cat <<-END\n\
  ca-certificates\n\
  wget\n\
  gcc\n\
  gcc-c++ \n\
  python36u\n\
  python36u-devel\n\
  git\n\
END\n\
)\n\
for pkg in ${PKGS_TO_INSTALL}; do\n\
  # Stop executing if at least one package is not available:\n\
  yum info ${pkg} || ( echo "yum could not find package ${pkg}"; exit 1 )\n\
done\n\
yum -y install ${PKGS_TO_INSTALL}\n' >> /tmp/safe_yum.sh \
&& /bin/bash /tmp/safe_yum.sh \
&& yum clean all

RUN wget https://bootstrap.pypa.io/get-pip.py \
  && python3.6 get-pip.py

CMD /bin/bash

