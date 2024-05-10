#!/bin/zsh

git rm app/person/graph --force
git rm app/person/util --force

git rm app/resource/graph --force
git rm app/resource/util --force


git submodule add --force https://github.com/jm4rc05/pm-graph.git app/person/graph
git submodule add --force https://github.com/jm4rc05/pm-util.git app/person/util

git submodule add --force https://github.com/jm4rc05/pm-graph.git app/resource/graph
git submodule add --force https://github.com/jm4rc05/pm-util.git app/resource/util
