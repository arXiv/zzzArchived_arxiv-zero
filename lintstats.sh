PYLINT_SCORE=$( pylint --disable=$PYLINT_IGNORE -f parseable zero | tail -2 | grep -Eo '[0-9\.]+/10' | tail -1 | sed s/\\/10// )
PYLINT_PASS=$(echo $SCORE">="$MIN_SCORE | bc -l)

if [ "$TRAVIS_PULL_REQUEST_SHA" = "" ]    # This is not a pull request.
then
    SHA=$TRAVIS_COMMIT
else
    SHA=$TRAVIS_PULL_REQUEST_SHA
fi

if [ $PYLINT_PASS ]
then
    PYLINT_STATE="success"
    echo "pylint passed with score "$PYLINT_SCORE" for sha "$SHA
else
    PYLINT_STATE="failure"
    echo "pylint failed with score "$PYLINT_SCORE" for sha "$SHA
fi

curl -u $USERNAME:$GITHUB_TOKEN \
    -d '{"state": "'$PYLINT_STATE'", "target_url": "https://travis-ci.org/'$TRAVIS_REPO_SLUG'/builds/'$TRAVIS_BUILD_ID'", "description": "'$PYLINT_SCORE'/10", "context": "code-quality/pylint"}' \
    -XPOST https://api.github.com/repos/$TRAVIS_REPO_SLUG/statuses/$SHA \
    > /dev/null 2>&1


mypy -p zero --ignore-missing-imports
if [ "$?" ]
then
    MYPY_STATE="success"
    echo "mypy passed"
else
    MYPY_STATE="failure"
    echo "mypy failed"
fi

curl -u $USERNAME:$GITHUB_TOKEN \
    -d '{"state": "'$MYPY_STATE'", "target_url": "https://travis-ci.org/'$TRAVIS_REPO_SLUG'/builds/'$TRAVIS_BUILD_ID'", "description": "", "context": "code-quality/mypy"}' \
    -XPOST https://api.github.com/repos/$TRAVIS_REPO_SLUG/statuses/$SHA \
    > /dev/null 2>&1
