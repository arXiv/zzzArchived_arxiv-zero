#!/bin/bash
set -e # exit on error
set -x # show each command

REPO=arxiv/arxiv-zero
SRCDOCS=`pwd`/docs/build/html
echo $SRCDOCS

cd `pwd`/docs
make html SPHINXBUILD=$(pipenv --venv)/bin/sphinx-build

cd $SRCDOCS
MSG="Adding gh-pages docs for `git log -1 --pretty=short --abbrev-commit`"

TMPREPO=/tmp/docs/$REPO
rm -rf $TMPREPO
mkdir -p -m 0755 $TMPREPO
echo $MSG

git clone https://$USERNAME:$GITHUB_TOKEN@github.com/$REPO.git $TMPREPO
cd $TMPREPO
git checkout gh-pages  ###gh-pages has previously one off been set to be nothing but html
cp -r $SRCDOCS/* $TMPREPO
git add -A
git commit -m "$MSG"
git push origin gh-pages
