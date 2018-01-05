
# Check pylint status
if [ -z ${MIN_SCORE} ]; then MIN_SCORE="9"; fi
PYLINT_SCORE=$( pylint --disable=$PYLINT_IGNORE -f parseable zero | tail -2 | grep -Eo '[0-9\.]+/10' | tail -1 | sed s/\\/10// )
PYLINT_PASS=$(echo $PYLINT_SCORE">="$MIN_SCORE | bc -l)

if [ "$TRAVIS_PULL_REQUEST_SHA" = "" ];  then SHA=$TRAVIS_COMMIT; else SHA=$TRAVIS_PULL_REQUEST_SHA; fi
if [ "$PYLINT_PASS" ]; then PYLINT_STATE="success" &&  echo "pylint passed with score "$PYLINT_SCORE" for sha "$SHA; else PYLINT_STATE="failure" &&  echo "pylint failed with score "$PYLINT_SCORE" for sha "$SHA; fi

curl -u $USERNAME:$GITHUB_TOKEN \
    -d '{"state": "'$PYLINT_STATE'", "target_url": "https://travis-ci.org/'$TRAVIS_REPO_SLUG'/builds/'$TRAVIS_BUILD_ID'", "description": "'$PYLINT_SCORE'/10", "context": "code-quality/pylint"}' \
    -XPOST https://api.github.com/repos/$TRAVIS_REPO_SLUG/statuses/$SHA \
    > /dev/null 2>&1

# Check pylintrc status
diff .pylintrc <(pylint --disable=$PYLINT_IGNORE -f parseable --generate-rcfile)
PYLINTRC_STATUS=$?
if [ $PYLINTRC_STATUS -ne 0 ]; then PYLINTRC_STATE="failure" && echo "pylintrc not updated or PYLINT_IGNORE not updated"; else PYLINTRC_STATE="success" &&  echo "pylintrc up-to-date"; fi
curl -u $USERNAME:$GITHUB_TOKEN \
    -d '{"state": "'$PYLINTRC_STATE'", "target_url": "https://travis-ci.org/'$TRAVIS_REPO_SLUG'/builds/'$TRAVIS_BUILD_ID'", "description": "", "context": "code-quality/pylintrc"}' \
    -XPOST https://api.github.com/repos/$TRAVIS_REPO_SLUG/statuses/$SHA \
    > /dev/null 2>&1

# Check mypy integration
mypy -p zero
MYPY_STATUS=$?
if [ $MYPY_STATUS -ne 0 ]; then MYPY_STATE="failure" && echo "mypy failed"; else MYPY_STATE="success" &&  echo "mypy passed"; fi

curl -u $USERNAME:$GITHUB_TOKEN \
    -d '{"state": "'$MYPY_STATE'", "target_url": "https://travis-ci.org/'$TRAVIS_REPO_SLUG'/builds/'$TRAVIS_BUILD_ID'", "description": "", "context": "code-quality/mypy"}' \
    -XPOST https://api.github.com/repos/$TRAVIS_REPO_SLUG/statuses/$SHA \
    > /dev/null 2>&1
