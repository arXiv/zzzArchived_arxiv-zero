SCORE=$( pylint --disable=$PYLINT_IGNORE -f parseable zero | tail -2 | grep -Eo '[0-9\.]+/10' | tail -1 | sed s/\\/10// )

if [ "$TRAVIS_PULL_REQUEST_SHA" = "" ]    # This is not a pull request.
then
    SHA=$TRAVIS_COMMIT
else
    SHA=$TRAVIS_PULL_REQUEST_SHA
fi

PASS=$(echo $SCORE">="$MIN_SCORE | bc -l)
if [ $PASS ]

then
    STATE="success"
    echo "pylint passed with score "$SCORE
else
    STATE="failure"
    echo "pylint failed with score "$SCORE
fi

curl -u $USERNAME:$GITHUB_TOKEN \
    -d '{"state": "'$STATE'", "target_url": "https://travis-ci.org/'$TRAVIS_REPO_SLUG'/builds/'$TRAVIS_BUILD_ID'", "description": "", "context": "code-quality/pylint"}' \
    -XPOST https://api.github.com/repos/$TRAVIS_REPO_SLUG/statuses/$SHA
