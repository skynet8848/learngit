Git is a distributed version control system. 
Git is free software under the GPL.

$mkdir learngit
$cd learngit
$pwd
/c/Users/ryanliu/learngit
$git init

$git add readme.txt
$git commit -m "wrote a readme file"

$git status
$git diff readme.txt

$git log readme.txt
$git log --pretty=oneline

$git reset --hard HEAD^
$git reset --hard 9445090
$git reflog

$git push origin master
SSH:
$git clone git@github.com:skynet8848/gitskills.git
HTTPS:
$git clone https://github.com/skynet8848/gitskills.git
