#!/usr/bin/env bash
# usage: sh ab_generate.sh <url> -c <concurrency> -n <requests>
URL=$1
shift
ab $URL "$@"
