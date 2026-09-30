@echo off

set CSV=%~dp0resultados2.csv

pushd p2p
call run.bat %CSV%
popd
