python3 -m pip install -r requirements.txt
python3 local_main.py  

python3 -m pip install -r requirements.txt   



Build scripts: 

sed -i '' 's/version="[0-9]*\.[0-9]*\.[0-9]*"/version="'$(awk -F'"' '/version=/{print $2}' setu.py | awk -F. '{$2++;print $1"."$2"."$3}')'"/' setup.py

git add . && git commit -m "feat: add wu xi pillar calculation" && git push
