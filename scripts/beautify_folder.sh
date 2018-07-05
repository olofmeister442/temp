cd ..
cd engine
pwd
rm views.py
cp views_post.py views.py

cd static
cd engine
cd js
pwd
rm init.js
cp init_post.js init.js
rm init1.js
cp init1_post.js init1.js

cd ..
cd ..
cd ..
cd ..
pwd

python manage.py makemigrations

cd easychat
pwd
rm settings.py
cp settings_debug_false.py settings.py

cd ..

rm -rf .git
find . -type f -name '*.pyc' -delete
rm EasyChatLog*
rm db.sqlite3
rm engine/migrations/00*
rm easychat/migrations/00*
rm -rf static
