D=$1
find mviznARMG/*/weights mviznARMG/*/sample|rsync -av --files-from=- ./ $D
