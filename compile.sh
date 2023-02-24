#!/bin/bash

cd ../..
flutter clean && flutter build web --release --base-href=/web/

rm -r flask/tac2/templates

cp -R build/web flask/tac2/templates/

cp flask/favicon.* flask/tac2/templates/

cd flask/tac2/

git add .
git commit -m $1

git push 
